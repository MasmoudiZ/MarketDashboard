# MarketDashboard
Visuels Dashboard 

Ce projet génère automatiquement des tableaux indiciels, sectoriels:
performances 5D / 1M / 3M / YTD, jauges vert-rouge, mise en page professionnelle identique à Bloomberg ou Excel.

Objectif

L’objectif est de séparer proprement la collecte de données et la visualisation,
pour permettre à un quant, un analyste ou un développeur de :

changer de source (Yahoo, FRED, TradingEconomics, base interne…) sans toucher au code graphique,

automatiser les mises à jour (via cron, Airflow, GitHub Actions…),

garder un visuel stable et desk-compatible.

Structure du projet:

MarketDashboard/
├─ scripts/
│  ├─ createdata.py       # collecte et met en cache les données
│  └─ createvisu.py       # crée les visuels à partir des données
├─ data/
│  └─ .gitkeep            # dossier de stockage local (non versionné)
├─ output/
│  └─ .gitkeep            # visuels générés (ex: sectors_2panels.png)
├─ config.yaml            # configuration des instruments / sources
├─ requirements.txt       # dépendances Python
├─ .gitignore             # fichiers ignorés par Git
└─ README.md              # ce fichier
