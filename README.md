# Cetaceans vs. ships

**Simulation multi-agents du risque de collision entre le trafic maritime et les cétacés aux îles Canaries**

## Descriptif du projet

Les eaux des îles Canaries sont fréquentées à la fois par des navires assurant le transport de passagers et de marchandises, et par plusieurs espèces de cétacés. "Collisions between vessels and cetaceans globally are an issue of growing concern. Since large ships reached travelling speeds greater than 14 knots around the 1950ies, collisions with vessels have increased and today affect a rising number of cetacean populations (Laist et al. 2001)."\[1]

Ce projet consiste à développer une simulation multi-agents pour étudier ces interactions. Chaque navire sera représenté par un agent doté de caractéristiques et de règles de déplacement propres. Le modèle intégrera également les contraintes géographiques du milieu marin et la répartition spatiale des zones fréquentées par les cétacés.

Plusieurs configurations du trafic seront comparées : une situation de référence sans mesure supplémentaire, une réduction de la vitesse des navires dans les zones sensibles, une adaptation de leurs trajectoires en fonction de la présence des cétacés, puis une combinaison de ces mesures.

La simulation permettra ainsi d'étudier les effets de ces stratégies sur les interactions entre navires et cétacés, mais aussi sur les conditions de navigation. Les résultats dépendront des hypothèses retenues et de la qualité des données disponibles, notamment pour représenter les déplacements des animaux et leur présence à proximité de la surface.

## Question de recherche

Dans quelle mesure la réduction de la vitesse des navires et l'adaptation de leurs trajectoires dans les zones fréquentées par les cétacés permettent-elles de réduire le risque de collision aux îles Canaries, sans entraîner de perturbations excessives du trafic maritime ?

L'hypothèse étudiée est que la combinaison d'une réduction ciblée de la vitesse et d'un ajustement des routes peut réduire davantage le risque de collision que l'application isolée de chacune de ces mesures. La simulation devra déterminer si ce gain écologique s'accompagne de délais ou de distances supplémentaires pour les navires.

## Indicateurs clefs

|Indicateur|Ce qu'il permet d'évaluer|
|---|---|
|**Nombre de collisions simulées**|Comparer le nombre d'événements de collision entre les différentes stratégies.|
|**Risque de collision**|Mesurer la fréquence ou la probabilité des situations dans lesquelles un navire et un cétacé entrent dans une configuration de collision.|
|**Mortalité estimée des cétacés**|Estimer les conséquences biologiques des collisions à partir d'une probabilité de mortalité conditionnelle à une collision.|
|**Durée moyenne des trajets**|Mesurer les retards associés aux mesures de régulation.|
|**Distance moyenne parcourue par les navires**|Évaluer les détours imposés par l'adaptation des trajectoires.|
|**Répartition spatiale du risque**|Repérer les secteurs où les interactions entre navires et cétacés sont les plus fréquentes et observer leur évolution selon les stratégies.|

Le nombre de collisions et la mortalité estimée seront deux indicateurs distincts. Une collision simulée ne correspond pas nécessairement à la mort d'un animal. L'estimation de la mortalité devra donc intégrer la probabilité de décès associée aux caractéristiques de chaque collision, notamment la vitesse du navire.

## Résultat attendu

Le projet doit permettre de comparer les stratégies de régulation selon deux dimensions : la réduction du risque pour les cétacés et les contraintes supplémentaires imposées au trafic maritime.

Il s'agira notamment de déterminer si une stratégie combinant réduction de vitesse et adaptation des trajectoires apporte un meilleur compromis que des mesures appliquées séparément. La simulation pourra également faire apparaître les secteurs où la superposition entre trafic maritime et présence des cétacés justifie une attention particulière.

Les résultats constitueront une base d'aide à l'analyse des mesures de prévention. Ils ne prétendront pas prédire exactement le nombre de collisions réelles, mais permettront de comparer des scénarios à partir d'hypothèses explicites et de données géographiques et biologiques disponibles.


## Glossary:
- **Automatic identification system** (AIS) is an automatic tracking system that uses transponders on ships and is used by vessel traffic services.

## Sources:
- Calcul collision léthale https://www.wwf.fr/sites/default/files/doc-2017-07/16_rapport_trafic_maritime_et_risques_de_collisions_avec_les_grands_cetaces_sanctuaire_pelagos.pdf

- Vessel strike encounter risk model https://www.researchgate.net/publication/387706146_Vessel_strike_encounter_risk_model_informs_mortality_risk_for_endangered_North_Atlantic_right_whales_along_the_United_States_east_coast

