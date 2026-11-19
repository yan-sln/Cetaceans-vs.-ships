# Propal QGIS :
## Principe général

Le principe retenu est le suivant :
- **Go constitue le moteur de simulation** et assure la gestion de l'ensemble des données métier.
- **Python/PyQGIS assure le contrôle et la communication** entre l'interface et le moteur.
- **QGIS constitue l'interface géographique**, permettant de visualiser la simulation, de modifier ses paramètres et d'en analyser les résultats.

Les couches géographiques affichées dans QGIS sont des représentations de l'état de la simulation. Elles ne constituent pas la source de référence des données métier.

## Séparation des responsabilités

### Serveur Go := moteur de simulation

Le serveur Go centralise toute la logique métier et constitue la source de vérité de la simulation.

Il est responsable de :
- La création et la gestion des agents (navires, cétacés, environnement).
- La gestion de leurs états, déplacements et comportements.
- La simulation des interactions entre navires et cétacés.
- La détection et la caractérisation des collisions.
- L'estimation de la mortalité associée aux impacts.
- L'application des stratégies de prévention (réduction de vitesse, déviation des trajectoires).
- Le calcul des indicateurs et statistiques de simulation.

Il gère également l'horloge simulée, indépendamment du temps réel et de la fréquence de rafraîchissement de QGIS.

### Plugin Python := contrôleur et interface

Le plugin Python, développé avec PyQGIS et les bibliothèques Qt, assure l'intégration du moteur de simulation dans QGIS.

Il est responsable de :
- La gestion des interactions utilisateur et des paramètres de simulation.
- L'envoi des commandes au serveur Go.
- La réception des positions et événements transmis par le serveur.
- La mise à jour des couches géographiques QGIS.
- L'affichage des indicateurs et statistiques.
- La gestion de la connexion et de l'état de la simulation.

Il constitue une couche intermédiaire entre l'interface géographique et le moteur, sans implémenter lui-même la logique de simulation.

### QGIS := interface géographique

QGIS assure la visualisation et l'exploration spatiale des données.

Il permet notamment de représenter :
- Les zones de présence et de densité des cétacés.
- Les zones sensibles et les contraintes environnementales.
- Les routes maritimes et trajectoires des navires.
- Les positions des navires en mouvement.
- Les événements de collision.
- Les cartes de risque et résultats des simulations.

Son interface permet également de configurer les scénarios, de sélectionner les stratégies de prévention et de consulter les indicateurs associés.

## Communication entre les composants

La communication entre le plugin Python et le serveur Go repose sur deux mécanismes complémentaires : une API REST et une connexion WebSocket.

**API REST -> Commandes et configuration**

Le plugin Python utilise des requêtes HTTP pour transmettre les actions de l'utilisateur au serveur Go.

Cela concerne notamment :
- L'initialisation d'une simulation.
- Le démarrage, la mise en pause et l'arrêt.
- La modification des paramètres.
- Le choix des stratégies de prévention.
- La consultation des résultats et statistiques.

**WebSocket -> Données dynamiques**

Une connexion WebSocket persistante permet au serveur Go de transmettre au plugin Python les évolutions de la simulation.

Elle est notamment utilisée pour :
- La diffusion des positions actualisées des navires.
- La transmission des événements de collision.
- La mise à jour des statistiques.
- La notification des changements d'état de la simulation.

Cette séparation permet de distinguer les commandes utilisateur des flux de données dynamiques.

## Déroulement des échanges

Le fonctionnement général s'organise de la manière suivante :
1. L'utilisateur configure une simulation depuis le panneau du plugin QGIS.
2. Le plugin transmet les paramètres au serveur Go via l'API REST.
3. Le serveur initialise les agents et démarre le moteur de simulation.
4. Le moteur fait évoluer les agents et calcule leurs interactions.
5. Le serveur transmet périodiquement les changements d'état via WebSocket.
6. Le plugin Python réceptionne les données et actualise les couches géographiques dans QGIS.
7. Les événements et statistiques sont affichés dans l'interface.
8. L'utilisateur peut modifier les paramètres ou interrompre la simulation depuis le plugin.

Le calcul de la simulation et son affichage restent indépendants : le moteur Go peut fonctionner à une vitesse accélérée, tandis que QGIS actualise les représentations à une fréquence adaptée aux performances graphiques.

## Gestion des données et performances

Les données métier et l'état courant des agents sont gérés par le serveur Go. Les données géographiques de référence peuvent être stockées dans une base PostgreSQL/PostGIS ou importées depuis des fichiers géographiques.

Les couches QGIS sont actualisées à partir des informations transmises par le serveur. Elles ne doivent pas être utilisées comme stockage de référence de la simulation.

Afin de préserver la fluidité de l'interface, trois fréquences doivent être distinguées :
- La fréquence de calcul du moteur de simulation.
- La fréquence de transmission des mises à jour par le serveur.
- La fréquence de rafraîchissement graphique de QGIS.

Le plugin doit également gérer les communications réseau de manière asynchrone, sans bloquer l'interface. Les modifications des couches QGIS sont effectuées dans le thread principal.

## Choix techniques

| Composant                | Technologie          | Fonction                              |
| ------------------------ | -------------------- | ------------------------------------- |
| Interface géographique   | QGIS                 | Visualisation et exploration spatiale |
| Plugin                   | Python / PyQGIS / Qt | Contrôle et intégration               |
| Moteur de simulation     | Go                   | Logique métier et calculs             |
| Communication            | HTTP REST            | Commandes et configuration            |
| Communication temps réel | WebSocket            | Diffusion des états et événements     |

---

## Projet analogue intéressant :
- https://github.com/PeterCotroneo/Wake
- https://github.com/thanderoy/ais-tracker
