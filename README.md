# Assistant d'Aide à l'Enseignement Primaire
## Système Multi-Agents (SMA) — Projet Universitaire

---

## Description

Système intelligent basé sur **CrewAI** qui aide les instituteurs du primaire à générer automatiquement des **activités pédagogiques ludiques** adaptées à l'âge des enfants.

L'utilisateur renseigne l'âge de l'enfant, le niveau scolaire, le type d'activité et un objectif pédagogique. Le système orchestre 3 agents IA en séquence, enrichis par un pipeline RAG, et produit une fiche PDF prête à imprimer.

---

## Architecture du Système

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTERFACE UTILISATEUR                         │
│                   Streamlit (app.py)                             │
│  Formulaire : âge, niveau, type activité, objectif pédagogique  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Paramètres
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   WORKFLOW ORCHESTRATOR                          │
│                   (workflow.py)                                  │
│  Façade : coordonne RAG → Agents → PDF → Trace                  │
└───────┬─────────────────────┬──────────────────────────┬────────┘
        │                     │                          │
        ▼                     ▼                          ▼
┌───────────────┐   ┌────────────────────┐   ┌──────────────────┐
│  RAG PIPELINE │   │   CREW AI AGENTS   │   │  PDF GENERATOR   │
│   (rag.py)    │   │   (agents.py)      │   │(pdf_generator.py)│
│               │   │                    │   │                  │
│ ChromaDB      │   │ [Agent 1]          │   │ ReportLab        │
│ Embeddings    │──▶│ Analyse Péda.      │   │ Fiche A4 colorée │
│ Chunking      │   │      ↓             │──▶│ Téléchargeable   │
│ adaptatif     │   │ [Agent 2]          │   │                  │
│ Compression   │──▶│ Génér. Activités   │   └──────────────────┘
│ contexte      │   │      ↓             │
└───────────────┘   │ [Agent 3]          │
                    │ Struct. PDF        │
                    └────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LOGGING & TRACE                               │
│  outputs/agents.log  |  Learning_Log/execution_trace.txt        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Les 3 Agents CrewAI

| Agent | Rôle | Input | Output |
|-------|------|-------|--------|
| **Agent 1 — Analyse Pédagogique** | Expert en sciences de l'éducation (15 ans d'exp.) | Âge, niveau, objectif + contexte RAG | Profil cognitif en 5 sections |
| **Agent 2 — Génération Activités** | Créateur d'activités ludiques Montessori/Waldorf | Analyse Agent 1 + contexte RAG | 3 activités complètes avec instructions |
| **Agent 3 — Structuration PDF** | Rédacteur de fiches pédagogiques | Outputs des agents 1 et 2 | Fiche structurée prête à imprimer |

Les agents s'exécutent en **séquence** (`Process.sequential`) : chaque agent reçoit le contexte produit par le précédent.

---

## Pipeline RAG

Le **Retrieval-Augmented Generation** ancre les agents dans des ressources pédagogiques validées pour limiter les hallucinations.

```
PDF pédagogiques (data/)
        │
        ▼ load_pdf()
   Texte brut
        │
        ▼ chunk_text_adaptive()   ← Découpe sur frontières de phrases
   Chunks sémantiques (≤500 chars, overlap 50)
        │
        ▼ SentenceTransformer (all-MiniLM-L6-v2)
   Vecteurs d'embeddings (384 dimensions)
        │
        ▼ ChromaDB (cosine similarity)
   Base vectorielle persistante
        │
        ▼ retrieve(query, top_k=5)
   Top-5 chunks pertinents
        │
        ▼ _compress_context()     ← Supprime doublons (>85% tokens communs)
   Contexte compressé (<4000 chars)
        │
        ▼ Injection dans les prompts des agents
```

**Fallback** : si la base est vide ou si la requête échoue, un contexte pédagogique statique de référence est automatiquement utilisé.

---

## Système de Logging Structuré

Chaque action produit des logs au format :
```
[2026-05-14 10:32:05][AGENT-1][ANALYSIS] Lancement analyse — 8 ans, CE2
[2026-05-14 10:32:12][AGENT-2][GENERATION] 3 activités générées — 1842 caractères
[2026-05-14 10:32:18][AGENT-3][COMPLETE] Contenu PDF : 2104 caractères
[2026-05-14 10:32:21][PDF][GENERATION] Fichier PDF créé : ./outputs/fiche_pedagogique_...pdf
```

- **`outputs/agents.log`** — log machine de toutes les exécutions
- **`Learning_Log/execution_trace.txt`** — trace humaine lisible de chaque run

---

