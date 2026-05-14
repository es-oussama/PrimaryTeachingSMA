"""
pdf_generator.py - Génération de fiches pédagogiques PDF avec ReportLab.
Produit un document propre et professionnel adapté à un usage en classe.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, KeepTogether, Image as RLImage
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)

# Image dimensions dans le PDF (largeur pleine colonne, hauteur fixe)
IMG_WIDTH  = 17   * cm
IMG_HEIGHT = 5.8  * cm

# ── Palette de couleurs ────────────────────────────────────────────────────────
COLOR_PRIMARY   = HexColor("#2563EB")   # Bleu
COLOR_SECONDARY = HexColor("#10B981")   # Vert
COLOR_ACCENT    = HexColor("#F59E0B")   # Orange
COLOR_LIGHT_BG  = HexColor("#EFF6FF")   # Bleu très clair
COLOR_HEADER_BG = HexColor("#1E40AF")   # Bleu foncé
COLOR_TEXT      = HexColor("#1F2937")   # Gris foncé
COLOR_MUTED     = HexColor("#6B7280")   # Gris moyen


def build_styles() -> dict:
    """Construit les styles ReportLab du document."""
    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "DocTitle",
            parent=base["Title"],
            fontSize=22,
            textColor=white,
            alignment=TA_CENTER,
            spaceAfter=6,
            fontName="Helvetica-Bold"
        ),
        "subtitle": ParagraphStyle(
            "DocSubtitle",
            parent=base["Normal"],
            fontSize=12,
            textColor=HexColor("#BFDBFE"),
            alignment=TA_CENTER,
            spaceAfter=4,
            fontName="Helvetica"
        ),
        "section_header": ParagraphStyle(
            "SectionHeader",
            parent=base["Heading2"],
            fontSize=13,
            textColor=white,
            alignment=TA_LEFT,
            spaceBefore=14,
            spaceAfter=6,
            leftIndent=0,
            fontName="Helvetica-Bold"
        ),
        "activity_title": ParagraphStyle(
            "ActivityTitle",
            parent=base["Heading3"],
            fontSize=11,
            textColor=COLOR_PRIMARY,
            spaceBefore=8,
            spaceAfter=4,
            fontName="Helvetica-Bold"
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontSize=10,
            textColor=COLOR_TEXT,
            alignment=TA_JUSTIFY,
            spaceAfter=4,
            leading=15,
            fontName="Helvetica"
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["Normal"],
            fontSize=10,
            textColor=COLOR_TEXT,
            spaceAfter=3,
            leftIndent=16,
            bulletIndent=4,
            fontName="Helvetica"
        ),
        "info_label": ParagraphStyle(
            "InfoLabel",
            parent=base["Normal"],
            fontSize=9,
            textColor=COLOR_MUTED,
            fontName="Helvetica-Bold",
            spaceAfter=2
        ),
        "info_value": ParagraphStyle(
            "InfoValue",
            parent=base["Normal"],
            fontSize=10,
            textColor=COLOR_TEXT,
            fontName="Helvetica"
        ),
        "footer": ParagraphStyle(
            "Footer",
            parent=base["Normal"],
            fontSize=8,
            textColor=COLOR_MUTED,
            alignment=TA_CENTER,
            fontName="Helvetica"
        ),
        "note": ParagraphStyle(
            "Note",
            parent=base["Normal"],
            fontSize=9,
            textColor=HexColor("#92400E"),
            fontName="Helvetica",
            leftIndent=8,
            rightIndent=8,
            spaceAfter=6
        )
    }
    return styles


class PDFGenerator:
    """Génère une fiche pédagogique PDF à partir du contenu produit par les agents."""

    def __init__(self, output_dir: str = "./outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = build_styles()

    def generate(
        self,
        analysis: str,
        activities: str,
        metadata: dict,
        filename: Optional[str] = None,
        activity_images: Optional[dict] = None
    ) -> str:
        """
        Génère le PDF et retourne le chemin du fichier créé.

        Args:
            analysis        : Texte de l'Agent 1
            activities      : Texte de l'Agent 2
            metadata        : Infos contextuelles (age, level, etc.)
            filename        : Nom du fichier (auto-généré si None)
            activity_images : dict {1: path, 2: path, 3: path} — images DALL-E optionnelles
        """
        if not filename:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fiche_pedagogique_{ts}.pdf"

        filepath = self.output_dir / filename
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            leftMargin=2*cm,
            rightMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        images = activity_images or {}

        story = []
        story += self._build_header(metadata)
        story += self._build_info_table(metadata)
        story += self._build_analysis_section(analysis)
        story += self._build_activities_section(activities, images)
        story += self._build_footer()

        doc.build(story)
        logger.info(f"[PDF] Fiche générée : {filepath}")
        return str(filepath)

    # ── Sections ───────────────────────────────────────────────────────────────

    def _build_header(self, meta: dict) -> list:
        """Bandeau d'en-tête coloré avec titre."""
        elements = []

        # Tableau d'en-tête avec fond coloré
        title_text = Paragraph("Fiche Pédagogique", self.styles["title"])
        subtitle_text = Paragraph(
            f"Assistant d'Aide à l'Enseignement Primaire — Système Multi-Agents",
            self.styles["subtitle"]
        )

        header_table = Table(
            [[title_text], [subtitle_text]],
            colWidths=[17*cm]
        )
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), COLOR_HEADER_BG),
            ("TOPPADDING",    (0, 0), (-1, -1), 14),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
            ("LEFTPADDING",   (0, 0), (-1, -1), 16),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
            ("ROUNDEDCORNERS", [6]),
        ]))

        elements.append(header_table)
        elements.append(Spacer(1, 12))
        return elements

    def _build_info_table(self, meta: dict) -> list:
        """Tableau d'informations pédagogiques (âge, niveau, type, objectif)."""
        elements = []

        rows = [
            ["Age cible",     meta.get("age", "N/A")],
            ["Niveau",        meta.get("level", "N/A")],
            ["Type activité", meta.get("activity_type", "N/A")],
            ["Objectif",      meta.get("objective", "N/A")],
            ["Date",          datetime.now().strftime("%d/%m/%Y %H:%M")],
        ]

        table_data = []
        for label, value in rows:
            table_data.append([
                Paragraph(label, self.styles["info_label"]),
                Paragraph(str(value), self.styles["info_value"])
            ])

        t = Table(table_data, colWidths=[5*cm, 12*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (0, -1), COLOR_LIGHT_BG),
            ("GRID",          (0, 0), (-1, -1), 0.5, HexColor("#DBEAFE")),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ]))

        elements.append(t)
        elements.append(Spacer(1, 14))
        return elements

    def _build_section_header(self, title: str, color=None) -> list:
        """Bandeau de section coloré."""
        c = color or COLOR_SECONDARY
        header = Table(
            [[Paragraph(title, self.styles["section_header"])]],
            colWidths=[17*cm]
        )
        header.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), c),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ]))
        return [header, Spacer(1, 6)]

    def _build_analysis_section(self, analysis: str) -> list:
        """Section Analyse Pédagogique."""
        elements = []
        elements += self._build_section_header("Analyse Pédagogique", COLOR_PRIMARY)

        if analysis:
            for line in analysis.split("\n"):
                line = line.strip()
                if not line:
                    elements.append(Spacer(1, 4))
                elif line.startswith("•") or line.startswith("-") or line.startswith("*"):
                    elements.append(Paragraph(f"• {line.lstrip('•-* ')}", self.styles["bullet"]))
                else:
                    elements.append(Paragraph(line, self.styles["body"]))
        else:
            elements.append(Paragraph("Aucune analyse disponible.", self.styles["body"]))

        elements.append(Spacer(1, 10))
        return elements

    def _build_activity_image(self, image_path: str) -> list:
        """
        Insère l'illustration DALL-E dans le PDF.
        Gère les erreurs silencieusement (image corrompue → ignorée).
        """
        elements = []
        try:
            img = RLImage(image_path, width=IMG_WIDTH, height=IMG_HEIGHT)
            img.hAlign = "CENTER"

            # Cadre autour de l'image
            frame = Table(
                [[img]],
                colWidths=[IMG_WIDTH + 0.4*cm]
            )
            frame.setStyle(TableStyle([
                ("BOX",           (0, 0), (-1, -1), 0.5, HexColor("#DBEAFE")),
                ("BACKGROUND",    (0, 0), (-1, -1), HexColor("#F8FAFF")),
                ("TOPPADDING",    (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING",   (0, 0), (-1, -1), 4),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
            ]))

            elements.append(frame)
            elements.append(Paragraph(
                "Exercice visuel généré automatiquement — à compléter par l'élève",
                self.styles["footer"]
            ))
            elements.append(Spacer(1, 8))
        except Exception as e:
            logger.warning(f"[PDF] Image ignorée ({image_path}) : {e}")
        return elements

    def _build_activities_section(self, activities: str, images: dict = None) -> list:
        """
        Section Activités générées avec illustrations DALL-E optionnelles.
        images : {1: path, 2: path, 3: path} ou dict vide / None
        """
        images = images or {}
        elements = []
        elements += self._build_section_header(
            "Activités Pédagogiques Générées (avec illustrations IA)" if images
            else "Activités Pédagogiques Générées",
            COLOR_SECONDARY
        )

        if not activities:
            elements.append(Paragraph("Aucune activité générée.", self.styles["body"]))
            elements.append(Spacer(1, 10))
            return elements

        activity_counter = 0

        for line in activities.split("\n"):
            line = line.strip()
            if not line:
                elements.append(Spacer(1, 4))
                continue

            # Détecter le début d'une nouvelle activité (## ACTIVITÉ N :)
            is_activity_header = (
                any(
                    line.startswith(f"## ACTIVITÉ {i}") or
                    line.startswith(f"## Activité {i}") or
                    line.startswith(f"ACTIVITÉ {i}") or
                    line.startswith(f"Activité {i}")
                    for i in range(1, 10)
                )
            )

            if is_activity_header:
                activity_counter += 1
                clean_title = line.strip("# ")
                elements.append(Paragraph(clean_title, self.styles["activity_title"]))

                # Insérer l'image DALL-E si disponible pour cette activité
                img_path = images.get(activity_counter)
                if img_path and Path(img_path).exists():
                    elements += self._build_activity_image(img_path)

            elif line.startswith("##"):
                clean = line.strip("# ")
                elements.append(Paragraph(clean, self.styles["activity_title"]))
            elif line.startswith("**") and line.endswith("**"):
                clean = line.strip("*")
                elements.append(Paragraph(f"<b>{clean}</b>", self.styles["body"]))
            elif line.startswith("•") or line.startswith("-") or line.startswith("*"):
                elements.append(Paragraph(f"• {line.lstrip('•-* ')}", self.styles["bullet"]))
            else:
                elements.append(Paragraph(line, self.styles["body"]))

        elements.append(Spacer(1, 10))
        return elements

    def _build_footer(self) -> list:
        """Pied de page avec mention du système."""
        elements = []
        elements.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_MUTED))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            "Généré par PrimaryTeachingSMA — Système Multi-Agents CrewAI + Claude API + DALL-E 3",
            self.styles["footer"]
        ))
        elements.append(Paragraph(
            "Document à usage pédagogique — Vérifier le contenu avant distribution en classe",
            self.styles["note"]
        ))
        return elements


# ── Interface simple ───────────────────────────────────────────────────────────

def generate_pdf(analysis: str, activities: str, metadata: dict,
                 output_dir: str = "./outputs",
                 activity_images: Optional[dict] = None) -> str:
    """Fonction utilitaire pour générer un PDF depuis n'importe quel module."""
    gen = PDFGenerator(output_dir=output_dir)
    return gen.generate(analysis, activities, metadata,
                        activity_images=activity_images)
