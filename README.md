\# MarketDashboard



\- séparation claire entre \*\*scripts de données\*\* (`createdata\_\*`) et \*\*scripts de visuels\*\* (`createvisu\_\*`),

\- facile à faire tourner en local, à automatiser (CRON / tâche planifiée) ou à brancher sur d’autres sources (APIs, bases, scrapers),

\- rendu visuel calqué sur des \*\*slides PowerPoint existantes\*\* (secteurs, macro, taux, crédit).



But: 

\- \*\*changer la source de données\*\* sans toucher au code de visu,

\- \*\*re-générer tous les PNG\*\* à partir d’un simple `python -m scripts.build\_all`,

\- plugger ça ensuite dans un script PowerPoint (VBA ou python-pptx).



---



\## 1. Contenu du projet



```text

MarketDashboard/

├─ marketdash/              # (optionnel) helpers génériques

│  ├─ \_\_init\_\_.py

│  ├─ utils.py              # fonctions génériques (perfs, chemins, etc.)

│  └─ config.py             # chargement de config.yaml

├─ scripts/

│  ├─ createdata.py         # secteurs actions (SP500 \& Stoxx600)

│  ├─ createvisu.py         # visuel secteurs (2 panneaux)

│  ├─ createdata\_macro.py   # dashboard macro (indices / ETF)

│  ├─ createvisu\_macro.py   # visuel macro (jauges par bloc)

│  ├─ createdata\_rates.py   # taux : courbe US, spreads, US vs Allemagne

│  ├─ createvisu\_rates.py   # visuel marché des taux

│  ├─ createdata\_credit.py  # crédit : OAS US IG / HY / Europe HY / EM HY

│  ├─ createvisu\_credit.py  # visuel marché du crédit

│  ├─ build\_all.py          # lance tous les createdata\_\* + createvisu\_\*

│  └─ clean.py              # supprime CSV \& PNG générés

├─ data/                    # CSV générés (non versionnés)

├─ output/                  # PNG générés (non versionnés)

├─ config.yaml              # configuration des chemins \& providers

├─ requirements.txt

├─ LICENSE

└─ README.md



2\. Principe d’architecture



Le projet repose sur un principe simple :



createdata\_\*

→ va chercher la donnée (Yahoo Finance, FRED, etc.)

→ calcule les perfs / agrégations nécessaires

→ écrit un CSV dans data/



createvisu\_\*

→ lit le CSV dans data/

→ reproduit le design du slide (taille, couleurs, layout, jauges…)

→ sauvegarde un PNG dans output/



build\_all.py

→ enchaîne tous les createdata\_\* puis tous les createvisu\_\*

→ en un seul call, régénère tous les dashboards.



Si quelqu'un veut changer la source (scraping, base interne, autre API), il modifie seulement createdata\_\*.py.



3\. Installation (local)

3.1. Prérequis



Python 3.10+



Git installé (optionnel mais recommandé)



Connexion internet pour télécharger les données (Yahoo / FRED)



3.2. Cloner le repo



Depuis un terminal / PowerShell :



cd C:\\Users\\Zied

git clone https://github.com/MasmoudiZ/MarketDashboard.git

cd MarketDashboard



3.3. Créer un environnement virtuel (Windows)

python -m venv .venv



\# PowerShell

.venv\\Scripts\\Activate.ps1

\# Si ça bloque pour des raisons de politique d’exécution :

\#   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

\# puis re-tenter :

\#   .venv\\Scripts\\Activate.ps1



3.4. Installer les dépendances

pip install -r requirements.txt



4\. Configuration



Le fichier config.yaml contient la configuration minimale :



paths:

&nbsp; data\_dir: "data"

&nbsp; output\_dir: "output"



providers:

&nbsp; use\_yahoo: true      # données marché via yfinance

&nbsp; use\_fred: true       # données FRED (taux, crédit OAS)





Tu peux ajuster ces valeurs (par exemple si tu veux pointer data/ ou output/ ailleurs).



4.1. Clé API FRED (taux + crédit)



Les scripts taux et crédit utilisent l’API FRED (Federal Reserve).

Il faut définir la variable d’environnement FRED\_API\_KEY.



Sous PowerShell (Windows) :

$env:FRED\_API\_KEY = "TON\_API\_KEY\_FRED"





(À refaire dans chaque nouvelle session, sauf si tu la définis de manière permanente dans les variables d’environnement Windows.)



5\. Usage : scripts séparés

5.1. Dashboards secteurs (SP500 \& Stoxx 600)

cd C:\\Users\\Zied\\MarketDashboard



\# 1) Récupérer / recalculer les données secteurs

python -m scripts.createdata



\# 2) Générer le visuel secteurs (2 panneaux)

python -m scripts.createvisu





Input : téléchargement de données via yfinance (ETF sectoriels US et Europe).



Output :



data/sector\_data.csv



output/sectors\_2panels\_legacy\_style.png



Le PNG est dimensionné et stylé pour coller au slide historique (bande bleue, alternance de lignes, jauges 5D / 1M / 3M / YTD, etc.).



5.2. Dashboard macro

\# Data

python -m scripts.createdata\_macro



\# Visu

python -m scripts.createvisu\_macro





Input : proxies macro (indices actions, obligations, or, pétrole, etc.) via yfinance.



Output :



data/macro\_dashboard.csv



output/macro\_dashboard\_legacy\_style.png



Le rendu est un tableau macro en blocs (Actions, Obligations, Matières premières, etc.) avec jauges horizontales homogènes gauche → droite, calqué sur le design original.



5.3. Marché des taux

\# Data (nécessite FRED\_API\_KEY)

python -m scripts.createdata\_rates



\# Visu

python -m scripts.createvisu\_rates





Input : séries FRED (courbe US, Bund 10 ans, OAT 10 ans, etc.).



Output :



data/rates\_fred.csv



1 ou plusieurs PNG dans output/ (par ex. rates\_dashboard\_fred.png + images split si nécessaire).



Les graphiques reproduisent :



la courbe des taux US (1M → 30Y),



les spreads 2–10 ans US et 2–10 ans Allemagne,



les taux US 10Y vs Bund 10Y.



Échelle de temps : généralement depuis octobre 2020, agrégé en mensuel pour coller aux slides originels.



5.4. Marché du crédit

\# Data (nécessite FRED\_API\_KEY)

python -m scripts.createdata\_credit



\# Visu

python -m scripts.createvisu\_credit





Input : OAS FRED (US IG, US HY, EU HY, EM HY).



Output :



data/credit\_dashboard.csv



output/credit\_dashboard\_legacy\_style.png (ou équivalent, selon le nom dans le script).



Le visuel suit le même gabarit PowerPoint (titre en haut, légende en bas, échelle temporelle alignée sur oct-2020 → date récente, etc.).



6\. Tout ré-générer d’un coup



Pour refaire proprement tous les CSV + PNG :



cd C:\\Users\\(fichier)\\MarketDashboard



\# (Optionnel) nettoyer ce qui existe déjà

python -m scripts.clean



\# Refaire tout

python -m scripts.build\_all





build\_all.py enchaîne dans l’ordre :



scripts.createdata (secteurs)



scripts.createdata\_macro (macro)



scripts.createdata\_rates (taux)



scripts.createdata\_credit (crédit)



scripts.createvisu (visuel secteurs)



scripts.createvisu\_macro (visuel macro)



scripts.createvisu\_rates (visuel taux)



scripts.createvisu\_credit (visuel crédit)



7\. Logique “quant / desk-friendly”

7.1. Remplacer facilement la source de données



Exemples :



Tu veux utiliser Refinitiv, Bloomberg, un CSV maison, ou un scraper Investing.com :



tu ne touches qu’aux scripts createdata\_\*.py



tu gardes intacts les createvisu\_\* (validés par le métier, répliquant exactement les slides).



Exemple de pseudo-refactor dans createdata.py :



\# au lieu de \_load\_price\_series\_yahoo(...)

\# tu peux brancher un \_load\_price\_series\_refinitiv(...)

\# ou lire un CSV déjà préparé





Tant que le CSV de sortie garde les mêmes colonnes (secteur, Perf\_5D, Perf\_1M, etc.), les visuels ne voient pas la différence.



7.2. Automatisation / intégration PowerPoint



Une fois les PNG générés dans output/ :



tu peux écrire un script VBA ou python-pptx pour :



ouvrir un modèle PowerPoint,



remplacer les images d’un slide par les nouveaux PNG,



garder exactement le même placement et gabarit.



Le fait d’avoir :



un PNG par slide ou même



plusieurs PNG (1 par graphique)



permet une insertion très précise, avec des coordonnées constantes dans le template PPT.



8\. Résolution de problèmes courants

8.1. KeyError: 'data\_dir' dans createvisu\_\*



Vérifier que ton config.yaml contient bien :



paths:

&nbsp; data\_dir: "data"

&nbsp; output\_dir: "output"





Et que les scripts createvisu\_\* appellent bien la fonction qui lit ce config.yaml.



8.2. Erreurs FRED\_API\_KEY n'est pas défini



Tu dois définir la variable d’environnement :



$env:FRED\_API\_KEY = "TA\_CLEF\_API\_FRED"





Puis relancer :



python -m scripts.createdata\_rates

python -m scripts.createdata\_credit



8.3. Messages HTTP Error 404 sur certains tickers Yahoo



Certains tickers proxys peuvent être delistés ou mal référencés dans ta région.



Solutions possibles :



changer de ticker proxy dans les dictionnaires (secteurs, macro),



ou commenter temporairement la ligne en question dans le dict.



Les scripts loggent les erreurs mais continuent à construire le CSV et les PNG avec ce qui est disponible.

