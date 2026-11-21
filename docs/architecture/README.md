# Propal QGIS

## Principe général

Le principe retenu est le suivant :

- **Go constitue le moteur de simulation** et assure la gestion de l'ensemble des données métier.
- **Python/PyQGIS assure le contrôle et la communication** entre l'interface et le moteur.
- **QGIS constitue l'interface géographique**, permettant de visualiser la simulation, de modifier ses paramètres et d'en analyser les résultats.

Les couches géographiques affichées dans QGIS sont des représentations de l'état de la simulation. Elles ne constituent pas la source de référence des données métier.

Le plugin Python assure également le lancement et la supervision du serveur Go, afin que l'utilisateur puisse démarrer et piloter une simulation directement depuis QGIS, sans intervention extérieure.

## Séparation des responsabilités

### Serveur Go := moteur de simulation

Le serveur Go centralise toute la logique métier et constitue la source de vérité de la simulation.

Il est responsable de :

- La création et la gestion des agents (navires, cétacés, environnement).
- La gestion de leurs états, déplacements et comportements.
- La gestion des routes maritimes prédéfinies.
- La simulation des interactions entre navires et cétacés.
- La détection et la caractérisation des collisions.
- L'estimation de la mortalité associée aux impacts.
- L'application des stratégies de prévention (réduction de vitesse, déviation des trajectoires).
- Le calcul des indicateurs et statistiques de simulation.
- La production des données géographiques correspondant aux entités.

Il gère également l'horloge simulée, indépendamment du temps réel et de la fréquence de rafraîchissement de QGIS.

Le serveur est responsable de l'état réel des entités et de leurs évolutions. Il transmet au plugin Python les données nécessaires à leur représentation géographique, sans manipuler directement les couches QGIS.

### Plugin Python := contrôleur et interface

Le plugin Python, développé avec PyQGIS et les bibliothèques Qt, assure l'intégration du moteur de simulation dans QGIS.

Il est responsable de :

- La gestion des interactions utilisateur et des paramètres de simulation.
- Le lancement, la supervision et l'arrêt du processus serveur Go.
- La vérification de la disponibilité du moteur.
- L'envoi des commandes au serveur Go via HTTP.
- La réception des positions et événements transmis par le serveur via WebSocket.
- La mise à jour des features et géométries des couches géographiques QGIS.
- L'affichage des indicateurs et statistiques.
- La gestion de la connexion et de l'état de la simulation.
- La synchronisation des données géographiques après une connexion initiale ou une interruption de communication.

Il constitue une couche intermédiaire entre l'interface géographique et le moteur, sans implémenter lui-même la logique de simulation.

Les communications réseau doivent être réalisées de manière asynchrone, sans bloquer l'interface QGIS. Les modifications des couches géographiques sont effectuées dans le thread principal de QGIS.

### QGIS := interface géographique

QGIS assure la visualisation et l'exploration spatiale des données.

Il permet notamment de représenter :

- Les zones de présence et de densité des cétacés.
- Les zones sensibles et les contraintes environnementales.
- Les routes maritimes et trajectoires des navires.
- Les positions des navires en mouvement.
- Les événements de collision.
- Les cartes de risque et résultats des simulations.

Le projet QGIS repose notamment sur quatre couches vectorielles :

- **Collisions** : événements de collision détectés par le moteur.
- **Routes** : routes maritimes prédéfinies.
- **Navires** : positions et caractéristiques des navires.
- **Cétacés** : positions et caractéristiques des cétacés.

Chaque feature correspond à une entité ou à un événement de la simulation.

Les couches sont alimentées et actualisées par le plugin Python à partir des données transmises par Go. Elles constituent uniquement une représentation de l'état de la simulation.

Pour les entités dynamiques, des couches vectorielles mémoire QGIS (`QgsVectorLayer` avec le fournisseur `memory`) peuvent être utilisées.

Le fond cartographique peut notamment s'appuyer sur OpenSeaMap, indépendamment des couches propres à la simulation.

Son interface permet également de configurer les scénarios, de sélectionner les stratégies de prévention et de consulter les indicateurs associés.

## Communication entre les composants

La communication entre le plugin Python et le serveur Go repose sur deux mécanismes complémentaires : une API REST et une connexion WebSocket.

Le plugin Python assure également le lancement du serveur Go et la gestion de son cycle de vie.

