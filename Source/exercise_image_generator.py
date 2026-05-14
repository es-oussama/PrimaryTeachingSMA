"""
exercise_image_generator.py
Génère des images d'exercices visuelles et ludiques pour enfants (Pillow).
Aucune API externe — 100% local et gratuit.

3 types d'images selon l'activité :
  1. Suite numérique   → cartes colorées avec terme manquant
  2. Pattern visuel    → formes/couleurs avec élément manquant
  3. Grille robot      → parcours du robot débranché

Adaptées à l'âge : difficulté ajustée selon 5-7 / 8-9 / 10-12 ans.
"""

import os
import random
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont
from logger import get_logger, log_agent

logger = get_logger(__name__)

# ── Constantes visuelles ───────────────────────────────────────────────────────

W, H = 1200, 380          # dimensions de l'image (pixels)
PADDING = 30

# Palette enfant-friendly
C = {
    "bg":       "#FFFDE7",   # fond jaune très clair
    "card_1":   "#4A90E2",   # bleu
    "card_2":   "#E2574A",   # rouge
    "card_3":   "#4CB87A",   # vert
    "card_4":   "#F5A623",   # orange
    "card_5":   "#9B59B6",   # violet
    "question": "#FF6B35",   # orange vif pour "?"
    "text_w":   "#FFFFFF",   # texte blanc
    "text_d":   "#2C3E50",   # texte sombre
    "border":   "#BDC3C7",   # bordure grise
    "title_bg": "#2C3E50",   # fond titre
    "grid_bg":  "#ECF0F1",   # fond grille
    "obstacle": "#E74C3C",   # obstacle rouge
    "robot":    "#3498DB",   # robot bleu
    "star":     "#F1C40F",   # étoile jaune
    "path":     "#2ECC71",   # chemin vert
    "shadow":   "#B0BEC5",   # ombre
}

