"""
agents.py - Définition des 3 agents CrewAI du système PrimaryTeachingSMA.

Architecture :
  Agent 1 : Analyse Pédagogique  → analyse l'input utilisateur
  Agent 2 : Génération Activités → crée les activités ludiques
  Agent 3 : PDF                  → structure le contenu final

Améliorations v2 :
  - Structured logging via logger.py [AGENT-X][STEP]
  - Fallback safe outputs quand l'API échoue
  - Validation des outputs avant de les transmettre au prochain agent
"""

import os
from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process, LLM

from logger import get_logger, log_agent

load_dotenv()
logger = get_logger(__name__)

# ── Fallback outputs (retournés si l'API est indisponible) ─────────────────────

_FALLBACK_ANALYSIS = """
[AGENT 1 — ANALYSE PÉDAGOGIQUE]
- Âge : 8 ans | Niveau : CE2
- Type : Logique & Raisonnement
- Objectif : Développer la pensée logique et la reconnaissance de patterns

PROFIL COGNITIF
- Stade Piaget : Opératoire concret (7-11 ans)
- Durée attention : 10-15 minutes
- Mode d'apprentissage dominant : visuel et kinesthésique

COMPÉTENCES ALGORITHMIQUES CIBLÉES
- Compétence 1 : Reconnaissance de patterns — identifier une règle de répétition
- Compétence 2 : Séquençage — ordonner des étapes logiques
- Compétence 3 : Déduction — trouver le terme manquant par inférence

RÈGLE ALGORITHMIQUE PRINCIPALE
- Type : pattern / séquence
- Structure : SI terme(N) suit terme(N-1) par règle R ALORS terme(N+1) = terme(N) + R
- Exemple adapté à 8 ans : 2, 4, 6, ? → règle = +2 → réponse = 8

RECOMMANDATIONS POUR L'AGENT 2
- Format activité conseillé : manipulation de cartes ou tableau blanc
- Complexité max : séquences de 5 termes, règle unique
- Matériel préférentiel : cartes numérotées, feutres de couleur
- Points d'attention : partir toujours d'un exemple concret avant l'abstraction

[RAG INFLUENCE SUR L'ANALYSE]
- Contexte utilisé : oui (ressources embarquées)
- Résumé de l'influence : recommandation d'utiliser des suites visuelles pour 8-10 ans
""".strip()