**API REST -> Commandes et configuration**

Le plugin Python utilise des requêtes HTTP pour transmettre les actions de l'utilisateur au serveur Go.

Cela concerne notamment :

- L'initialisation d'une simulation.
- Le démarrage, la mise en pause, la reprise et l'arrêt.
- La modification des paramètres du scénario courant.
- Le choix des routes maritimes.
- La modification de la vitesse des navires.
- Le choix des stratégies de prévention.
- La consultation des résultats et statistiques.

Les paramètres peuvent être modifiés pendant l'exécution de la simulation. Les modifications concernent les entités déjà présentes dans le scénario courant, conformément aux règles métier définies par le moteur.

Chaque modification est transmise individuellement au serveur. Celui-ci applique la commande et retourne une réponse HTTP indiquant le résultat de l'opération.

Une réponse positive (par exemple HTTP 200) permet au plugin de confirmer la modification et d'actualiser la valeur affichée dans le panneau.

En cas d'erreur, le plugin conserve la dernière valeur confirmée et informe l'utilisateur.

**WebSocket -> Données dynamiques**

Une connexion WebSocket persistante permet au serveur Go de transmettre au plugin Python les évolutions de la simulation.

Elle est notamment utilisée pour :

- La diffusion des positions actualisées des navires.
- La diffusion des positions actualisées des cétacés.
- La transmission des événements de collision.
- La mise à jour des statistiques.
- La notification des changements d'état de la simulation.
- La transmission des modifications concernant les entités.

Compte tenu du nombre d'entités envisagé (environ 1 000 navires et 1 000 cétacés), il est préférable de privilégier la transmission des seules entités modifiées plutôt que de renvoyer systématiquement l'ensemble des données.

Les routes étant prédéfinies, elles peuvent être chargées initialement et ne nécessitent pas d'actualisation permanente.

Cette séparation permet de distinguer les commandes utilisateur des flux de données dynamiques.

## Déroulement des échanges

Le fonctionnement général s'organise de la manière suivante :

1. L'utilisateur ouvre le panneau du plugin QGIS.
2. Le plugin vérifie la disponibilité du serveur Go et lance le processus si nécessaire.
3. Le plugin attend que le moteur soit opérationnel et établit la connexion WebSocket.
4. Le plugin initialise le scénario et récupère les données nécessaires à la création ou à la synchronisation des couches QGIS.
5. L'utilisateur configure et démarre la simulation depuis le panneau du plugin.
6. Le plugin transmet les paramètres au serveur Go via l'API REST.
7. Le serveur initialise les agents et démarre le moteur de simulation.
8. Le moteur fait évoluer les agents et calcule leurs interactions.
9. Le serveur transmet périodiquement les changements d'état via WebSocket.
10. Le plugin Python réceptionne les données et actualise les features et géométries des couches géographiques QGIS.
11. Les événements et statistiques sont affichés dans l'interface.
12. L'utilisateur peut modifier les paramètres du scénario courant ou interrompre la simulation depuis le plugin.

Les modifications des paramètres sont transmises individuellement au serveur via HTTP. Le moteur applique les changements aux entités concernées et retourne une confirmation. L'actualisation géographique intervient indépendamment à partir des données transmises via WebSocket.

Le calcul de la simulation et son affichage restent indépendants : le moteur Go peut fonctionner à une vitesse accélérée, tandis que QGIS actualise les représentations à une fréquence adaptée aux performances graphiques.

## Gestion des données et performances

Les données métier et l'état courant des agents sont gérés par le serveur Go. Les données géographiques de référence peuvent être stockées dans une base PostgreSQL/PostGIS ou importées depuis des fichiers géographiques.

Pour la première version, les couches dynamiques peuvent être constituées de couches vectorielles mémoire QGIS, alimentées directement par les données transmises via WebSocket. Une base PostgreSQL/PostGIS pourra être envisagée ultérieurement pour l'archivage des scénarios ou l'analyse historique, sans être intégrée à la boucle de simulation temps réel.

Les couches QGIS sont actualisées à partir des informations transmises par le serveur. Elles ne doivent pas être utilisées comme stockage de référence de la simulation.

Chaque entité dispose d'un identifiant stable permettant de retrouver sa feature dans QGIS et de mettre à jour sa géométrie ou ses attributs sans supprimer et recréer systématiquement la feature.

