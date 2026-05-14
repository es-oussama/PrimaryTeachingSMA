# Script de Démonstration — PrimaryTeachingSMA
## Guide vidéo étape par étape

---

## Informations générales

**Durée estimée de la démo :** 3 à 5 minutes  
**Objectif :** Montrer le fonctionnement complet du système, de la saisie utilisateur au PDF généré.  
**Public :** Jury universitaire, enseignants, développeurs.

---

## Avant de commencer

Vérifier que :
- [ ] L'environnement virtuel est activé (`.\venv\Scripts\Activate.ps1`)
- [ ] Le fichier `.env` contient une clé API valide
- [ ] Le terminal est positionné dans `d:\PrimaryTeachingSMA\Source`
- [ ] Aucune autre instance Streamlit ne tourne

Lancer le serveur :
```powershell
streamlit run app.py
```
Ouvrir `http://localhost:8501` dans le navigateur.

---

## Scène 1 — Présentation de l'interface (30 secondes)

**Action :** Montrer la page d'accueil Streamlit.

**À dire :**
> "Voici l'interface de notre Système Multi-Agents. À gauche, la barre latérale confirme que l'API Claude est configurée et liste nos 3 agents actifs. Au centre, le formulaire de demande pédagogique."

**Points à montrer :**
- Le bandeau bleu avec le titre
- La sidebar : statut API vert, les 3 agents, la configuration RAG
- Le formulaire vide

---

## Scène 2 — Saisie des paramètres (45 secondes)

**Action :** Remplir le formulaire avec ces valeurs exactes :

| Champ | Valeur à saisir |
|-------|-----------------|
| Âge de l'enfant | **8 ans** (slider) |
| Niveau scolaire | **CE2 (8 ans)** |
| Type d'activité | **Logique & Raisonnement** |
| Niveau de difficulté | **Moyen** |
| Objectif pédagogique | *laisser la valeur par défaut* |
| Notes spéciales | *(laisser vide)* |

**À dire :**
> "Je simule la demande d'un instituteur de CE2. Son élève a 8 ans, et il souhaite créer une activité de logique de niveau moyen pour développer la pensée logique."

---

## Scène 3 — Lancement du workflow (10 secondes)

**Action :** Cliquer sur le bouton "Générer les Activités Pédagogiques".

**À dire :**
> "Je clique sur Générer. Le workflow multi-agents se lance."

---

## Scène 4 — Exécution en temps réel (60 à 90 secondes)

**Action :** Laisser tourner et commenter ce qui s'affiche.

**Commenter au fur et à mesure :**

Lorsque la barre de progression atteint 25% :
> "L'étape 1 est terminée. Le pipeline RAG a récupéré le contexte pédagogique depuis ChromaDB et l'a compressé pour l'injecter dans les agents."

Lorsque les logs montrent l'Agent 1 :
> "L'Agent 1 — Expert en Analyse Pédagogique — est en train d'analyser le profil cognitif de l'enfant de 8 ans. Il s'appuie sur les théories de Piaget."

Lorsque les logs montrent l'Agent 2 :
> "L'Agent 2 prend le relais. Il reçoit l'analyse de l'Agent 1 et génère 3 activités ludiques adaptées au CE2."

Lorsque les logs montrent l'Agent 3 :
> "L'Agent 3 structure le tout en fiche pédagogique, prête à être convertie en PDF."

Lorsque la barre atteint 100% :
> "Workflow terminé. Regardons les résultats."

---

## Scène 5 — Exploration des résultats (60 secondes)

**Action :** Naviguer entre les onglets de résultats.

### Onglet "Logs Agents"

**Montrer les logs structurés.**

**À dire :**
> "Ici les logs structurés de chaque agent. On voit le format : timestamp, nom de l'agent, étape, message. Chaque action est tracée."

Pointer un exemple comme :
```
[2026-05-14 10:32:05][AGENT-1][ANALYSIS] Lancement analyse — 8 ans, CE2
```

### Onglet "Analyse"

**À dire :**
> "L'Agent 1 a produit une analyse en 5 sections : profil cognitif, compétences ciblées, niveau de difficulté, recommandations et points d'attention. Cette analyse est basée sur les théories pédagogiques réelles."