# Couleurs des formes pour pattern
SHAPE_COLORS = ["#E2574A", "#4A90E2", "#4CB87A", "#F5A623", "#9B59B6"]
SHAPE_NAMES  = ["Cercle", "Carré", "Triangle", "Étoile", "Losange"]


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Charge Arial depuis Windows, sinon retourne la police par défaut."""
    font_name = "arialbd.ttf" if bold else "arial.ttf"
    paths = [
        f"C:/Windows/Fonts/{font_name}",
        f"C:/Windows/Fonts/Arial.ttf",
    ]
    for p in paths:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _rounded_rect(draw: ImageDraw.Draw, xy: tuple, radius: int,
                  fill: str, outline: str = None, width: int = 0) -> None:
    """Dessine un rectangle arrondi."""
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius,
                            fill=fill, outline=outline, width=width)


def _draw_title_bar(draw: ImageDraw.Draw, text: str,
                    emoji: str = "", font_size: int = 36) -> None:
    """Bandeau titre en haut de l'image."""
    _rounded_rect(draw, (PADDING, PADDING, W - PADDING, PADDING + 60),
                  radius=12, fill=C["title_bg"])
    font = _load_font(font_size, bold=True)
    label = f"{emoji}  {text}" if emoji else text
    draw.text((W // 2, PADDING + 30), label, font=font,
              fill=C["text_w"], anchor="mm")


def _draw_subtitle(draw: ImageDraw.Draw, text: str, y: int,
                   color: str = None, size: int = 26) -> None:
    font = _load_font(size)
    draw.text((W // 2, y), text, font=font,
              fill=color or C["text_d"], anchor="mm")


# ── Générateur 1 : Suite numérique ────────────────────────────────────────────

def _get_sequence(age: int, activity_index: int) -> tuple:
    """Retourne (liste_termes, règle_texte, position_manquante)."""
    sequences = {
        # (termes, règle affichée, index du terme manquant)
        (5,  1): ([2, 4, "?", 8, 10],      "Règle : + 2",  2),
        (5,  2): ([1, 3, "?", 7, 9],       "Règle : + 2",  2),
        (5,  3): ([5, "?", 15, 20, 25],    "Règle : + 5",  1),
        (8,  1): ([3, 6, 9, "?", 15],      "Règle : + 3",  3),
        (8,  2): ([2, 5, 8, "?", 14],      "Règle : + 3",  3),
        (8,  3): ([10, 20, "?", 40, 50],   "Règle : + 10", 2),
        (10, 1): ([4, 8, 12, "?", 20],     "Règle : + 4",  3),
        (10, 2): ([100, 90, "?", 70, 60],  "Règle : - 10", 2),
        (10, 3): ([2, 4, 8, "?", 32],      "Règle : × 2",  3),
    }
    age_key = 5 if age <= 7 else (8 if age <= 9 else 10)
    return sequences.get((age_key, activity_index),
                         ([1, 2, "?", 4, 5], "Règle : + 1", 2))


def generate_sequence_image(age: int, activity_index: int,
                             save_path: str) -> Optional[str]:
    """Carte colorée : 5 nombres dont un manquant + règle à trouver."""
    img  = Image.new("RGB", (W, H), C["bg"])
    draw = ImageDraw.Draw(img)

    _draw_title_bar(draw, "Complète la suite !", emoji="🔢")

    terms, rule, missing_idx = _get_sequence(age, activity_index)
    colors = [C["card_1"], C["card_2"], C["card_3"], C["card_4"], C["card_5"]]

    card_w, card_h = 150, 120
    total_w = len(terms) * card_w + (len(terms) - 1) * 30
    start_x = (W - total_w) // 2
    card_y  = 115

    font_num    = _load_font(52, bold=True)
    font_arrow  = _load_font(34)
    font_rule   = _load_font(30, bold=True)
    font_answer = _load_font(22)

    for i, term in enumerate(terms):
        cx = start_x + i * (card_w + 30)
        is_q = (str(term) == "?")
        color = C["question"] if is_q else colors[i % len(colors)]

        # Ombre
        _rounded_rect(draw, (cx + 5, card_y + 5, cx + card_w + 5, card_y + card_h + 5),
                      radius=18, fill=C["shadow"])
        # Carte
        _rounded_rect(draw, (cx, card_y, cx + card_w, card_y + card_h),
                      radius=18, fill=color, outline="white", width=3)

        label = "?" if is_q else str(term)
        draw.text((cx + card_w // 2, card_y + card_h // 2),
                  label, font=font_num, fill="white", anchor="mm")

        # Flèche entre les cartes
        if i < len(terms) - 1:
            ax = cx + card_w + 10
            ay = card_y + card_h // 2
            draw.text((ax, ay), "→", font=font_arrow,
                      fill=C["text_d"], anchor="lm")

    # Règle et réponse
    draw.text((W // 2, card_y + card_h + 30),
              rule, font=font_rule, fill=C["text_d"], anchor="mm")

    answer = [t for t in terms if t != "?"]
    if len(answer) >= 2 and isinstance(answer[-1], int) and isinstance(answer[-2], int):
        diff = answer[-1] - answer[-2]
        correct = answer[-1] + diff if missing_idx == len(terms) - 1 else None
        if correct is None and missing_idx > 0 and isinstance(terms[missing_idx - 1], int):
            correct = terms[missing_idx - 1] + diff
        if correct:
            draw.text((W // 2, card_y + card_h + 68),
                      f"(Réponse : {correct})",
                      font=font_answer, fill=C["card_3"], anchor="mm")

    img.save(save_path, "PNG")
    return save_path


# ── Générateur 2 : Pattern visuel ─────────────────────────────────────────────

def _draw_shape(draw: ImageDraw.Draw, shape: int, cx: int, cy: int,
                r: int, color: str, is_question: bool = False) -> None:
    """Dessine une forme géométrique (0=cercle, 1=carré, 2=triangle, 3=étoile)."""
    fill = C["question"] if is_question else color
    outline = "white"
    lw = 3

    if shape == 0:  # Cercle
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     fill=fill, outline=outline, width=lw)
    elif shape == 1:  # Carré
        draw.rounded_rectangle([cx - r, cy - r, cx + r, cy + r],
                               radius=8, fill=fill, outline=outline, width=lw)
    elif shape == 2:  # Triangle
        pts = [(cx, cy - r), (cx - r, cy + r), (cx + r, cy + r)]
        draw.polygon(pts, fill=fill, outline=outline)
    else:  # Losange
        pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
        draw.polygon(pts, fill=fill, outline=outline)

    if is_question:
        font_q = _load_font(r, bold=True)
        draw.text((cx, cy), "?", font=font_q, fill="white", anchor="mm")


def _get_pattern(age: int, activity_index: int) -> list:
    """Retourne un pattern de (forme, couleur) avec le dernier = '?'."""
    if age <= 7:
        # Cycle simple : 2 formes/couleurs
        patterns = [
            [(0, 0), (1, 1), (0, 0), (1, 1), (0, 0), None],   # cercle/carré
            [(0, 2), (0, 3), (0, 2), (0, 3), (0, 2), None],   # vert/orange
            [(1, 0), (1, 1), (1, 0), (1, 1), (1, 0), None],   # bleu/rouge
        ]
    elif age <= 9:
        # Cycle de 3
        patterns = [
            [(0, 0), (1, 1), (2, 2), (0, 0), (1, 1), None],   # 3 formes
            [(0, 0), (0, 1), (0, 2), (0, 0), (0, 1), None],   # même forme 3 couleurs
            [(0, 3), (1, 4), (2, 0), (0, 3), (1, 4), None],   # 3 formes couleurs
        ]
    else:
        # Cycle complexe
        patterns = [
            [(0, 0), (1, 1), (0, 2), (1, 0), (0, 1), None],
            [(2, 0), (1, 1), (0, 2), (2, 0), (1, 1), None],
            [(0, 0), (0, 1), (1, 2), (0, 0), (0, 1), None],
        ]

    idx = (activity_index - 1) % len(patterns)
    pat = patterns[idx]
    # Le dernier None = question, l'élément attendu = pat[0] (cycle)
    return pat


def generate_pattern_image(age: int, activity_index: int,
                            save_path: str) -> Optional[str]:
    """Pattern de formes colorées avec le dernier à deviner."""
    img  = Image.new("RGB", (W, H), C["bg"])
    draw = ImageDraw.Draw(img)

    _draw_title_bar(draw, "Quel vient ensuite ?", emoji="🎨")

    pattern = _get_pattern(age, activity_index)
    n       = len(pattern)
    r       = 55
    total_w = n * (2 * r + 20) - 20
    start_x = (W - total_w) // 2
    cy      = H // 2 + 20
    font_arrow = _load_font(30)

    # Identifier la réponse (premier élément du cycle)
    answer_shape, answer_color_idx = pattern[0]

    for i, item in enumerate(pattern):
        cx = start_x + i * (2 * r + 20) + r
        is_q = (item is None)

        if is_q:
            shape, color_idx = answer_shape, answer_color_idx
        else:
            shape, color_idx = item

        color = SHAPE_COLORS[color_idx % len(SHAPE_COLORS)]

        # Ombre
        _draw_shape(draw, shape, cx + 4, cy + 4, r, C["shadow"])
        # Forme
        _draw_shape(draw, shape, cx, cy, r, color, is_question=is_q)

        # Flèche
        if i < n - 1:
            ax = cx + r + 3
            draw.text((ax, cy), "→", font=font_arrow,
                      fill=C["text_d"], anchor="lm")

    # Légende sous les formes
    font_hint = _load_font(24)
    answer_color = SHAPE_COLORS[answer_color_idx % len(SHAPE_COLORS)]
    shape_name   = ["Cercle", "Carré", "Triangle", "Losange"][answer_shape % 4]
    _draw_subtitle(draw,
                   f"Indice : observe le motif qui se répète !",
                   cy + r + 40, color=C["text_d"], size=24)

    img.save(save_path, "PNG")
    return save_path


# ── Générateur 3 : Grille robot ───────────────────────────────────────────────

def _get_grid(age: int, activity_index: int) -> tuple:
    """
    Retourne (taille_grille, pos_robot, pos_star, obstacles, chemin).
    """
    grids = {
        (5,  1): (4, (0, 0), (3, 3), [(1, 1), (2, 2)],
                  [(0,0),(1,0),(2,0),(3,0),(3,1),(3,2),(3,3)]),
        (5,  2): (4, (0, 3), (3, 0), [(1, 2), (2, 1)],
                  [(0,3),(0,2),(0,1),(0,0),(1,0),(2,0),(3,0)]),
        (5,  3): (4, (0, 0), (3, 2), [(0, 2), (2, 0), (1, 3)],
                  [(0,0),(1,0),(2,0),(3,0),(3,1),(3,2)]),
        (8,  1): (5, (0, 0), (4, 4), [(1, 1), (3, 2), (2, 3)],
                  [(0,0),(1,0),(2,0),(2,1),(2,2),(3,2),(4,2),(4,3),(4,4)]),
        (8,  2): (5, (0, 2), (4, 2), [(2, 0), (2, 4), (1, 3)],
                  [(0,2),(1,2),(2,2),(3,2),(4,2)]),
        (8,  3): (5, (0, 0), (4, 3), [(1, 0), (2, 2), (3, 1), (0, 3)],
                  [(0,0),(0,1),(0,2),(1,2),(2,2),(2,3),(3,3),(4,3)]),
        (10, 1): (6, (0, 0), (5, 5), [(1,1),(2,3),(3,2),(4,1),(1,4)],
                  [(0,0),(1,0),(2,0),(2,1),(2,2),(3,2),(3,3),(4,3),(5,3),(5,4),(5,5)]),
        (10, 2): (6, (0, 3), (5, 2), [(1,2),(2,4),(3,1),(4,3)],
                  [(0,3),(0,2),(1,2),(2,2),(3,2),(4,2),(5,2)]),
        (10, 3): (6, (0, 0), (5, 4), [(2,0),(1,3),(3,2),(4,1),(0,4)],
                  [(0,0),(0,1),(0,2),(1,2),(2,2),(2,3),(3,3),(4,3),(5,3),(5,4)]),
    }
    age_key = 5 if age <= 7 else (8 if age <= 9 else 10)
    return grids.get(
        (age_key, activity_index),
        (4, (0, 0), (3, 3), [(1, 2)],
         [(0,0),(1,0),(2,0),(3,0),(3,1),(3,2),(3,3)])
    )


def generate_robot_grid_image(age: int, activity_index: int,
                               save_path: str) -> Optional[str]:
    """Grille de parcours pour le robot débranché."""
    img  = Image.new("RGB", (W, H), C["bg"])
    draw = ImageDraw.Draw(img)

    _draw_title_bar(draw, "Guide le robot jusqu'à l'étoile !", emoji="🤖")

    grid_size, robot_pos, star_pos, obstacles, solution_path = \
        _get_grid(age, activity_index)

    cell  = min((H - 150) // grid_size, (W - 200) // grid_size, 62)
    total = grid_size * cell
    ox    = (W - total) // 2
    oy    = 100

    font_cell  = _load_font(28, bold=True)
    font_coord = _load_font(18)
    font_hint  = _load_font(22)

    # Dessiner la grille
    for row in range(grid_size):
        for col in range(grid_size):
            x1 = ox + col * cell
            y1 = oy + row * cell
            x2 = x1 + cell
            y2 = y1 + cell

            pos = (col, row)

            if pos in obstacles:
                fill = C["obstacle"]
            elif (col, row) in solution_path:
                fill = "#D5F5E3"    # vert très clair
            else:
                fill = C["grid_bg"]

            draw.rectangle([x1, y1, x2, y2],
                            fill=fill, outline="#BDC3C7", width=2)

            cx, cy = x1 + cell // 2, y1 + cell // 2

            if pos == robot_pos:
                _rounded_rect(draw, (x1 + 5, y1 + 5, x2 - 5, y2 - 5),
                              radius=8, fill=C["robot"])
                draw.text((cx, cy), "🤖", font=font_cell,
                          fill="white", anchor="mm")
            elif pos == star_pos:
                _rounded_rect(draw, (x1 + 5, y1 + 5, x2 - 5, y2 - 5),
                              radius=8, fill=C["star"])
                draw.text((cx, cy), "⭐", font=font_cell,
                          fill="white", anchor="mm")
            elif pos in obstacles:
                draw.text((cx, cy), "🚧", font=font_cell,
                          fill="white", anchor="mm")

    # Légende
    legend_x = ox + total + 25
    legend_y = oy + 10
    items = [
        (C["robot"],   "🤖 Robot (départ)"),
        (C["star"],    "⭐ Arrivée"),
        (C["obstacle"],"🚧 Obstacle"),
    ]
    font_leg = _load_font(20)
    for color, label in items:
        _rounded_rect(draw, (legend_x, legend_y, legend_x + 22, legend_y + 22),
                      radius=4, fill=color)
        draw.text((legend_x + 30, legend_y + 11), label,
                  font=font_leg, fill=C["text_d"], anchor="lm")
        legend_y += 35

    # Instruction
    steps = len(solution_path) - 1
    _draw_subtitle(draw,
                   f"Combien d'étapes minimum pour atteindre l'étoile ? ({steps} étapes)",
                   oy + total + 25, color=C["text_d"], size=22)

    img.save(save_path, "PNG")
    return save_path


# ── Sélecteur principal ────────────────────────────────────────────────────────

_GENERATORS = {
    1: generate_sequence_image,
    2: generate_pattern_image,
    3: generate_robot_grid_image,
}

_TYPE_TO_GEN = {
    "Suites & Patterns":        {1: generate_sequence_image,
                                  2: generate_pattern_image,
                                  3: generate_sequence_image},
    "Logique & Raisonnement":   {1: generate_sequence_image,
                                  2: generate_pattern_image,
                                  3: generate_robot_grid_image},
    "Pensée Algorithmique":     {1: generate_robot_grid_image,
                                  2: generate_sequence_image,
                                  3: generate_robot_grid_image},
    "Codage Débranché":         {1: generate_robot_grid_image,
                                  2: generate_pattern_image,
                                  3: generate_robot_grid_image},
    "Mini-Jeux Mathématiques":  {1: generate_sequence_image,
                                  2: generate_pattern_image,
                                  3: generate_sequence_image},
    "Résolution de Problèmes":  {1: generate_sequence_image,
                                  2: generate_robot_grid_image,
                                  3: generate_pattern_image},
    "Puzzles & Enigmes":        {1: generate_pattern_image,
                                  2: generate_sequence_image,
                                  3: generate_robot_grid_image},
}


def generate_exercise_image(activity_index: int, activity_type: str,
                             age: int, output_dir: str = "./outputs") -> Optional[str]:
    """
    Génère l'image d'exercice adaptée à l'activité.

    Returns:
        Chemin local du fichier PNG, ou None si erreur.
    """
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        save_path = str(
            Path(output_dir) / f"exercise_{activity_index}_{activity_type[:8].replace(' ', '')}.png"
        )

        generators = _TYPE_TO_GEN.get(activity_type, _GENERATORS)
        gen_func   = generators.get(activity_index, generate_sequence_image)

        result = gen_func(age, activity_index, save_path)

        log_agent(logger, "IMAGE", "EXERCISE",
                  f"Image exercice {activity_index} générée : {save_path}")
        return result

    except Exception as e:
        log_agent(logger, "IMAGE", "ERROR",
                  f"Génération exercice {activity_index} échouée : {e}", level="error")
        return None


def generate_all_exercise_images(activity_type: str, age: int,
                                  output_dir: str = "./outputs") -> dict:
    """
    Génère les 3 images d'exercices pour un run complet.

    Returns:
        {1: path, 2: path, 3: path}
    """
    log_agent(logger, "IMAGE", "START",
              f"Génération 3 images d'exercices — type={activity_type}, age={age}")
    images = {}
    for i in range(1, 4):
        images[i] = generate_exercise_image(i, activity_type, age, output_dir)

    done = sum(1 for v in images.values() if v)
    log_agent(logger, "IMAGE", "COMPLETE",
              f"{done}/3 images d'exercices générées (Pillow, 100% local)")
    return images