La gestion des couches repose sur les principes suivants :

- Les routes sont chargées initialement et restent inchangées, sauf modification du scénario.
- Les navires et les cétacés sont créés lors de l'initialisation, puis leurs positions et attributs sont actualisés.
- Les collisions sont ajoutées au fur et à mesure de leur détection.
- Les features ne sont pas recréées à chaque actualisation.
- Les modifications des couches sont effectuées dans le thread principal QGIS.

Afin de préserver la fluidité de l'interface, trois fréquences doivent être distinguées :

- La fréquence de calcul du moteur de simulation.
- La fréquence de transmission des mises à jour par le serveur.
- La fréquence de rafraîchissement graphique de QGIS.

Le moteur peut ainsi calculer les déplacements à une fréquence supérieure à celle de la transmission et du rafraîchissement graphique.

Le plugin peut regrouper les mises à jour reçues et appliquer le dernier état disponible aux couches QGIS à une fréquence adaptée aux performances de l'application.

Les fréquences définitives devront être déterminées par des tests de performances.

Le plugin doit également gérer les communications réseau de manière asynchrone, sans bloquer l'interface. Les modifications des couches QGIS sont effectuées dans le thread principal.

Une resynchronisation complète doit être possible lors de la connexion initiale et après une interruption WebSocket, afin de garantir la cohérence entre les données du moteur et leur représentation dans QGIS.

## Interface du plugin

L'interface doit être intégrée au panneau latéral de QGIS et privilégier une organisation minimaliste, intuitive et évolutive.

La carte constitue l'espace principal de visualisation. Le panneau du plugin regroupe les informations essentielles et les commandes nécessaires au pilotage de la simulation.

L'interface s'organise autour de quatre blocs :

**1. Contexte et état de connexion**

- Nom du scénario courant.
- État de connexion au serveur Go.
- État de la simulation (non démarrée, en cours, en pause, terminée).

**2. Indicateurs de simulation**

Trois compteurs visibles en permanence :

- Nombre de collisions.
- Nombre de collisions mortelles.
- Durée de la simulation (temps simulé).

Ces indicateurs sont actualisés automatiquement à partir des données transmises par Go.

**3. Contrôle de la timeline**

- Bouton Play / Pause / Resume.
- Affichage de la date et de l'heure simulées.
- Frise temporelle indiquant la progression de la simulation.
- Éventuellement, contrôle de la vitesse d'avancement de l'horloge simulée.

La vitesse de simulation doit être distinguée de la vitesse physique des navires.

**4. Paramètres du scénario**

Les paramètres principaux restent directement visibles :

- Sélection de la route parmi trois routes prédéfinies.
- Modification de la vitesse des navires au moyen d'un curseur avec affichage numérique et unité en nœuds.

Les paramètres secondaires sont regroupés dans une section repliable « Paramètres avancés » :

- Stratégies de prévention.
- Conditions environnementales.
- Densité du trafic.
- Autres paramètres susceptibles d'être ajoutés ultérieurement.

L'organisation des paramètres doit être extensible afin de permettre l'ajout de nouveaux contrôles sans modifier la structure générale du panneau.

Les modifications sont transmises individuellement au serveur Go, sans bouton global « Appliquer ».

Le panneau doit distinguer trois états pour chaque modification :

- Modification confirmée et synchronisée.
- Modification en cours de transmission.
- Erreur ou modification refusée.

L'interface affiche toujours les valeurs confirmées par le moteur.

## Choix techniques

|Composant|Technologie|Fonction|
|---|---|---|
|Interface géographique|QGIS|Visualisation et exploration spatiale|
|Plugin|Python / PyQGIS / Qt|Contrôle, intégration et gestion du serveur|
|Moteur de simulation|Go|Logique métier, gestion des agents et calculs|
|Communication|HTTP REST|Commandes et configuration|
|Communication temps réel|WebSocket|Diffusion des positions, états et événements|
|Couches dynamiques|QgsVectorLayer (memory)|Représentation des entités dans QGIS|
|Fond cartographique|OpenSeaMap / XYZ Tiles|Cartographie maritime|

---

## Projet analogue intéressant :

- [https://github.com/PeterCotroneo/Wake](https://github.com/PeterCotroneo/Wake)
- https://github.com/thanderoy/ais-tracker