_FALLBACK_ACTIVITIES = """
## ACTIVITÉ 1 : La Machine à Règles

**1. Objectif**
Identifier et appliquer une règle de transformation pour compléter une suite numérique.

**2. Règle algorithmique**
- Règle : ajouter un nombre fixe N à chaque terme
- Type : pattern / séquence arithmétique
- Logique : SI terme(i) est connu ET règle = +N ALORS terme(i+1) = terme(i) + N
- Pseudo-code :
  terme_actuel = premier terme
  RÉPÉTER : terme_suivant = terme_actuel + N
  JUSQU'À : terme manquant trouvé

**3. Matériel**
- Tableau blanc ou feuille de papier
- Marqueurs de 2 couleurs (connu / inconnu)

**4. Étapes**
1. L'enseignant écrit une suite avec un terme manquant : 3, 6, 9, ?, 15
2. L'élève calcule la différence entre deux termes consécutifs : 6-3=3, 9-6=3
3. L'élève identifie la règle : +3
4. L'élève complète la suite : ? = 9+3 = 12

**5. Exemple résolu**
- Input : 2, 5, 8, ?, 14
- Raisonnement : 5-2=3 ✓ | 8-5=3 ✓ | règle = +3 | ? = 8+3
- Output : ? = 11

**6. Correction**
- Réponse correcte : 11
- Erreur fréquente : compter +3 depuis le premier terme au lieu du précédent
- Pourquoi c'est faux : la règle s'applique terme à terme, pas depuis le début

**7. Variations**
- Plus facile : suite +2 avec seulement 4 termes, terme manquant en dernière position
- Plus difficile : suite +5 avec deux termes manquants, ou règle ×2

**8. [RAG CONTEXT UTILISÉ]**
- Source : ressource embarquée "suites numériques 8-10 ans"
- Application : suites arithmétiques simples recommandées pour CE2

---

## ACTIVITÉ 2 : Le Détective des Patterns

**1. Objectif**
Reconnaître un motif visuel répété et prédire le prochain élément de la séquence.

**2. Règle algorithmique**
- Règle : une séquence de 2 éléments se répète en boucle
- Type : boucle / répétition cyclique
- Logique : SI position(i) mod longueur_cycle = k ALORS élément(i) = motif[k]
- Pseudo-code :
  cycle = [élément_A, élément_B]
  POUR chaque position : afficher cycle[position mod 2]

**3. Matériel**
- Cartes illustrées (formes colorées) ou dessin au tableau
- Cartes blanches pour la réponse

**4. Étapes**
1. Afficher une séquence de 6 cartes avec un terme caché : ● ■ ● ■ ● ?
2. L'élève identifie les éléments qui alternent : rond / carré
3. L'élève détermine la longueur du cycle : 2
4. L'élève prédit le terme caché en appliquant le cycle

**5. Exemple résolu**
- Input : 🔴 🔵 🔴 🔵 🔴 ?
- Raisonnement : cycle = [rouge, bleu], longueur = 2, position 6 → 6 mod 2 = 0 → rouge
- Output : ? = 🔴

**6. Correction**
- Réponse correcte : 🔴 (rouge)
- Erreur fréquente : donner le dernier élément vu sans appliquer le cycle
- Pourquoi c'est faux : il faut lire le pattern global, pas seulement le dernier terme

**7. Variations**
- Plus facile : cycle de 2 avec seulement des couleurs (rouge/bleu)
- Plus difficile : cycle de 3 éléments (forme + couleur + taille)

**8. [RAG CONTEXT UTILISÉ]**
- Source : ressource embarquée "activités logique 5-7 ans / 8-10 ans"
- Application : activité de patterns visuels adaptée au niveau CE2

---

## ACTIVITÉ 3 : Le Robot Débranché

**1. Objectif**
Formuler et suivre des instructions séquentielles précises — introduction à la programmation débranchée.

**2. Règle algorithmique**
- Règle : une séquence d'instructions s'exécute dans l'ordre, sans interprétation
- Type : séquence d'instructions / algorithme
- Logique : POUR chaque instruction dans la liste : exécuter l'instruction dans l'ordre
- Pseudo-code :
  instructions = [avance(3), tourne_droite, avance(2), stop]
  POUR chaque instruction : robot.executer(instruction)

**3. Matériel**
- Espace de jeu dégagé (couloir ou cour)
- Obstacles (chaises, livres posés au sol)
- Cartes instructions pré-écrites (optionnel)

**4. Étapes**
1. Définir la position de départ du "robot" et la cible à atteindre
2. Le programmeur écrit ou dit les instructions une par une
3. Le robot exécute chaque instruction EXACTEMENT (pas d'interprétation)
4. Vérifier si la cible est atteinte sans toucher un obstacle
5. Si échec : identifier l'instruction incorrecte et corriger (débogage)

**5. Exemple résolu**
- Input : départ = A, cible = B, obstacles = [colonne1, colonne2]
- Instructions : "Avance 3 pas → tourne à droite → avance 2 pas → stop"
- Raisonnement : vérifier pas à pas que chaque instruction évite les obstacles
- Output : robot en position B ✓

**6. Correction**
- Réponse correcte : séquence qui amène le robot à la cible sans collision
- Erreur fréquente : donner une instruction ambiguë ("va là-bas") au lieu de précise
- Pourquoi c'est faux : un algorithme exige des instructions non ambiguës et mesurables

**7. Variations**
- Plus facile : parcours en ligne droite, 3 instructions seulement
- Plus difficile : ajouter une condition SI obstacle ALORS contourner

**8. [RAG CONTEXT UTILISÉ]**
- Source : ressource embarquée "pensée algorithmique 10-12 ans"
- Application : activité de codage débranché adaptée en version simplifiée pour CE2
""".strip()

