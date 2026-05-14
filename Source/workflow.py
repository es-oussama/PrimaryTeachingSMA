"""
workflow.py - Orchestration complète du pipeline PrimaryTeachingSMA.
Point d'entrée principal : RAG → Agents → PDF → Trace → Logs.

Améliorations v2 :
  - Structured logging via logger.py
  - Execution trace écrite dans Learning_Log/execution_trace.txt
  - Gestion d'erreurs avec fallback à chaque étape
  - Résumé JSON d'audit par run
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from logger import get_logger, log_agent, ExecutionTrace

logger = get_logger("workflow")


class TeachingWorkflow:
    """
    Workflow complet :
    1. Initialisation RAG
    2. Retrieval du contexte pédagogique + compression
    3. Lancement du Crew multi-agents (avec fallbacks)
    4. Génération du PDF
    5. Écriture de la trace d'exécution
    6. Sauvegarde du résumé JSON

    Design : Facade — simplifie l'interface pour Streamlit et n8n.
    """

    def __init__(self):
        log_agent(logger, "WORKFLOW", "INIT", "Démarrage du workflow PrimaryTeachingSMA")
        self._rag   = None
        self._crew  = None
        self._trace = ExecutionTrace()

    def _init_rag(self) -> None:
        if self._rag is None:
            log_agent(logger, "WORKFLOW", "INIT", "Initialisation lazy du pipeline RAG...")
            from rag import get_rag
            self._rag = get_rag()

    def _init_crew(self) -> None:
        if self._crew is None:
            log_agent(logger, "WORKFLOW", "INIT", "Initialisation lazy du Crew...")
            from agents import TeachingCrew
            self._crew = TeachingCrew()

    def run(
        self,
        age: int,
        level: str,
        activity_type: str,
        objective: str,
        output_dir: str = "./outputs"
    ) -> dict:
        """
        Lance le workflow complet.

        Returns:
            dict : analysis, activities, pdf_path, pdf_content,
                   duration_sec, log_path, rag_chars, fallback_used
        """
        start_time = datetime.now()
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        params = {
            "age":           f"{age} ans",
            "level":         level,
            "activity_type": activity_type,
            "objective":     objective[:80] + ("..." if len(objective) > 80 else ""),
            "output_dir":    output_dir,
        }

        log_agent(logger, "WORKFLOW", "START",
                  f"Paramètres : age={age}, level={level}, type={activity_type}")
        self._trace.start(params)

        # ── Étape 1 : RAG Retrieval ────────────────────────────────────────────
        log_agent(logger, "WORKFLOW", "STEP-1", "Étape 1/3 — Retrieval RAG + compression")

        try:
            self._init_rag()
            rag_context = self._rag.get_context_for_agent(age, level, activity_type)
            rag_chars   = len(rag_context)
            log_agent(logger, "WORKFLOW", "STEP-1",
                      f"Contexte RAG prêt : {rag_chars} caractères")
            self._trace.record("RAG", "RETRIEVAL",
                               f"Contexte récupéré et compressé : {rag_chars} caractères")
        except Exception as e:
            log_agent(logger, "WORKFLOW", "ERROR",
                      f"RAG échoué : {e} — contexte vide utilisé", level="error")
            rag_context = ""
            rag_chars   = 0
            self._trace.record("RAG", "ERROR", f"RAG indisponible : {e} — fallback vide")

        # ── Étape 2 : Agents CrewAI ───────────────────────────────────────────
        log_agent(logger, "WORKFLOW", "STEP-2", "Étape 2/3 — Lancement des 3 agents CrewAI")
        self._trace.record("WORKFLOW", "STEP-2",
                           "Lancement séquentiel : Agent-1 → Agent-2 → Agent-3")

        try:
            self._init_crew()
            agent_outputs = self._crew.run(
                age=age,
                level=level,
                activity_type=activity_type,
                objective=objective,
                rag_context=rag_context
            )
        except Exception as e:
            log_agent(logger, "WORKFLOW", "ERROR",
                      f"Crew échoué : {e} — fallback complet activé", level="error")
            self._trace.record("CREW", "ERROR", f"API indisponible : {e} — outputs par défaut")
            from agents import (
                _FALLBACK_ANALYSIS, _FALLBACK_ACTIVITIES, _FALLBACK_PDF_CONTENT
            )
            agent_outputs = {
                "analysis":    _FALLBACK_ANALYSIS,
                "activities":  _FALLBACK_ACTIVITIES,
                "pdf_content": _FALLBACK_PDF_CONTENT,
                "fallback_used": True,
                "error": str(e)
            }

        analysis    = agent_outputs.get("analysis",    "")
        activities  = agent_outputs.get("activities",  "")
        pdf_content = agent_outputs.get("pdf_content", "")
        fallback    = agent_outputs.get("fallback_used", False)

        self._trace.record("AGENT-1", "ANALYSIS",
                           f"Output : {len(analysis)} caractères — fallback={fallback}")
        self._trace.record("AGENT-2", "GENERATION",
                           f"Output : {len(activities)} caractères — fallback={fallback}")
        self._trace.record("AGENT-3", "STRUCTURATION",
                           f"Output : {len(pdf_content)} caractères — fallback={fallback}")

        log_agent(logger, "WORKFLOW", "STEP-2",
                  f"Agents terminés — analyse={len(analysis)}c, "
                  f"activités={len(activities)}c, pdf_struct={len(pdf_content)}c")

        # ── Étape 3a : Génération des images d'exercices (Pillow, 100% local) ────
        log_agent(logger, "WORKFLOW", "STEP-3a",
                  "Étape 3a — Génération images d'exercices (Pillow, local)")
        activity_images = {}
        try:
            from exercise_image_generator import generate_all_exercise_images
            activity_images = generate_all_exercise_images(
                activity_type=activity_type,
                age=age,
                output_dir=output_dir
            )
            generated_count = sum(1 for v in activity_images.values() if v)
            self._trace.record("IMAGE", "EXERCISE",
                               f"{generated_count}/3 images d'exercices générées (Pillow)")
            log_agent(logger, "WORKFLOW", "STEP-3a",
                      f"{generated_count}/3 images d'exercices générées")
        except Exception as e:
            log_agent(logger, "WORKFLOW", "STEP-3a",
                      f"Images exercices ignorées : {e}", level="warning")
            self._trace.record("IMAGE", "SKIP", f"Images exercices ignorées : {e}")

        # ── Étape 3b : Génération PDF ─────────────────────────────────────────
        log_agent(logger, "WORKFLOW", "STEP-3b", "Étape 3b — Génération PDF (ReportLab)")

        try:
            from pdf_generator import generate_pdf
            metadata = {
                "age":           f"{age} ans",
                "level":         level,
                "activity_type": activity_type,
                "objective":     objective
            }
            pdf_path = generate_pdf(
                analysis=analysis or pdf_content,
                activities=activities,
                metadata=metadata,
                output_dir=output_dir,
                activity_images=activity_images
            )
            log_agent(logger, "WORKFLOW", "STEP-3b", f"PDF généré : {pdf_path}")
            self._trace.record("PDF", "GENERATION", f"Fichier PDF créé : {pdf_path}")
        except Exception as e:
            log_agent(logger, "WORKFLOW", "ERROR",
                      f"PDF échoué : {e}", level="error")
            self._trace.record("PDF", "ERROR", f"Génération PDF échouée : {e}")
            pdf_path = ""

        # ── Finalisation ───────────────────────────────────────────────────────
        duration = (datetime.now() - start_time).total_seconds()
        self._trace.finish(pdf_path, duration)

        result = {
            "analysis":     analysis,
            "activities":   activities,
            "pdf_content":  pdf_content,
            "pdf_path":     pdf_path,
            "duration_sec": round(duration, 2),
            "log_path":     os.getenv("LOG_FILE", "./outputs/agents.log"),
            "rag_chars":    rag_chars,
            "fallback_used": fallback
        }

        # Résumé JSON d'audit
        summary_path = (
            Path(output_dir) /
            f"run_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        try:
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump({
                    "metadata":      params,
                    "duration_sec":  result["duration_sec"],
                    "pdf_path":      pdf_path,
                    "rag_chars":     rag_chars,
                    "fallback_used": fallback
                }, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        log_agent(logger, "WORKFLOW", "COMPLETE",
                  f"Workflow terminé en {duration:.1f}s — PDF : {pdf_path}")
        return result


# ── Webhook n8n ────────────────────────────────────────────────────────────────

def trigger_n8n_workflow(payload: dict) -> dict:
    """
    Déclenche le workflow via un webhook n8n (optionnel).
    Retombe en exécution locale si n8n est indisponible.
    """
    n8n_url = os.getenv("N8N_WEBHOOK_URL", "")
    if not n8n_url:
        log_agent(logger, "N8N", "INFO",
                  "N8N_WEBHOOK_URL non configurée — exécution locale")
        return _run_locally(payload)

    try:
        import requests
        log_agent(logger, "N8N", "INFO", f"Envoi vers webhook : {n8n_url}")
        resp = requests.post(n8n_url, json=payload, timeout=10)
        resp.raise_for_status()
        log_agent(logger, "N8N", "COMPLETE", "Webhook n8n déclenché avec succès")
        return resp.json()
    except Exception as e:
        log_agent(logger, "N8N", "ERROR",
                  f"Webhook échoué ({e}) — fallback local", level="warning")
        return _run_locally(payload)


def _run_locally(payload: dict) -> dict:
    wf = TeachingWorkflow()
    return wf.run(
        age=payload.get("age", 8),
        level=payload.get("level", "CE2"),
        activity_type=payload.get("activity_type", "logique"),
        objective=payload.get("objective", "Développer la pensée logique"),
        output_dir=payload.get("output_dir", "./outputs")
    )


# ── CLI rapide ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    result = trigger_n8n_workflow({
        "age": 8,
        "level": "CE2",
        "activity_type": "logique et suites",
        "objective": "Développer la pensée algorithmique",
        "output_dir": "./outputs"
    })
    print(f"\nPDF       : {result.get('pdf_path')}")
    print(f"Durée     : {result.get('duration_sec')}s")
    print(f"Fallback  : {result.get('fallback_used')}")