## Stack Technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Framework Agents | CrewAI | ≥0.63.0 |
| LLM | Claude Sonnet 4.6 (Anthropic) | claude-sonnet-4-6 |
| Orchestration LLM | LangChain-Anthropic | ≥0.1.15 |
| RAG — Vector Store | ChromaDB | ≥0.5.0 |
| RAG — Embeddings | sentence-transformers/all-MiniLM-L6-v2 | ≥3.0.0 |
| Interface | Streamlit | ≥1.35.0 |
| PDF | ReportLab | ≥4.2.0 |
| Orchestration externe | n8n (optionnel) | ≥1.0 |
| Environnement | Python | 3.11+ |

---

## Installation

### Prérequis

- Python 3.11 ou supérieur
- Clé API Anthropic ([console.anthropic.com](https://console.anthropic.com))

### Étapes

```powershell
# 1. Aller dans le dossier Source
cd d:\PrimaryTeachingSMA\Source

# 2. Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Si bloqué par la politique d'exécution :
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
copy .env.example .env
# Ouvrir .env et renseigner ANTHROPIC_API_KEY et CLAUDE_MODEL

# 5. Tester l'environnement
python test_api.py

# 6. Lancer l'application
streamlit run app.py
```

---

## Configuration `.env`

```env
# Obligatoire
ANTHROPIC_API_KEY=sk-ant-api03-...
CLAUDE_MODEL=claude-sonnet-4-6

# RAG (valeurs par défaut recommandées)
CHROMA_PERSIST_DIR=./data/chroma_db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
RAG_TOP_K=5
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50
CONTEXT_WINDOW_LIMIT=4000

# Tokens (anti-surconsommation)
MAX_TOKENS_PER_AGENT=1500

# Sorties
OUTPUT_DIR=./outputs
LOG_FILE=./outputs/agents.log
TRACE_FILE=../Learning_Log/execution_trace.txt

# n8n (optionnel)
N8N_WEBHOOK_URL=http://localhost:5678/webhook/primary-teaching
```

---

## Utilisation

### Via l'interface Streamlit

1. Lancer : `streamlit run app.py` → s'ouvre sur `http://localhost:8501`
2. Remplir le formulaire : âge, niveau, type d'activité, objectif
3. Cliquer sur **"Générer les Activités Pédagogiques"**
4. Suivre les logs en temps réel dans l'onglet "Logs Agents"
5. Télécharger le PDF dans l'onglet "PDF"

### Via l'API n8n (optionnel)

Importer `Source/n8n_workflow.json` dans n8n, puis envoyer :

```bash
curl -X POST http://localhost:5678/webhook/primary-teaching \
  -H "Content-Type: application/json" \
  -d '{
    "age": 8,
    "level": "CE2",
    "activity_type": "Logique & Raisonnement",
    "objective": "Développer la pensée algorithmique"
  }'
```

### Via la ligne de commande

```powershell
cd d:\PrimaryTeachingSMA\Source
.\venv\Scripts\Activate.ps1
python workflow.py
```

---

## Structure du Projet

```
PrimaryTeachingSMA/
│
├── README.md                      ← Ce fichier
│
├── Source/                        ← Code source principal
│   ├── app.py                     ← Interface Streamlit
│   ├── agents.py                  ← 3 agents CrewAI + fallbacks
│   ├── rag.py                     ← Pipeline RAG (chunking adaptatif)
│   ├── pdf_generator.py           ← Génération PDF ReportLab
│   ├── workflow.py                ← Orchestration + trace d'exécution
│   ├── logger.py                  ← Système de logging structuré
│   ├── test_api.py                ← Tests de l'environnement
│   ├── n8n_workflow.json          ← Export workflow n8n
│   ├── requirements.txt
│   ├── .env.example
│   ├── data/                      ← PDFs pédagogiques source (RAG)
│   └── outputs/                   ← PDFs générés + logs + résumés JSON
│
├── Rapport/
│   └── token_optimization.md      ← Rapport optimisation coûts & tokens
│
├── Learning_Log/
│   └── execution_trace.txt        ← Trace d'exécution générée automatiquement
│
└── Video/
    └── demo_script.md             ← Script de démonstration
```

---

## Gestion des Erreurs

Le système intègre des **fallbacks à 3 niveaux** :

| Niveau | Problème | Comportement |
|--------|----------|--------------|
| RAG | Base vide ou requête échouée | Contexte pédagogique statique intégré |
| API Claude | Quota, réseau, authentification | Outputs pré-définis de qualité renvoyés |
| PDF | Erreur ReportLab | Chemin vide retourné, erreur loguée |

Aucune exception non gérée ne bloque l'interface Streamlit — le système dégrade gracieusement.

---

## Auteur

Projet universitaire — Système Multi-Agents (SMA)
Technologies : CrewAI + Claude API (Anthropic) + ChromaDB + Streamlit + ReportLab