_FALLBACK_PDF_CONTENT = """
[PIPELINE SMA — TRACE D'EXÉCUTION]
- Agent 1 (Analyse Pédagogique) : profil cognitif CE2 + règle algorithmique pattern/séquence
- Agent 2 (Génération Activités) : 3 activités avec pensée algorithmique (fallback)
- Agent 3 (Structuration PDF) : assemblage et formatage final
- RAG Pipeline : contexte pédagogique embarqué injecté (ressources par défaut)

## ANALYSE PÉDAGOGIQUE
- Stade Piaget : opératoire concret — manipulation avant abstraction
- Compétences ciblées : reconnaissance de patterns, séquençage, déduction
- Règle algorithmique : SI terme(N) suit terme(N-1) par règle R ALORS terme(N+1) = terme(N) + R
- Durée attention max : 10-15 min par activité

## ACTIVITÉ 1 : La Machine à Règles

**1. Objectif**
Identifier et appliquer une règle de transformation pour compléter une suite numérique.

**2. Règle algorithmique**
- Règle : ajouter N fixe à chaque terme
- Logique : SI terme(i) connu ET règle = +N ALORS terme(i+1) = terme(i) + N
- Pseudo-code : RÉPÉTER terme += N JUSQU'À terme manquant trouvé

**3. Matériel** — Tableau blanc, marqueurs 2 couleurs

**4. Étapes**
1. Écrire la suite avec terme manquant : 3, 6, 9, ?, 15
2. Calculer différence entre termes consécutifs : 6-3=3
3. Identifier la règle : +3
4. Compléter : ? = 9+3 = 12

**5. Exemple résolu**
- Input : 2, 5, 8, ?, 14
- Raisonnement : différence = 3 → règle = +3 → ? = 8+3
- Output : 11

**6. Correction**
- Réponse correcte : 11
- Erreur fréquente : compter depuis le premier terme

**7. Variations**
- Facile : suite +2, terme en dernière position | Difficile : deux termes manquants

**8. [RAG CONTEXT UTILISÉ]**
- Source : ressource embarquée "suites numériques 8-10 ans"
- Application : suites arithmétiques recommandées CE2

---

## ACTIVITÉ 2 : Le Détective des Patterns

**1. Objectif**
Reconnaître un motif visuel répété et prédire le prochain élément.

**2. Règle algorithmique**
- Règle : cycle de 2 éléments en répétition
- Logique : SI position mod 2 = 0 ALORS élément_A SINON élément_B
- Pseudo-code : POUR chaque position : afficher cycle[position mod longueur]

**3. Matériel** — Cartes illustrées, formes colorées

**4. Étapes**
1. Afficher 6 cartes avec terme caché : ● ■ ● ■ ● ?
2. Identifier les 2 éléments alternants
3. Déterminer la longueur du cycle : 2
4. Appliquer : position 6, 6 mod 2 = 0 → premier élément

**5. Exemple résolu**
- Input : 🔴 🔵 🔴 🔵 🔴 ?
- Raisonnement : cycle [rouge, bleu], position 6 → rouge
- Output : 🔴

**6. Correction**
- Réponse correcte : rouge
- Erreur fréquente : donner le dernier élément vu sans appliquer le cycle

**7. Variations**
- Facile : 2 couleurs seulement | Difficile : cycle de 3 (forme + couleur + taille)

**8. [RAG CONTEXT UTILISÉ]**
- Source : ressource embarquée "patterns visuels 5-7 ans"
- Application : adapté en niveau CE2 avec cycle à 2 éléments

---

## ACTIVITÉ 3 : Le Robot Débranché

**1. Objectif**
Formuler des instructions séquentielles précises — introduction à la programmation débranchée.

**2. Règle algorithmique**
- Règle : séquence d'instructions exécutée dans l'ordre strict
- Logique : POUR chaque instruction dans liste : exécuter sans interprétation
- Pseudo-code : instructions = [avance(3), tourne_droite, avance(2), stop]

**3. Matériel** — Espace dégagé, obstacles (chaises)

**4. Étapes**
1. Définir départ, cible, obstacles
2. Le programmeur dicte les instructions une par une
3. Le robot exécute exactement chaque ordre
4. Vérifier arrivée à la cible
5. Si échec : identifier l'instruction fausse (débogage)

**5. Exemple résolu**
- Input : départ=A, cible=B, obstacle=milieu
- Instructions : avance 3, tourne droite, avance 2, stop
- Output : robot en B ✓

**6. Correction**
- Réponse correcte : séquence sans collision atteignant la cible
- Erreur fréquente : instruction ambiguë "va là-bas"

**7. Variations**
- Facile : ligne droite, 3 instructions | Difficile : condition SI obstacle ALORS contourner

**8. [RAG CONTEXT UTILISÉ]**
- Source : ressource embarquée "codage débranché 10-12 ans"
- Application : version simplifiée pour CE2

## CONSEILS POUR L'INSTITUTEUR
- Conseil 1 : toujours démontrer la règle algorithmique avant de lancer l'activité
- Conseil 2 : encourager la verbalisation du raisonnement ("je fais +3 parce que...")
- Conseil 3 : proposer la variante facile aux élèves en difficulté sans les exclure du groupe
""".strip()


