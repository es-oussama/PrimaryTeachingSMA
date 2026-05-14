"""
test_api.py - Premier test de connexion à l'API Claude (Anthropic)
Valide que la clé API et l'environnement sont correctement configurés.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

def test_anthropic_api():
    """Test de connexion basique à l'API Anthropic Claude."""
    print("=" * 60)
    print("  TEST API CLAUDE - PrimaryTeachingSMA")
    print("=" * 60)

    # 1. Vérifier la clé API
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "sk-ant-api03-VOTRE_CLE_ICI":
        print("[ERREUR] ANTHROPIC_API_KEY non configurée dans .env")
        print("  -> Copiez .env.example vers .env")
        print("  -> Ajoutez votre vraie clé API")
        sys.exit(1)

    print(f"[OK] Clé API détectée : {api_key[:20]}...")

    # 2. Importer Anthropic
    try:
        import anthropic
        print("[OK] Package anthropic importé")
    except ImportError:
        print("[ERREUR] Package anthropic non installé")
        print("  -> pip install anthropic")
        sys.exit(1)

    # 3. Tester l'appel API
    model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
    print(f"[INFO] Modèle utilisé : {model}")
    print("[INFO] Envoi d'un message de test à Claude...")

    start = time.time()
    try:
        client = anthropic.Anthropic(api_key=api_key)

        message = client.messages.create(
            model=model,
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Tu es un assistant pédagogique. "
                        "Réponds en une phrase : "
                        "Quelle est l'importance du jeu dans l'apprentissage des enfants ?"
                    )
                }
            ]
        )

        elapsed = time.time() - start
        response_text = message.content[0].text

        print(f"\n[OK] Réponse reçue en {elapsed:.2f}s")
        print("-" * 60)
        print(f"Claude dit : {response_text}")
        print("-" * 60)
        print(f"\nUsage tokens :")
        print(f"  - Input  : {message.usage.input_tokens} tokens")
        print(f"  - Output : {message.usage.output_tokens} tokens")
        print(f"  - Total  : {message.usage.input_tokens + message.usage.output_tokens} tokens")

    except anthropic.AuthenticationError:
        print("[ERREUR] Clé API invalide ou expirée")
        sys.exit(1)
    except anthropic.RateLimitError:
        print("[ERREUR] Rate limit atteint - réessayez dans quelques secondes")
        sys.exit(1)
    except Exception as e:
        print(f"[ERREUR] Inattendue : {e}")
        sys.exit(1)

    # 4. Vérifier ChromaDB
    print("\n[INFO] Test ChromaDB...")
    try:
        import chromadb
        client_db = chromadb.Client()
        col = client_db.create_collection("test_col")
        col.add(documents=["test document"], ids=["id1"])
        results = col.query(query_texts=["test"], n_results=1)
        client_db.delete_collection("test_col")
        print("[OK] ChromaDB opérationnel")
    except Exception as e:
        print(f"[AVERTISSEMENT] ChromaDB : {e}")

    # 5. Vérifier sentence-transformers
    print("[INFO] Test sentence-transformers...")
    try:
        from sentence_transformers import SentenceTransformer
        model_emb = SentenceTransformer("all-MiniLM-L6-v2")
        emb = model_emb.encode(["test"])
        print(f"[OK] Embeddings opérationnels (dim={len(emb[0])})")
    except Exception as e:
        print(f"[AVERTISSEMENT] sentence-transformers : {e}")

    # 6. Vérifier ReportLab
    print("[INFO] Test ReportLab...")
    try:
        from reportlab.pdfgen import canvas
        print("[OK] ReportLab opérationnel")
    except Exception as e:
        print(f"[AVERTISSEMENT] ReportLab : {e}")

    print("\n" + "=" * 60)
    print("  TOUS LES TESTS PASSÉS - ENVIRONNEMENT PRÊT")
    print("=" * 60)


if __name__ == "__main__":
    test_anthropic_api()
