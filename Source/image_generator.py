"""
image_generator.py - Génération d'illustrations via Google Gemini (Imagen 3).
Remplace DALL-E 3 par l'API Google AI Studio — clé gratuite disponible.

Clé API : aistudio.google.com → Get API Key
Variable .env : GOOGLE_API_KEY=AIza...

Fallback : si GOOGLE_API_KEY absent ou quota dépassé, retourne None
et le PDF est généré sans illustration.
"""

import os
import time
import logging
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from logger import get_logger, log_agent

load_dotenv()
logger = get_logger(__name__)

OUTPUT_DIR     = os.getenv("OUTPUT_DIR", "./outputs")
GEMINI_IMG_MODEL  = "gemini-3.1-flash-image-preview"
GEMINI_IMG_FAST   = "gemini-2.5-flash-image"     # fallback


# ── Prompts par activité ───────────────────────────────────────────────────────

_BASE_STYLE = (
    "Colorful cartoon illustration, child-friendly, primary school style, "
    "bright cheerful colors, simple shapes, no text, no letters, no numbers visible, "
    "educational poster style for children aged {age}. "
    "Clean white background, simple bold outlines."
)

_ACTIVITY_PROMPTS = {
    1: (
        "Happy children sitting around a classroom table discovering number patterns "
        "on large colorful cards. Teacher pointing at a sequence of cards. "
        "Warm, inviting classroom environment. {style}"
    ),
    2: (
        "Children joyfully sorting and matching colorful geometric shapes — circles, "
        "squares and triangles in red and blue — arranged in repeating patterns on the floor. "
        "Engaged, smiling faces. {style}"
    ),
    3: (
        "One child standing blindfolded acting as a friendly robot, another child "
        "giving step-by-step directions with clear hand gestures. "
        "Simple obstacle course made of chairs in a bright classroom. {style}"
    ),
}

_TYPE_PROMPTS = {
    "Logique & Raisonnement": (
        "Cheerful children solving colorful logic puzzles and riddles together "
        "at school desks, bright classroom with educational posters. {style}"
    ),
    "Suites & Patterns": (
        "Primary school children arranging colorful beads and blocks "
        "in repeating sequences on a table, focused and happy. {style}"
    ),
    "Pensée Algorithmique": (
        "Children following step-by-step illustrated instruction cards "
        "with arrows and colorful icons spread on the classroom floor. {style}"
    ),
    "Résolution de Problèmes": (
        "Smiling children collaborating around a large colorful puzzle "
        "on a classroom table, thinking and pointing. {style}"
    ),
    "Puzzles & Enigmes": (
        "Excited children working on a giant colorful jigsaw puzzle "
        "in a bright, cheerful classroom setting. {style}"
    ),
    "Mini-Jeux Mathématiques": (
        "Children playing a fun math board game with colorful tokens, dice "
        "and number cards on a classroom floor, laughing and engaged. {style}"
    ),
    "Codage Débranché": (
        "Children playing unplugged coding game — laying out large arrow cards "
        "on the floor to program a path, bright colors, no screens. {style}"
    ),
}


def _build_prompt(activity_index: int, activity_type: str, age: int) -> str:
    style = _BASE_STYLE.format(age=age)
    if activity_index in _ACTIVITY_PROMPTS:
        return _ACTIVITY_PROMPTS[activity_index].format(style=style)
    fallback = _TYPE_PROMPTS.get(
        activity_type,
        "Happy children doing a fun educational activity in a colorful classroom. {style}"
    )
    return fallback.format(style=style)


# ── Génération via Gemini Image Generation ────────────────────────────────────

def _generate_with_gemini(client, model: str, prompt: str, save_path: str) -> bool:
    """
    Génère une image via Gemini image generation (generate_content).
    Récupère la première partie inline_data de la réponse.
    """
    import base64
    try:
        from google.genai import types
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"]
            )
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image_bytes = base64.b64decode(part.inline_data.data)
                with open(save_path, "wb") as f:
                    f.write(image_bytes)
                return True
        log_agent(logger, "IMAGE", "ERROR",
                  f"Gemini ({model}) : aucune image dans la réponse", level="warning")
        return False
    except Exception as e:
        log_agent(logger, "IMAGE", "ERROR",
                  f"Gemini ({model}) échoué : {e}", level="warning")
        return False


def generate_activity_image(
    activity_index: int,
    activity_type: str,
    age: int,
    output_dir: str = OUTPUT_DIR
) -> Optional[str]:
    """
    Génère une illustration pour une activité via Google Imagen 3.

    Args:
        activity_index : 1, 2 ou 3
        activity_type  : type d'activité
        age            : âge de l'enfant
        output_dir     : dossier de sauvegarde

    Returns:
        Chemin local de l'image (.png) ou None si génération impossible.
    """
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key or api_key in ("AIza_VOTRE_CLE_ICI", ""):
        log_agent(logger, "IMAGE", "SKIP",
                  f"GOOGLE_API_KEY absent — activité {activity_index} sans illustration",
                  level="warning")
        return None

    try:
        from google import genai
    except ImportError:
        log_agent(logger, "IMAGE", "ERROR",
                  "Package google-genai non installé — pip install google-genai",
                  level="error")
        return None

    prompt = _build_prompt(activity_index, activity_type, age)
    log_agent(logger, "IMAGE", "GENERATE",
              f"Génération Gemini Image — activité {activity_index} | type: {activity_type}")

    try:
        client    = genai.Client(api_key=api_key)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        ts        = int(time.time())
        save_path = str(Path(output_dir) / f"activity_{activity_index}_{ts}.png")

        # Modèle principal : gemini-3.1-flash-image-preview
        if _generate_with_gemini(client, GEMINI_IMG_MODEL, prompt, save_path):
            log_agent(logger, "IMAGE", "COMPLETE",
                      f"Image {activity_index} sauvegardée : {save_path}")
            return save_path

        # Fallback : gemini-2.5-flash-image
        log_agent(logger, "IMAGE", "FALLBACK",
                  f"Tentative avec {GEMINI_IMG_FAST}...", level="warning")
        if _generate_with_gemini(client, GEMINI_IMG_FAST, prompt, save_path):
            log_agent(logger, "IMAGE", "COMPLETE",
                      f"Image {activity_index} (fallback) sauvegardée : {save_path}")
            return save_path

        return None

    except Exception as e:
        log_agent(logger, "IMAGE", "ERROR",
                  f"Génération image {activity_index} échouée : {e}", level="error")
        return None


def generate_all_images(
    activity_type: str,
    age: int,
    output_dir: str = OUTPUT_DIR
) -> dict:
    """
    Génère les illustrations pour les 3 activités.

    Returns:
        dict {1: path_or_None, 2: path_or_None, 3: path_or_None}
    """
    log_agent(logger, "IMAGE", "START",
              f"Génération 3 illustrations Imagen 3 — type={activity_type}, age={age}")

    images = {}
    for i in range(1, 4):
        images[i] = generate_activity_image(i, activity_type, age, output_dir)
        if images[i]:
            time.sleep(0.3)

    generated = sum(1 for v in images.values() if v)
    log_agent(logger, "IMAGE", "COMPLETE",
              f"{generated}/3 illustrations générées (Gemini Image)")
    return images
