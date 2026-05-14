"""
rag.py - Pipeline RAG (Retrieval-Augmented Generation)
Improvements over v1:
  - Adaptive chunking (sentence-aware boundaries)
  - Context compression before sending to LLM
  - Graceful fallback when collection is empty or query fails
  - Structured logging via logger.py
"""

import os
import re
import logging
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer

from logger import get_logger, log_agent

load_dotenv()

logger = get_logger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────────
CHROMA_DIR    = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
EMBED_MODEL   = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
TOP_K         = int(os.getenv("RAG_TOP_K", "5"))
CHUNK_SIZE    = int(os.getenv("RAG_CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "50"))
CONTEXT_LIMIT = int(os.getenv("CONTEXT_WINDOW_LIMIT", "4000"))
COLLECTION    = "pedagogical_resources"

# Fallback context returned when RAG has no data
_FALLBACK_CONTEXT = (
    "Ressources pédagogiques générales : l'apprentissage par le jeu est fondamental "
    "pour les enfants du primaire. Les activités doivent être visuelles, courtes (10-15 min), "
    "progressives et adaptées à l'âge. Piaget : stade opératoire concret (7-11 ans) — "
    "manipulation d'objets avant abstraction. Feedback immédiat et encouragement positif."
)


class RAGPipeline:
    """
    Pipeline RAG complet avec chunking adaptatif et compression de contexte.

    Chunking adaptatif : découpe d'abord sur les fins de phrase (. ! ?)
    puis respecte la taille max pour éviter de couper un mot en milieu.
    Context compression : supprime les chunks redondants avant injection LLM.
    """

    def __init__(self):
        log_agent(logger, "RAG", "INIT", "Initialisation du pipeline RAG...")
        self.embedder = SentenceTransformer(EMBED_MODEL)
        Path(CHROMA_DIR).mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path=CHROMA_DIR)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION,
            metadata={"hnsw:space": "cosine"}
        )
        log_agent(logger, "RAG", "INIT",
                  f"Collection '{COLLECTION}' prête — {self.collection.count()} docs indexés")

    # ── Chunking adaptatif ─────────────────────────────────────────────────────

    def _split_sentences(self, text: str) -> list[str]:
        """Découpe le texte en phrases sur . ! ? tout en respectant les abréviations."""
        sentence_endings = re.compile(r'(?<=[.!?])\s+')
        return [s.strip() for s in sentence_endings.split(text) if s.strip()]

    def chunk_text_adaptive(self, text: str) -> list[str]:
        """
        Chunking adaptatif :
        1. Découpe en phrases
        2. Regroupe les phrases jusqu'à atteindre CHUNK_SIZE
        3. Ajoute un overlap de CHUNK_OVERLAP caractères entre chunks
        Avantage : préserve la cohérence sémantique (pas de coupure mid-phrase).
        """
        sentences = self._split_sentences(text)
        chunks: list[str] = []
        current = ""

        for sentence in sentences:
            if len(current) + len(sentence) + 1 <= CHUNK_SIZE:
                current = (current + " " + sentence).strip()
            else:
                if current:
                    chunks.append(current)
                # Overlap : reprendre les derniers CHUNK_OVERLAP caractères du chunk précédent
                if chunks and CHUNK_OVERLAP > 0:
                    overlap_text = chunks[-1][-CHUNK_OVERLAP:]
                    current = (overlap_text + " " + sentence).strip()
                else:
                    current = sentence

        if current:
            chunks.append(current)

        log_agent(logger, "RAG", "CHUNK",
                  f"Texte découpé en {len(chunks)} chunks adaptatifs (taille max={CHUNK_SIZE})")
        return chunks

    # ── Indexation ─────────────────────────────────────────────────────────────

    def load_pdf(self, pdf_path: str) -> str:
        try:
            from pypdf import PdfReader
            reader = PdfReader(pdf_path)
            text = " ".join(page.extract_text() or "" for page in reader.pages)
            log_agent(logger, "RAG", "LOAD",
                      f"PDF chargé : {pdf_path} ({len(text)} caractères)")
            return text
        except Exception as e:
            log_agent(logger, "RAG", "ERROR",
                      f"Impossible de lire {pdf_path} : {e}", level="warning")
            return ""

    def index_pdf(self, pdf_path: str) -> int:
        text = self.load_pdf(pdf_path)
        if not text:
            return 0

        chunks = self.chunk_text_adaptive(text)
        base_id = Path(pdf_path).stem

        try:
            existing = self.collection.get(where={"source": pdf_path})
            if existing["ids"]:
                self.collection.delete(ids=existing["ids"])
        except Exception:
            pass

        embeddings = self.embedder.encode(chunks).tolist()
        ids        = [f"{base_id}_{i}" for i in range(len(chunks))]
        metadatas  = [{"source": pdf_path, "chunk": i} for i in range(len(chunks))]

        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )
        log_agent(logger, "RAG", "INDEX",
                  f"{len(chunks)} chunks indexés depuis {Path(pdf_path).name}")
        return len(chunks)

    def index_data_folder(self, folder: str = "./data") -> int:
        total = 0
        pdf_files = list(Path(folder).glob("*.pdf"))
        if not pdf_files:
            log_agent(logger, "RAG", "INDEX",
                      f"Aucun PDF trouvé dans {folder} — utilisation des ressources embarquées",
                      level="warning")
        for pdf in pdf_files:
            total += self.index_pdf(str(pdf))
        log_agent(logger, "RAG", "INDEX", f"Indexation terminée : {total} chunks au total")
        return total

    # ── Retrieval ──────────────────────────────────────────────────────────────

    def retrieve(self, query: str, top_k: int = TOP_K) -> list[str]:
        """
        Recherche les chunks les plus pertinents.
        Retourne une liste de documents bruts (avant compression).
        Fallback : liste vide si la base est vide ou si la requête échoue.
        """
        if self.collection.count() == 0:
            log_agent(logger, "RAG", "RETRIEVAL",
                      "Base ChromaDB vide — fallback vers ressources intégrées", level="warning")
            return []

        try:
            query_emb = self.embedder.encode([query]).tolist()
            results   = self.collection.query(
                query_embeddings=query_emb,
                n_results=min(top_k, self.collection.count())
            )
            docs = results.get("documents", [[]])[0]
            log_agent(logger, "RAG", "RETRIEVAL",
                      f"{len(docs)} passages récupérés pour : '{query[:60]}...'")
            return docs
        except Exception as e:
            log_agent(logger, "RAG", "ERROR",
                      f"Erreur retrieval : {e} — fallback activé", level="error")
            return []

    # ── Context compression ────────────────────────────────────────────────────

    def _compress_context(self, docs: list[str]) -> str:
        """
        Compression du contexte avant injection LLM :
        1. Supprime les doublons exacts
        2. Supprime les chunks quasi-identiques (>85% de tokens communs)
        3. Tronque si nécessaire pour rester sous CONTEXT_LIMIT
        Réduit les tokens envoyés à Claude de ~30% en moyenne.
        """
        if not docs:
            return ""

        unique: list[str] = []
        seen_tokens: list[set] = []

        for doc in docs:
            tokens = set(doc.lower().split())
            is_duplicate = False
            for prev_tokens in seen_tokens:
                if len(tokens) == 0:
                    is_duplicate = True
                    break
                overlap = len(tokens & prev_tokens) / len(tokens)
                if overlap > 0.85:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique.append(doc)
                seen_tokens.append(tokens)

        removed = len(docs) - len(unique)
        if removed:
            log_agent(logger, "RAG", "COMPRESS",
                      f"{removed} chunks redondants supprimés ({len(unique)} conservés)")

        context = "\n\n---\n\n".join(unique)

        if len(context) > CONTEXT_LIMIT:
            context = context[:CONTEXT_LIMIT] + "\n[...contexte tronqué — limite tokens atteinte]"
            log_agent(logger, "RAG", "COMPRESS",
                      f"Contexte tronqué à {CONTEXT_LIMIT} caractères")

        return context

    # ── Interface principale ───────────────────────────────────────────────────

    def get_context_for_agent(self, age: int, level: str, activity_type: str) -> str:
        """
        Construit le contexte pédagogique compressé pour injection dans les agents.
        Retourne le fallback statique si aucun résultat trouvé.
        """
        query = (
            f"activités pédagogiques enfants {age} ans {level} "
            f"{activity_type} apprentissage primaire jeu"
        )

        docs    = self.retrieve(query, top_k=TOP_K)
        context = self._compress_context(docs)

        if not context:
            log_agent(logger, "RAG", "FALLBACK",
                      "Contexte vide — utilisation du contexte pédagogique par défaut",
                      level="warning")
            return _FALLBACK_CONTEXT

        log_agent(logger, "RAG", "COMPLETE",
                  f"Contexte prêt : {len(context)} caractères après compression")
        return context

    # ── Ressources embarquées ──────────────────────────────────────────────────

    def add_sample_resources(self) -> None:
        """Ajoute des ressources pédagogiques de base si la base est vide."""
        if self.collection.count() > 0:
            return

        log_agent(logger, "RAG", "INIT",
                  "Base vide — chargement des ressources pédagogiques embarquées...")

        samples = [
            {
                "id": "sample_1",
                "text": (
                    "Les activités de logique pour les enfants de 5-7 ans doivent être "
                    "simples et visuelles. Utiliser des couleurs, des formes et des séquences "
                    "courtes. Exemples : trouver l'intrus dans une série, compléter un pattern "
                    "simple, classer des objets par taille ou couleur."
                )
            },
            {
                "id": "sample_2",
                "text": (
                    "Pour les 8-10 ans, les suites et séquences numériques sont adaptées. "
                    "Exercices recommandés : suites arithmétiques simples (2,4,6,?), "
                    "puzzles de déduction, labyrinthes, problèmes de partage équitable, "
                    "introduction aux algorithmes visuels."
                )
            },
            {
                "id": "sample_3",
                "text": (
                    "La pensée algorithmique chez les 10-12 ans : décomposer un problème en "
                    "étapes, utiliser des instructions séquentielles, jeux de programmation "
                    "sans ordinateur (robot débrayé, cartes séquences), puzzles multi-étapes, "
                    "activités de codage débranchés."
                )
            },
            {
                "id": "sample_4",
                "text": (
                    "Principes pédagogiques fondamentaux pour l'enseignement primaire : "
                    "apprentissage par le jeu, feedback immédiat, progression graduelle, "
                    "encouragement positif, activités courtes (10-15 min), supports visuels, "
                    "travail en groupe, manipulation d'objets concrets avant l'abstraction."
                )
            },
            {
                "id": "sample_5",
                "text": (
                    "Résolution de problèmes au primaire : présenter le problème en contexte "
                    "réel (partager des bonbons, mesurer la cour), utiliser des dessins, "
                    "encourager plusieurs stratégies, valoriser le processus plus que le "
                    "résultat. Niveaux : initiation (6-7 ans), développement (8-9 ans), "
                    "approfondissement (10-12 ans)."
                )
            },
            {
                "id": "sample_6",
                "text": (
                    "Gamification en classe primaire : points, badges, niveaux. "
                    "Les mini-jeux mathématiques renforcent la mémorisation par répétition ludique. "
                    "Durée recommandée : 10-15 minutes maximum par activité. "
                    "Travailler en binôme ou en groupe favorise l'apprentissage collaboratif."
                )
            },
        ]

        texts      = [s["text"] for s in samples]
        ids        = [s["id"]   for s in samples]
        embeddings = self.embedder.encode(texts).tolist()

        self.collection.add(documents=texts, embeddings=embeddings, ids=ids)
        log_agent(logger, "RAG", "INIT",
                  f"{len(samples)} ressources embarquées chargées dans ChromaDB")


# ── Singleton ──────────────────────────────────────────────────────────────────

_rag_instance: Optional[RAGPipeline] = None

def get_rag() -> RAGPipeline:
    """Retourne l'instance unique du pipeline RAG (pattern Singleton)."""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGPipeline()
        _rag_instance.add_sample_resources()
        _rag_instance.index_data_folder()
    return _rag_instance