# ── LLM Configuration ──────────────────────────────────────────────────────────

def get_llm() -> LLM:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    model   = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
    max_tok = int(os.getenv("MAX_TOKENS_PER_AGENT", "1500"))

    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY manquante dans .env")

    log_agent(logger, "SYSTEM", "CONFIG",
              f"LLM initialisé : modèle={model}, max_tokens={max_tok}")

    return LLM(
        model=f"anthropic/{model}",
        api_key=api_key,
        max_tokens=max_tok,
        temperature=0.7
    )


# ── Agent 1 : Analyse Pédagogique ─────────────────────────────────────────────

def create_analysis_agent(llm: LLM) -> Agent:
    log_agent(logger, "AGENT-1", "INIT", "Création de l'Agent Analyse Pédagogique")
    return Agent(
        role="Expert en Analyse Pédagogique et Pensée Algorithmique",
        goal=(
            "Produire une analyse pédagogique structurée qui identifie explicitement "
            "les règles algorithmiques sous-jacentes à l'activité demandée : "
            "compétences cognitives ciblées, niveau de raisonnement logique attendu, "
            "et structure IF/THEN applicable à l'âge de l'enfant."
        ),
        backstory=(
            "Expert en sciences de l'éducation et en pensée computationnelle pour le primaire. "
            "Formé aux théories de Piaget et aux curricula d'informatique débranchée (CSTA K-12). "
            "Identifie systématiquement la règle algorithmique derrière chaque objectif pédagogique "
            "pour guider la génération d'activités logiques et structurées."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3
    )


# ── Agent 2 : Génération Activités ────────────────────────────────────────────

def create_activity_agent(llm: LLM) -> Agent:
    log_agent(logger, "AGENT-2", "INIT", "Création de l'Agent Génération Activités")
    return Agent(
        role="Concepteur d'Activités à Pensée Algorithmique",
        goal=(
            "Générer 3 activités pédagogiques COMPLÈTES dont chacune expose explicitement "
            "une règle algorithmique (IF/THEN, boucle, séquence), des étapes numérotées, "
            "un exemple résolu pas-à-pas, une section correction et deux variations. "
            "Chaque activité doit être entièrement rédigée sans abréviation ni troncature."
        ),
        backstory=(
            "Ingénieur pédagogique spécialisé en informatique débranchée et pensée computationnelle "
            "pour les 5-12 ans. Conçoit des activités qui rendent visible la logique algorithmique "
            "sans ordinateur : séquences, conditions, boucles, patterns. "
            "Chaque activité suit un format fixe en 8 sections pour garantir la complétude "
            "et la traçabilité pédagogique."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3
    )


# ── Agent 3 : Structuration PDF ───────────────────────────────────────────────

def create_pdf_agent(llm: LLM) -> Agent:
    log_agent(logger, "AGENT-3", "INIT", "Création de l'Agent Structuration PDF")
    return Agent(
        role="Ingénieur de Documentation Pédagogique SMA",
        goal=(
            "Assembler la fiche pédagogique finale en préservant INTÉGRALEMENT les 8 sections "
            "de chaque activité, en ajoutant la trace du pipeline SMA (contributions de chaque agent) "
            "et en formatant pour une lisibilité maximale en classe."
        ),
        backstory=(
            "Spécialiste en documentation technique et pédagogique. Veille à la traçabilité "
            "des systèmes multi-agents : chaque fiche doit indiquer quelle section a été produite "
            "par quel agent. Garantit qu'aucune activité n'est tronquée ou résumée — "
            "toutes les 8 sections de chaque activité apparaissent dans le document final."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=2
    )


# ── Tâches ────────────────────────────────────────────────────────────────────

def create_analysis_task(agent: Agent, age: int, level: str,
                          activity_type: str, objective: str,
                          rag_context: str) -> Task:
    rag_block = (
        f"\nRAG CONTEXT RETRIEVED:\n---\n{rag_context}\n---\n"
        if rag_context else "\nRAG CONTEXT: aucune ressource externe disponible.\n"
    )

    return Task(
        description=(
            f"Tu es l'AGENT 1 d'un système multi-agents. Produis une analyse pédagogique "
            f"structurée avec identification explicite de la pensée algorithmique.\n\n"
            f"PARAMÈTRES REÇUS :\n"
            f"- Âge : {age} ans\n"
            f"- Niveau : {level}\n"
            f"- Type d'activité : {activity_type}\n"
            f"- Objectif : {objective}\n"
            f"{rag_block}\n"
            f"FORMAT DE SORTIE OBLIGATOIRE — respecte exactement ce bloc :\n\n"
            f"[AGENT 1 — ANALYSE PÉDAGOGIQUE]\n"
            f"- Âge : {age} ans | Niveau : {level}\n"
            f"- Type : {activity_type}\n"
            f"- Objectif : {objective}\n\n"
            f"PROFIL COGNITIF\n"
            f"- Stade Piaget : [stade exact]\n"
            f"- Durée attention : [durée en minutes]\n"
            f"- Mode d'apprentissage dominant : [visuel/kinesthésique/auditif]\n\n"
            f"COMPÉTENCES ALGORITHMIQUES CIBLÉES\n"
            f"- Compétence 1 : [nom] — description courte\n"
            f"- Compétence 2 : [nom] — description courte\n"
            f"- Compétence 3 : [nom] — description courte\n\n"
            f"RÈGLE ALGORITHMIQUE PRINCIPALE\n"
            f"- Type : [séquence / condition / boucle / pattern]\n"
            f"- Structure : SI [condition] ALORS [action] SINON [alternative]\n"
            f"- Exemple adapté à {age} ans : [exemple concret]\n\n"
            f"RECOMMANDATIONS POUR L'AGENT 2\n"
            f"- Format activité conseillé : [format]\n"
            f"- Complexité max : [niveau]\n"
            f"- Matériel préférentiel : [matériel]\n"
            f"- Points d'attention : [points]\n\n"
            f"[RAG INFLUENCE SUR L'ANALYSE]\n"
            f"- Contexte utilisé : [oui/non]\n"
            f"- Résumé de l'influence : [1-2 phrases]\n"
        ),
        agent=agent,
        expected_output=(
            "Bloc [AGENT 1 — ANALYSE PÉDAGOGIQUE] complet avec toutes les sections, "
            "incluant règle algorithmique et recommandations pour l'Agent 2."
        )
    )


def create_activity_task(agent: Agent, age: int, level: str,
                          activity_type: str, objective: str,
                          analysis_context: str, rag_context: str) -> Task:
    rag_block = (
        f"\nRAG CONTEXT RETRIEVED:\n---\n{rag_context}\n---\n"
        if rag_context else "\nRAG CONTEXT: aucune ressource externe.\n"
    )

    return Task(
        description=(
            f"Tu es l'AGENT 2 d'un système multi-agents. Tu reçois l'analyse de l'Agent 1 "
            f"et génères EXACTEMENT 3 activités pédagogiques COMPLÈTES.\n\n"
            f"ANALYSE REÇUE DE L'AGENT 1 :\n{analysis_context}\n"
            f"{rag_block}\n"
            f"PARAMÈTRES : âge={age} ans | niveau={level} | type={activity_type}\n\n"
            f"RÈGLE ABSOLUE : chaque activité DOIT contenir les 8 sections ci-dessous. "
            f"Ne jamais abréger, ne jamais écrire '[même structure]'. "
            f"Rédiger intégralement les 3 activités.\n\n"
            f"FORMAT OBLIGATOIRE POUR CHAQUE ACTIVITÉ :\n\n"
            f"## ACTIVITÉ N : [Titre accrocheur]\n\n"
            f"**1. Objectif**\n"
            f"[1 phrase claire — compétence visée]\n\n"
            f"**2. Règle algorithmique**\n"
            f"- Règle : [la règle en une ligne]\n"
            f"- Type : [séquence / condition IF-THEN / boucle / pattern]\n"
            f"- Logique : SI [condition] ALORS [action] SINON [alternative]\n"
            f"- Pseudo-code : [2-3 lignes style pseudo-code simple]\n\n"
            f"**3. Matériel**\n"
            f"[liste courte]\n\n"
            f"**4. Étapes**\n"
            f"1. [étape 1]\n2. [étape 2]\n3. [étape 3]\n4. [étape 4]\n\n"
            f"**5. Exemple résolu**\n"
            f"- Input : [données de départ]\n"
            f"- Raisonnement : [explication étape par étape]\n"
            f"- Output : [réponse finale]\n\n"
            f"**6. Correction**\n"
            f"- Réponse correcte : [réponse]\n"
            f"- Erreur fréquente : [erreur typique à {age} ans]\n"
            f"- Pourquoi c'est faux : [explication courte]\n\n"
            f"**7. Variations**\n"
            f"- Plus facile : [description]\n"
            f"- Plus difficile : [description]\n\n"
            f"**8. [RAG CONTEXT UTILISÉ]**\n"
            f"- Source : [nom de la ressource ou 'ressource embarquée']\n"
            f"- Application : [comment le contexte a influencé cette activité]\n\n"
            f"---\n\n"
            f"Génère maintenant les 3 activités complètes. Durée totale : 10-15 min chacune."
        ),
        agent=agent,
        expected_output=(
            "3 activités pédagogiques COMPLÈTES, chacune avec les 8 sections intégralement rédigées, "
            "incluant règle algorithmique IF/THEN, exemple résolu et section RAG context."
        )
    )


def create_pdf_task(agent: Agent, analysis: str, activities: str,
                    age: int, level: str) -> Task:
    return Task(
        description=(
            f"Tu es l'AGENT 3 d'un système multi-agents. Tu assembles la fiche finale.\n\n"
            f"CONTENU REÇU DE L'AGENT 1 :\n{analysis}\n\n"
            f"CONTENU REÇU DE L'AGENT 2 :\n{activities}\n\n"
            f"RÈGLES D'ASSEMBLAGE :\n"
            f"1. NE PAS résumer ni tronquer — copier le contenu complet des agents 1 et 2\n"
            f"2. NE PAS écrire '[même structure]' — rédiger chaque section intégralement\n"
            f"3. Ajouter la trace SMA en tête de document\n"
            f"4. Ajouter les conseils instituteur en fin de document\n\n"
            f"FORMAT FINAL OBLIGATOIRE :\n\n"
            f"[PIPELINE SMA — TRACE D'EXÉCUTION]\n"
            f"- Agent 1 (Analyse Pédagogique) : profil cognitif + règle algorithmique identifiée\n"
            f"- Agent 2 (Génération Activités) : 3 activités avec pensée algorithmique\n"
            f"- Agent 3 (Structuration PDF) : assemblage et formatage final\n"
            f"- RAG Pipeline : contexte pédagogique injecté dans Agents 1 et 2\n\n"
            f"## ANALYSE PÉDAGOGIQUE\n"
            f"[reprendre les points clés de l'Agent 1 — profil, compétences, règle algo]\n\n"
            f"## ACTIVITÉ 1 : [Titre]\n"
            f"[reprendre intégralement les 8 sections de l'Agent 2]\n\n"
            f"## ACTIVITÉ 2 : [Titre]\n"
            f"[reprendre intégralement les 8 sections de l'Agent 2]\n\n"
            f"## ACTIVITÉ 3 : [Titre]\n"
            f"[reprendre intégralement les 8 sections de l'Agent 2]\n\n"
            f"## CONSEILS POUR L'INSTITUTEUR\n"
            f"- Conseil 1 : [conseil pratique adapté à {age} ans, {level}]\n"
            f"- Conseil 2 : [conseil sur la gestion de classe]\n"
            f"- Conseil 3 : [conseil sur l'adaptation aux élèves en difficulté]\n"
        ),
        agent=agent,
        expected_output=(
            "Fiche complète avec trace SMA en en-tête, 3 activités intégralement retranscrites "
            "avec leurs 8 sections, et conseils instituteur. Aucune troncature."
        )
    )


# ── Crew Orchestrator ─────────────────────────────────────────────────────────

class TeachingCrew:
    """
    Orchestre les 3 agents en séquence (Process.sequential).
    Fallback safe : retourne les outputs par défaut si l'API échoue.
    """

    def __init__(self):
        log_agent(logger, "SYSTEM", "INIT", "Initialisation du Crew multi-agents...")
        try:
            self.llm            = get_llm()
            self.analysis_agent = create_analysis_agent(self.llm)
            self.activity_agent = create_activity_agent(self.llm)
            self.pdf_agent      = create_pdf_agent(self.llm)
            log_agent(logger, "SYSTEM", "INIT", "3 agents CrewAI prêts")
        except Exception as e:
            log_agent(logger, "SYSTEM", "ERROR",
                      f"Initialisation du Crew échouée : {e}", level="error")
            raise

    def run(self, age: int, level: str, activity_type: str,
            objective: str, rag_context: str = "") -> dict:
        """
        Lance le workflow multi-agents complet.
        Retourne un dict avec les outputs de chaque agent.
        En cas d'échec API, retourne les fallback outputs.
        """
        log_agent(logger, "SYSTEM", "START",
                  f"Démarrage Crew — age={age}, level={level}, type={activity_type}")

        try:
            task1 = create_analysis_task(
                self.analysis_agent, age, level, activity_type, objective, rag_context
            )
            task2 = create_activity_task(
                self.activity_agent, age, level, activity_type, objective,
                analysis_context="[voir tâche précédente]", rag_context=rag_context
            )
            task3 = create_pdf_task(
                self.pdf_agent,
                analysis="[voir tâche 1]",
                activities="[voir tâche 2]",
                age=age,
                level=level
            )

            crew = Crew(
                agents=[self.analysis_agent, self.activity_agent, self.pdf_agent],
                tasks=[task1, task2, task3],
                process=Process.sequential,
                verbose=True
            )

            log_agent(logger, "AGENT-1", "ANALYSIS",
                      f"Lancement analyse pédagogique — {age} ans, {level}")
            result = crew.kickoff()
            log_agent(logger, "SYSTEM", "COMPLETE", "Crew terminé avec succès")

            analysis    = str(task1.output.raw) if task1.output else ""
            activities  = str(task2.output.raw) if task2.output else ""
            pdf_content = str(task3.output.raw) if task3.output else ""

            # Validation : utiliser fallback si un output est vide
            if not analysis.strip():
                log_agent(logger, "AGENT-1", "FALLBACK",
                          "Output vide — utilisation du fallback analyse", level="warning")
                analysis = _FALLBACK_ANALYSIS

            if not activities.strip():
                log_agent(logger, "AGENT-2", "FALLBACK",
                          "Output vide — utilisation du fallback activités", level="warning")
                activities = _FALLBACK_ACTIVITIES

            if not pdf_content.strip():
                log_agent(logger, "AGENT-3", "FALLBACK",
                          "Output vide — utilisation du fallback PDF", level="warning")
                pdf_content = _FALLBACK_PDF_CONTENT

            log_agent(logger, "AGENT-1", "COMPLETE",
                      f"Analyse : {len(analysis)} caractères")
            log_agent(logger, "AGENT-2", "COMPLETE",
                      f"Activités : {len(activities)} caractères")
            log_agent(logger, "AGENT-3", "COMPLETE",
                      f"Contenu PDF : {len(pdf_content)} caractères")

            return {
                "analysis":    analysis,
                "activities":  activities,
                "pdf_content": pdf_content,
                "final":       str(result),
                "fallback_used": False
            }

        except Exception as e:
            log_agent(logger, "SYSTEM", "ERROR",
                      f"Crew échoué : {e} — fallback complet activé", level="error")
            return {
                "analysis":    _FALLBACK_ANALYSIS,
                "activities":  _FALLBACK_ACTIVITIES,
                "pdf_content": _FALLBACK_PDF_CONTENT,
                "final":       "Fallback — API indisponible",
                "fallback_used": True,
                "error": str(e)
            }