- Study of the Inter-Island Maritime Traffic with respect to Collisions between Ships and Cetaceans in the Canary Islands \[1] https://www.researchgate.net/profile/Fabian-Ritter-6/publication/242190031_Quantification_of_ferry_traffic_in_the_Canary_Islands_Spain_and_its_implications_for_collisions_with_cetaceans/links/0c960528e276b848be000000/Quantification-of-ferry-traffic-in-the-Canary-Islands-Spain-and-its-implications-for-collisions-with-cetaceans.pdf
- A Quantification of Ferry Traffic in the Canary Islands (Spain) and its Significance for Collisions with Cetacean https://www.researchgate.net/profile/Jose-Grassa/publication/337567385_Study_of_the_Inter-Island_Maritime_Traffic_with_respect_to_Collisions_between_Ships_and_Cetaceans_in_the_Canary_Islands/links/5dde990e299bf10bc32b7f66/Study-of-the-Inter-Island-Maritime-Traffic-with-respect-to-Collisions-between-Ships-and-Cetaceans-in-the-Canary-Islands.pdf

- Collisions (83) 1985-2014: https://datosdelanzarote.lztic.com/media/item/docs/Colisiones-cet%C3%A1ceos-con-embarcaciones-(2000-2014)-20181205140118697Colisiones-2000-2014.pdf
- Cétacés échoués (938) 2000-2018 : https://datosdelanzarote.lztic.com/media/item/docs/Estad%C3%ADsticas-de-varamientos-de-cet%C3%A1ceos-en-Canarias-(2000-2018)-20190612154619470Cet%C3%A1ceos-2000-2018.pdf

- Whale superhighways : https://wwfwhales.org/news-stories/protecting-blue-corridors-report

## Data:
- https://github.com/OpenSeaMap -> récupérer les cartes
    - Pour QGIS : https://wiki.openseamap.org/wiki/QGIS
- https://github.com/vessel-api/VesselApi -> récupérer les navires
    - Pour QGIS : https://plugins.qgis.org/plugins/wake/
- -> récupérer répartitions populations cétacés (existe dans \[1])
- https://emodnet.ec.europa.eu/en

## Contacts:
- https://en.wikipedia.org/wiki/Natacha_Aguilar_de_Soto
- https://scholar.google.com/citations?user=yKHlp7cAAAAJ


## Risques méthodologiques

- Observations biologiques biaisées.
- Des données comportementales manquantes.
- Les collisions réelles sont sous-déclarées.

## Structure du projet

```text
Cetaceans-vs.-ships/
├── plugin-qgis/                 # Plugin Python / PyQGIS intégré à QGIS
│   ├── controllers/              # Contrôle des interactions et des échanges avec le serveur
│   ├── resources/                # Ressources du plugin, dont l'icône
│   ├── services/                 # Services applicatifs et communication
│   ├── ui/                       # Interface utilisateur
│   ├── __init__.py               # Point d'entrée du plugin QGIS
│   ├── main.py                   # Initialisation du plugin
│   ├── metadata.txt              # Métadonnées reconnues par QGIS
│   ├── pyproject.toml            # Configuration et dépendances Python
│   ├── uv.lock                   # Versions verrouillées des dépendances Python
│   └── README.md
├── server/                       # Serveur et futur moteur de simulation Go
│   ├── cmd/                      # Emplacement prévu pour les exécutables
│   ├── go.mod                    # Module et dépendances Go
│   └── README.md
├── docs/                         # Documentation du projet
│   ├── architecture/             # Architecture des composants et échanges
│   ├── sources/                  # Documents et références documentaires
│   └── user-guide/               # Emplacement prévu pour le guide utilisateur
├── contracts/                    # Contrats des interfaces entre composants
│   └── openapi.yaml              # Description de l'API REST
├── deployment/                   # Configuration de déploiement
│   └── compose.yaml              # Services Docker Compose
├── .gitignore
└── README.md                     # Présentation générale du projet
```

Le plugin QGIS fournit l'interface qui contrôle la simulation. Les dossiers `ui/`, `controllers/` et `services/` sont les emplacements des différentes parties du plugin ; `resources/` contient actuellement son icône. Le serveur Go est destiné à porter le moteur de simulation, tandis que le contrat OpenAPI décrit son interface REST. La documentation d'architecture précise la séparation des responsabilités et les échanges entre ces composants.

Certains dossiers, notamment `server/cmd/` et `docs/user-guide/`, sont encore des emplacements de travail et peuvent être vides.

### README des composants

- [README du plugin QGIS](plugin-qgis/README.md) : installation de l'environnement Python et commandes de vérification.
- [README du serveur Go](server/README.md) : informations de démarrage du module Go.
- [Documentation d'architecture](docs/architecture/README.md) : rôles du serveur, du plugin et de QGIS, ainsi que les échanges REST et WebSocket.