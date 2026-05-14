"""
app.py - Interface Streamlit redesignée — PrimaryTeachingSMA v2.
Design moderne : gradient header, cartes agents, step progress, résultats en cartes.
"""

import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Config page ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PrimaryTeachingSMA",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS global ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Fonts & base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Page background ── */
.stApp, .main { background-color: #F1F5F9 !important; }
section[data-testid="stSidebar"] { background-color: #FFFFFF !important; }

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Fix Streamlit default orange accents → blue ── */
:root {
    --primary-color: #1D4ED8 !important;
}
div[data-baseweb="slider"] div[role="slider"] { background-color: #1D4ED8 !important; }
div[data-baseweb="slider"] [data-testid="stSlider"] > div > div { background-color: #1D4ED8 !important; }
div[data-baseweb="select"] [aria-selected="true"] { background-color: #EFF6FF !important; color: #1D4ED8 !important; }
div[data-baseweb="radio"] label [data-checked="true"] ~ div { background-color: #1D4ED8 !important; }
.stRadio [data-testid="stMarkdownContainer"] { color: #1E293B !important; }

/* ── HERO HEADER ── */
.hero {
    background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 50%, #1D4ED8 100%);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(29,78,216,0.3);
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(99,102,241,0.3) 0%, transparent 70%);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -30%;
    left: 5%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(16,185,129,0.2) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0 0 0.4rem 0;
    line-height: 1.2;
    position: relative;
    z-index: 1;
}
.hero-sub {
    font-size: 1rem;
    color: #93C5FD;
    margin: 0 0 0.8rem 0;
    position: relative;
    z-index: 1;
}
.hero-badges {
    display: flex;
    gap: 0.6rem;
    flex-wrap: wrap;
    position: relative;
    z-index: 1;
}
.badge {
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    color: #E0F2FE;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 500;
    backdrop-filter: blur(4px);
}

/* ── FORM CARD ── */
.form-card {
    background: white;
    border-radius: 16px;
    padding: 1.8rem 2rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    border: 1px solid #E2E8F0;
    margin-bottom: 1.2rem;
}
.form-card h3 {
    font-size: 1rem;
    font-weight: 700;
    color: #1E293B;
    margin: 0 0 1.2rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-label {
    font-size: 0.82rem;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.4rem;
}

/* ── ACTIVITY TYPE CARDS ── */
.activity-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.6rem;
    margin-top: 0.4rem;
}
.act-card {
    background: #F8FAFC;
    border: 2px solid #E2E8F0;
    border-radius: 12px;
    padding: 0.8rem 0.5rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.82rem;
    font-weight: 500;
    color: #475569;
}
.act-card:hover {
    border-color: #3B82F6;
    background: #EFF6FF;
    color: #1D4ED8;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59,130,246,0.15);
}
.act-card.selected {
    border-color: #1D4ED8;
    background: #EFF6FF;
    color: #1D4ED8;
    box-shadow: 0 4px 12px rgba(29,78,216,0.2);
}
.act-icon { font-size: 1.4rem; display: block; margin-bottom: 0.3rem; }

/* ── SIDEBAR CARDS ── */
.status-card {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.8rem;
    border: 1px solid #E2E8F0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.status-title {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #94A3B8;
    margin-bottom: 0.7rem;
}
.status-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.35rem 0;
    font-size: 0.85rem;
    color: #334155;
    font-weight: 500;
}
.dot-green  { width:9px; height:9px; border-radius:50%; background:#10B981; flex-shrink:0; }
.dot-blue   { width:9px; height:9px; border-radius:50%; background:#3B82F6; flex-shrink:0; }
.dot-orange { width:9px; height:9px; border-radius:50%; background:#F59E0B; flex-shrink:0; }
.dot-red    { width:9px; height:9px; border-radius:50%; background:#EF4444; flex-shrink:0; }

/* ── AGENT CARDS SIDEBAR ── */
.agent-pill {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.6rem 0.8rem;
    border-radius: 10px;
    margin-bottom: 0.5rem;
    font-size: 0.83rem;
    font-weight: 600;
}
.agent-1 { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
.agent-2 { background: #F0FDF4; color: #15803D; border: 1px solid #BBF7D0; }
.agent-3 { background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
.agent-num {
    width: 22px; height: 22px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; font-weight: 800; flex-shrink: 0;
}
.num-1 { background: #1D4ED8; color: white; }
.num-2 { background: #15803D; color: white; }
.num-3 { background: #B45309; color: white; }

/* ── PIPELINE FLOW ── */
.pipeline-flow {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.78rem;
    color: #64748B;
    flex-wrap: wrap;
    margin-top: 0.5rem;
}
.pipe-step {
    background: #F1F5F9;
    border: 1px solid #CBD5E1;
    padding: 0.2rem 0.5rem;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.73rem;
    color: #475569;
}
.pipe-arrow { color: #94A3B8; font-size: 0.8rem; }

/* ── STEP PROGRESS ── */
.steps-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    margin: 1.5rem 0;
}
.step-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.3rem;
}
.step-circle {
    width: 40px; height: 40px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.9rem;
    border: 3px solid #E2E8F0;
    background: white;
    color: #94A3B8;
    transition: all 0.3s;
}
.step-circle.active  { background: #1D4ED8; color: white; border-color: #1D4ED8; box-shadow: 0 0 0 4px rgba(29,78,216,0.15); }
.step-circle.done    { background: #10B981; color: white; border-color: #10B981; }
.step-line {
    flex: 1;
    height: 3px;
    background: #E2E8F0;
    min-width: 60px;
    margin-bottom: 1.2rem;
    transition: background 0.3s;
}
.step-line.done { background: #10B981; }
.step-label { font-size: 0.72rem; font-weight: 600; color: #64748B; text-align: center; max-width: 80px; }

/* ── RESULT CARDS ── */
.result-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    border: 1px solid #E2E8F0;
    box-shadow: 0 4px 16px rgba(0,0,0,0.05);
}
.result-card h4 {
    font-size: 1rem;
    font-weight: 700;
    color: #1E293B;
    margin: 0 0 0.8rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── SUCCESS BANNER ── */
.success-banner {
    background: linear-gradient(135deg, #ECFDF5, #D1FAE5);
    border: 1px solid #6EE7B7;
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 1rem 0;
}
.success-icon { font-size: 2rem; }
.success-text h4 { font-size: 1rem; font-weight: 700; color: #065F46; margin: 0; }
.success-text p  { font-size: 0.85rem; color: #047857; margin: 0.2rem 0 0 0; }

/* ── METRIC CHIPS ── */
.metrics-row {
    display: flex;
    gap: 0.8rem;
    flex-wrap: wrap;
    margin: 1rem 0;
}
.metric-chip {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 0.7rem 1.2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 100px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.metric-val { font-size: 1.3rem; font-weight: 800; color: #1E293B; }
.metric-lbl { font-size: 0.72rem; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; }

/* ── LOG TERMINAL ── */
.log-terminal {
    background: #0F172A;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    font-family: 'Courier New', monospace;
    font-size: 0.82rem;
    color: #94A3B8;
    max-height: 280px;
    overflow-y: auto;
    line-height: 1.7;
}
.log-ok   { color: #34D399; }
.log-warn { color: #FCD34D; }
.log-err  { color: #F87171; }
.log-info { color: #60A5FA; }

/* ── DOWNLOAD BUTTON override ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #1D4ED8, #7C3AED) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.8rem 2rem !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    box-shadow: 0 8px 24px rgba(29,78,216,0.35) !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 32px rgba(29,78,216,0.45) !important;
}

/* ── PRIMARY BUTTON override ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1D4ED8, #7C3AED) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    box-shadow: 0 8px 24px rgba(29,78,216,0.3) !important;
    transition: all 0.2s !important;
    color: white !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 32px rgba(29,78,216,0.4) !important;
}

/* ── TABS style ── */
.stTabs [data-baseweb="tab-list"] {
    background: #F1F5F9;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    color: #64748B !important;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #1D4ED8 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
}

/* ── SLIDER ── */
.stSlider > div > div > div > div {
    background: #1D4ED8 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #F1F5F9; border-radius: 3px; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════
api_key = os.getenv("ANTHROPIC_API_KEY", "")
api_ok  = bool(api_key and api_key != "sk-ant-api03-VOTRE_CLE_ICI")

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 0.5rem;">
        <div style="font-size:2.2rem;">🎓</div>
        <div style="font-weight:800; font-size:1rem; color:#1E293B;">PrimaryTeachingSMA</div>
        <div style="font-size:0.72rem; color:#94A3B8; margin-top:0.2rem;">Système Multi-Agents v2.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Statut système
    api_dot   = "dot-green" if api_ok  else "dot-red"
    api_label = "Claude API · Connecté" if api_ok else "Claude API · Non configuré"
    st.markdown(f"""
    <div class="status-card">
        <div class="status-title">⚡ Statut Système</div>
        <div class="status-item"><div class="{api_dot}"></div>{api_label}</div>
        <div class="status-item"><div class="dot-green"></div>RAG · ChromaDB actif</div>
        <div class="status-item"><div class="dot-green"></div>Images · Pillow local</div>
        <div class="status-item"><div class="dot-blue"></div>PDF · ReportLab prêt</div>
    </div>
    """, unsafe_allow_html=True)

    # Agents
    st.markdown(f"""
    <div class="status-card">
        <div class="status-title">🤖 Agents CrewAI</div>
        <div class="agent-pill agent-1">
            <div class="agent-num num-1">1</div>
            <div>
                <div>Analyse Pédagogique</div>
                <div style="font-size:0.72rem;font-weight:400;opacity:0.7;">Profil cognitif · Règle algo</div>
            </div>
        </div>
        <div class="agent-pill agent-2">
            <div class="agent-num num-2">2</div>
            <div>
                <div>Génération Activités</div>
                <div style="font-size:0.72rem;font-weight:400;opacity:0.7;">3 activités · IF/THEN · Steps</div>
            </div>
        </div>
        <div class="agent-pill agent-3">
            <div class="agent-num num-3">3</div>
            <div>
                <div>Structuration PDF</div>
                <div style="font-size:0.72rem;font-weight:400;opacity:0.7;">Fiche finale · Trace SMA</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Pipeline
    st.markdown(f"""
    <div class="status-card">
        <div class="status-title">🔗 Pipeline</div>
        <div class="pipeline-flow">
            <span class="pipe-step">Input</span>
            <span class="pipe-arrow">→</span>
            <span class="pipe-step">RAG</span>
            <span class="pipe-arrow">→</span>
            <span class="pipe-step">Agent 1</span>
            <span class="pipe-arrow">→</span>
            <span class="pipe-step">Agent 2</span>
            <span class="pipe-arrow">→</span>
            <span class="pipe-step">Agent 3</span>
            <span class="pipe-arrow">→</span>
            <span class="pipe-step">PDF + Images</span>
        </div>
        <div style="margin-top:0.8rem; font-size:0.78rem; color:#64748B; line-height:1.6;">
            <div>📚 Embeddings · all-MiniLM-L6-v2</div>
            <div>🗄️ Vector Store · ChromaDB</div>
            <div>🎯 Top-K · 5 passages</div>
            <div>🖼️ Images · Pillow (local)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; font-size:0.72rem; color:#CBD5E1; padding-top:0.5rem;">
        Projet Universitaire — SMA 2026
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# HERO HEADER
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-title">🎓 Assistant d'Aide à l'Enseignement Primaire</div>
    <div class="hero-sub">
        Génération automatique d'activités pédagogiques ludiques · Éveil à la pensée informatique
    </div>
    <div class="hero-badges">
        <span class="badge">🤖 CrewAI · 3 Agents</span>
        <span class="badge">🧠 Claude Sonnet 4.6</span>
        <span class="badge">📚 RAG · ChromaDB</span>
        <span class="badge">🖼️ Exercices visuels</span>
        <span class="badge">📄 Export PDF</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# FORMULAIRE
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="form-card">
    <h3>📋 Paramètres de la demande pédagogique</h3>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    age = st.slider("🎂 Âge de l'enfant", min_value=5, max_value=12, value=8,
                    help="Âge de l'enfant en années")

    level_options = {
        "🌱 Maternelle (PS/MS/GS)": "Maternelle",
        "📘 CP  — 6 ans":  "CP",
        "📗 CE1 — 7 ans":  "CE1",
        "📙 CE2 — 8 ans":  "CE2",
        "📕 CM1 — 9 ans":  "CM1",
        "📒 CM2 — 10-11 ans": "CM2"
    }
    level_label = st.selectbox("🏫 Niveau scolaire", list(level_options.keys()), index=3)
    level = level_options[level_label]

    difficulty = st.select_slider(
        "📈 Niveau de difficulté",
        options=["⭐ Très facile", "⭐⭐ Facile", "⭐⭐⭐ Moyen",
                 "⭐⭐⭐⭐ Difficile", "⭐⭐⭐⭐⭐ Très difficile"],
        value="⭐⭐⭐ Moyen"
    )

with col2:
    # Activity type — visual cards via radio styled as grid
    ACT_ICONS = {
        "Logique & Raisonnement":  ("🧠", "Déduction et inférence"),
        "Suites & Patterns":       ("🔢", "Séquences numériques"),
        "Pensée Algorithmique":    ("⚙️", "Séquences et conditions"),
        "Résolution de Problèmes": ("💡", "Étapes de résolution"),
        "Puzzles & Enigmes":       ("🧩", "Déduction logique"),
        "Mini-Jeux Mathématiques": ("🎲", "Calcul ludique"),
        "Codage Débranché":        ("🤖", "Instructions séquentielles"),
    }

    st.markdown('<div class="section-label">🎮 Type d\'activité</div>', unsafe_allow_html=True)

    # Build clickable radio as visual grid via HTML + actual radio
    activity_type = st.radio(
        "Type d'activité",
        options=list(ACT_ICONS.keys()),
        index=0,
        label_visibility="collapsed",
        horizontal=False
    )

    # Show icon + description for selected
    icon, desc = ACT_ICONS[activity_type]
    st.markdown(f"""
    <div style="background:#EFF6FF; border:1.5px solid #BFDBFE; border-radius:10px;
                padding:0.6rem 0.9rem; margin-top:0.4rem; display:flex;
                align-items:center; gap:0.6rem;">
        <span style="font-size:1.4rem;">{icon}</span>
        <div>
            <div style="font-weight:700; font-size:0.85rem; color:#1D4ED8;">{activity_type}</div>
            <div style="font-size:0.75rem; color:#3B82F6;">{desc}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Objective + notes
objective = st.text_area(
    "🎯 Objectif pédagogique",
    value="Développer la pensée logique et la capacité à reconnaître des patterns simples",
    height=80,
    help="Décrivez l'objectif d'apprentissage visé"
)

special_notes = st.text_input(
    "📌 Notes spéciales (optionnel)",
    placeholder="Ex : classe multilingue, enfants dyslexiques, matériel limité..."
)
if special_notes:
    objective += f"\n\nNotes spéciales : {special_notes}"


# ══════════════════════════════════════════════════════════════════
# BOUTON GÉNÉRER
# ══════════════════════════════════════════════════════════════════
st.markdown("<div style='margin: 1.5rem 0 0.5rem;'></div>", unsafe_allow_html=True)
col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
with col_b2:
    generate_btn = st.button(
        "🚀  Générer les Activités Pédagogiques",
        use_container_width=True,
        type="primary"
    )


# ══════════════════════════════════════════════════════════════════
# WORKFLOW
# ══════════════════════════════════════════════════════════════════
if generate_btn:
    if not api_ok:
        st.error("❌ Configurez d'abord votre **ANTHROPIC_API_KEY** dans le fichier `.env`")
        st.stop()

    st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)

    # Step indicator
    step_ph = st.empty()

    def show_steps(active: int, done: list):
        steps = [
            ("1", "RAG Retrieval"),
            ("2", "Agents IA"),
            ("3", "Images"),
            ("4", "PDF"),
        ]
        circles = ""
        for i, (num, label) in enumerate(steps, 1):
            if i in done:
                cls = "done"; sym = "✓"
            elif i == active:
                cls = "active"; sym = num
            else:
                cls = ""; sym = num
            line_cls = "done" if i < len(steps) and i in done else ""
            circles += f"""
            <div class="step-item">
                <div class="step-circle {cls}">{sym}</div>
                <div class="step-label">{label}</div>
            </div>"""
            if i < len(steps):
                circles += f'<div class="step-line {line_cls}"></div>'
        step_ph.markdown(
            f'<div class="steps-row">{circles}</div>',
            unsafe_allow_html=True
        )

    show_steps(1, [])

    # Tabs résultats
    tab_logs, tab_analysis, tab_activities, tab_pdf = st.tabs([
        "🖥️ Logs",  "🔍 Analyse", "🎮 Activités", "📄 PDF"
    ])

    # Log terminal
    logs_html_lines = []
    log_ph = tab_logs.empty()

    def add_log(msg: str, level: str = "info"):
        cls_map = {"success": "log-ok", "warning": "log-warn",
                   "error": "log-err", "info": "log-info"}
        sym_map = {"success": "✓", "warning": "⚠", "error": "✗", "info": "›"}
        cls = cls_map.get(level, "log-info")
        sym = sym_map.get(level, "›")
        logs_html_lines.append(
            f'<div class="{cls}">{sym} {msg}</div>'
        )
        log_ph.markdown(
            f'<div class="log-terminal">{"".join(logs_html_lines)}</div>',
            unsafe_allow_html=True
        )

    progress_bar = st.progress(0, text="Initialisation...")

    try:
        # ── Étape 1 : RAG ─────────────────────────────────────────
        show_steps(1, [])
        progress_bar.progress(8, text="Étape 1 · RAG — Retrieval du contexte pédagogique...")
        add_log("Pipeline RAG initialisé — ChromaDB + sentence-transformers")
        add_log(f"Requête : {age} ans · {level} · {activity_type}")

        from workflow import TeachingWorkflow
        wf = TeachingWorkflow()
        wf._init_rag()
        rag_context = wf._rag.get_context_for_agent(age, level, activity_type)
        rag_chars   = len(rag_context)

        add_log(f"Contexte RAG récupéré et compressé : {rag_chars} caractères", "success")
        show_steps(2, [1])
        progress_bar.progress(25, text="Étape 2 · Agents IA — Claude Sonnet 4.6...")

        # ── Étape 2 : Agents ──────────────────────────────────────
        add_log("Agent 1 → Analyse pédagogique + règle algorithmique...")
        add_log("Agent 2 → Génération 3 activités avec IF/THEN + pseudo-code...")
        add_log("Agent 3 → Structuration PDF + trace SMA...")

        wf._init_crew()
        agent_outputs = wf._crew.run(
            age=age, level=level,
            activity_type=activity_type,
            objective=objective,
            rag_context=rag_context
        )

        analysis    = agent_outputs.get("analysis",    "")
        activities  = agent_outputs.get("activities",  "")
        pdf_content = agent_outputs.get("pdf_content", "")
        fallback    = agent_outputs.get("fallback_used", False)

        add_log(f"Agent 1 · Analyse : {len(analysis)} chars" +
                (" (fallback)" if fallback else ""), "success")
        add_log(f"Agent 2 · Activités : {len(activities)} chars", "success")
        add_log(f"Agent 3 · PDF struct : {len(pdf_content)} chars", "success")

        show_steps(3, [1, 2])
        progress_bar.progress(72, text="Étape 3 · Images — Génération exercices visuels...")

        # ── Étape 3 : Images exercices ─────────────────────────────
        add_log("Génération images d'exercices (Pillow · local · sans API)...")
        activity_images = {}
        try:
            from exercise_image_generator import generate_all_exercise_images
            output_dir = os.getenv("OUTPUT_DIR", "./outputs")
            activity_images = generate_all_exercise_images(
                activity_type=activity_type, age=age, output_dir=output_dir
            )
            n = sum(1 for v in activity_images.values() if v)
            add_log(f"{n}/3 images d'exercices générées", "success" if n == 3 else "warning")
        except Exception as e:
            add_log(f"Images ignorées : {e}", "warning")

        show_steps(4, [1, 2, 3])
        progress_bar.progress(88, text="Étape 4 · PDF — Assemblage final ReportLab...")

        # ── Étape 4 : PDF ──────────────────────────────────────────
        from pdf_generator import generate_pdf
        output_dir = os.getenv("OUTPUT_DIR", "./outputs")
        metadata   = {"age": f"{age} ans", "level": level,
                      "activity_type": activity_type, "objective": objective}

        pdf_path = generate_pdf(
            analysis=analysis or pdf_content,
            activities=activities,
            metadata=metadata,
            output_dir=output_dir,
            activity_images=activity_images
        )

        add_log(f"PDF généré → {Path(pdf_path).name}", "success")
        show_steps(4, [1, 2, 3, 4])
        progress_bar.progress(100, text="✅ Workflow terminé avec succès !")

        # ── Bannière succès ────────────────────────────────────────
        st.markdown(f"""
        <div class="success-banner">
            <div class="success-icon">🎉</div>
            <div class="success-text">
                <h4>Activités générées avec succès !</h4>
                <p>3 activités pédagogiques · {rag_chars} chars RAG · images d'exercices · PDF prêt</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Métriques
        st.markdown(f"""
        <div class="metrics-row">
            <div class="metric-chip">
                <div class="metric-val">{age}</div>
                <div class="metric-lbl">Âge</div>
            </div>
            <div class="metric-chip">
                <div class="metric-val">{level}</div>
                <div class="metric-lbl">Niveau</div>
            </div>
            <div class="metric-chip">
                <div class="metric-val">3</div>
                <div class="metric-lbl">Activités</div>
            </div>
            <div class="metric-chip">
                <div class="metric-val">{rag_chars}</div>
                <div class="metric-lbl">Chars RAG</div>
            </div>
            <div class="metric-chip">
                <div class="metric-val">{"✓" if not fallback else "FB"}</div>
                <div class="metric-lbl">{"IA live" if not fallback else "Fallback"}</div>
            </div>
            <div class="metric-chip">
                <div class="metric-val">{sum(1 for v in activity_images.values() if v)}/3</div>
                <div class="metric-lbl">Images</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Onglets résultats ──────────────────────────────────────
        with tab_analysis:
            st.markdown("""
            <div class="result-card">
                <h4>🔍 Agent 1 — Analyse Pédagogique</h4>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(analysis or "*Aucune analyse disponible*")

        with tab_activities:
            st.markdown("""
            <div class="result-card">
                <h4>🎮 Agent 2 — Activités Générées</h4>
            </div>
            """, unsafe_allow_html=True)
            # Afficher les images d'exercices avec les activités
            for idx in range(1, 4):
                img_path = activity_images.get(idx)
                if img_path and Path(img_path).exists():
                    st.image(img_path,
                             caption=f"Exercice visuel — Activité {idx}",
                             use_container_width=True)
            st.markdown(activities or "*Aucune activité disponible*")

        with tab_pdf:
            st.markdown("""
            <div class="result-card">
                <h4>📄 Agent 3 — Fiche Structurée</h4>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(pdf_content or "*Aucun contenu structuré*")
            st.divider()

            pdf_file = Path(pdf_path)
            if pdf_file.exists():
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="📥  Télécharger la Fiche PDF Illustrée",
                        data=f.read(),
                        file_name=pdf_file.name,
                        mime="application/pdf",
                        use_container_width=True
                    )

    except Exception as e:
        progress_bar.progress(0, text="❌ Erreur")
        add_log(f"ERREUR : {e}", "error")
        st.error(f"**Erreur :** {e}")
        with st.expander("📋 Traceback complet"):
            import traceback
            st.code(traceback.format_exc())


# ══════════════════════════════════════════════════════════════════
# FOOTER INFO
# ══════════════════════════════════════════════════════════════════
st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
with st.expander("ℹ️ Architecture du Système Multi-Agents"):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        **🤖 Agents CrewAI**
        - Agent 1 · Analyse pédagogique + règle algo
        - Agent 2 · 3 activités IF/THEN + pseudo-code
        - Agent 3 · Structuration + trace SMA
        - Process : **Sequential**
        """)
    with c2:
        st.markdown("""
        **📚 RAG Pipeline**
        - Embeddings : all-MiniLM-L6-v2
        - Vector store : ChromaDB
        - Chunking : **adaptatif** (frontières de phrases)
        - Compression : déduplication >85%
        - Top-K : 5 passages
        """)
    with c3:
        st.markdown("""
        **🖼️ Exercices Visuels**
        - Suites numériques avec terme manquant
        - Patterns de formes colorées
        - Grilles robot débranché
        - **100% local · Pillow · sans API**
        - Adapté à l'âge (5-7 / 8-9 / 10-12 ans)
        """)