### Onglet "Activités"

**À dire :**
> "L'Agent 2 a généré 3 activités complètes. Chacune a un titre, une description, le matériel nécessaire, les instructions étape par étape, un exemple concret et la durée. Ce sont des activités directement utilisables en classe."

### Onglet "PDF"

**À dire :**
> "L'Agent 3 a structuré tout le contenu en sections claires, avec les en-têtes markdown prêts pour ReportLab."

---

## Scène 6 — Téléchargement du PDF (20 secondes)

**Action :** Cliquer sur le bouton "Télécharger la Fiche PDF" et ouvrir le fichier.

**À dire :**
> "Je télécharge la fiche PDF finale. Elle contient l'en-tête institutionnel, les informations de contexte, l'analyse pédagogique et les 3 activités mises en forme professionnellement."

**Montrer le PDF ouvert avec :**
- Le bandeau bleu en-tête
- Le tableau de métadonnées (âge, niveau, objectif)
- La section Analyse Pédagogique
- Les 3 activités numérotées
- Le pied de page

---

## Scène 7 — Logs et trace d'exécution (30 secondes)

**Action :** Ouvrir dans un éditeur (VS Code ou Notepad) :
- `Source/outputs/agents.log`
- `Learning_Log/execution_trace.txt`

**Pour `agents.log` :**

**À dire :**
> "Le fichier de log machine enregistre chaque action avec le format structuré. Il est persistant entre les sessions."

**Pour `execution_trace.txt` :**

**À dire :**
> "La trace d'exécution est un document humainement lisible. Elle enregistre les paramètres d'entrée, chaque étape du pipeline, et le résumé final avec la durée totale et le chemin du PDF."

---

## Scène 8 (optionnelle) — Test du fallback (30 secondes)

*Uniquement si vous voulez montrer la robustesse du système.*

**Action :** Ouvrir `.env`, mettre une fausse clé API, relancer une génération.

**À dire :**
> "Si l'API est indisponible — mauvaise clé, quota dépassé, pas de réseau — le système ne plante pas. Il active les fallbacks pré-définis et génère quand même un PDF utilisable."

**Remettre la vraie clé après.**

---

## Scène 9 — Architecture (30 secondes)

**Action :** Montrer le `README.md` ou le schéma ASCII de l'architecture.

**À dire :**
> "Pour résumer l'architecture : l'utilisateur interagit avec Streamlit, qui passe par l'orchestrateur Workflow. Celui-ci lance d'abord le pipeline RAG pour récupérer le contexte, puis les 3 agents CrewAI en séquence, et enfin le générateur PDF. Tout est tracé dans les logs structurés."

---

## Conclusion (15 secondes)

**À dire :**
> "PrimaryTeachingSMA démontre l'utilisation concrète d'un Système Multi-Agents pour automatiser une tâche métier réelle : la création d'activités pédagogiques. Les 3 agents collaborent, le RAG ancre les réponses dans des ressources validées, et le résultat est un document professionnel directement utilisable par un instituteur."

---

## Valeurs de démonstration recommandées

Pour une démonstration variée, voici 3 scénarios :

### Scénario A — CE2, Logique (démonstration principale)
- Âge : 8 ans | Niveau : CE2 | Type : Logique & Raisonnement | Difficulté : Moyen

### Scénario B — CP, Suites visuelles
- Âge : 6 ans | Niveau : CP | Type : Suites & Patterns | Difficulté : Facile

### Scénario C — CM1, Pensée algorithmique
- Âge : 10 ans | Niveau : CM1 | Type : Pensée Algorithmique | Difficulté : Difficile

---

## Conseils de présentation

- Ouvrir le terminal et le navigateur côte à côte pour voir les logs en temps réel
- Zoomer sur les logs structurés pour les rendre lisibles
- Préparer le PDF généré d'une exécution précédente au cas où l'API serait lente
- La durée typique d'un run complet est de **30 à 90 secondes** selon le modèle

---

*Script rédigé pour le projet universitaire PrimaryTeachingSMA — Système Multi-Agents*
