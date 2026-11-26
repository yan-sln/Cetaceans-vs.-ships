# Moteur de simulation Go

Ce dossier correspond à la partie Go du projet **Cetaceans vs. ships**. Le but, c'est de simuler des navires et des cétacés dans une même zone maritime, puis de regarder ce qui se passe quand on change les conditions de navigation.

À terme, on voudrait comparer plusieurs situations : le trafic normal, des bateaux qui ralentissent dans certaines zones, des routes qui évitent ces zones, et un scénario qui combine les deux. L'idée est de voir si on peut réduire les collisions sans trop rallonger les trajets.

Dans l'architecture du groupe, **Go s'occupe de la simulation et des calculs**. Python fera le lien avec le moteur, et QGIS permettra d'afficher les bateaux, les cétacés et les résultats sur une carte.

Pour l'instant, on a surtout travaillé sur le moteur lui-même. **Les agents se déplacent, les navires suivent des routes et les cétacés peuvent plonger.** Tout ça fonctionne dans le terminal. On n'a pas encore ajouté les collisions, les statistiques finales ni la communication avec QGIS.

## Lancer le programme

Il faut avoir Go installé sur son PC. Dans `go.mod`, le projet indique actuellement la version `1.27.4` (Go peut avoir besoin de télécharger cette version selon l'installation locale).

Depuis la racine du dépôt, ouvrir un terminal et faire :

```powershell
cd server
go run ./cmd/simulation
```

Attention, si le terminal est déjà dans `server/`, on lance directement `go run ./cmd/simulation`. Les commandes Go doivent être exécutées dans ce dossier parce que c'est là que se trouve `go.mod`. Pas besoin de refaire `go mod init` non plus.

Pour mettre en forme le code et vérifier que tout va bien :

```powershell
go fmt ./...
go vet ./...
go test ./...
```

Et pour afficher le détail de chaque test :

```powershell
go test -v ./...
```

Actuellement, `main.go` lance un petit exemple de **10 secondes simulées**, avec un pas d'une seconde. On a 2 navires, 2 cétacés, 2 routes et 1 zone sensible. Le terminal affiche leur position à chaque itération, ainsi que la profondeur des cétacés. À la fin, on obtient l'état `finished`.

## Organisation des fichiers

```text
server/
├── cmd/
│   └── simulation/
│       └── main.go                # Lance l'exemple de simulation
├── internal/
│   ├── geometry/
│   │   ├── position.go            # Positions, distances et déplacements
│   │   └── position_test.go
│   ├── agents/
│   │   ├── ship.go                # Gestion des navires
│   │   ├── cetacean.go            # Gestion des cétacés
│   │   ├── agents_test.go
│   │   └── comportements_test.go
│   ├── environment/
│   │   ├── world.go               # Le monde et les listes d'agents
│   │   ├── zone.go                # Zones sensibles
│   │   ├── route.go               # Routes des navires
│   │   └── environment_test.go
│   └── simulation/
│       ├── config.go              # Paramètres de simulation
│       ├── clock.go               # Gestion du temps simulé
│       ├── engine.go              # Moteur principal
│       ├── engine_test.go
│       └── comportements_test.go
├── go.mod
└── README.md
```

On a séparé le code en plusieurs parties pour éviter de tout mettre dans `main.go`. C'est aussi plus simple à tester et à modifier par la suite.

Les dossiers `internal/api/`, `internal/strategy/` et `data/` sont prévus pour les prochaines étapes, mais ils ne contiennent pas encore de fichiers versionnés. Du coup, ils peuvent ne pas apparaître sur GitHub : Git ne garde pas les dossiers vides.

## Ce qu'on a déjà fait

### 1. Les calculs de base (`geometry`)

On a commencé par `geometry/position.go`. Une position est juste un couple de coordonnées `X` et `Y`, pour l'instant en mètres.

On a créé deux méthodes :

- `Distance()` : calcule la distance entre deux positions, avec `math.Hypot`.
- `Move()` : renvoie la nouvelle position d'un agent à partir de sa vitesse, sa direction et du temps écoulé.

Pour déplacer un agent, on utilise ces formules :

```text
nouveau X = X + vitesse × cos(direction) × pasTemps
nouveau Y = Y + vitesse × sin(direction) × pasTemps
```

On travaille en m/s pour les vitesses et en radians pour les directions. Dans notre repère, `0` radian pointe vers l'est et `π/2` vers le nord.

Petit point à garder en tête : les caps utilisés en navigation maritime n'ont pas exactement la même convention. Quand on utilisera des données AIS, il faudra faire la conversion.

On a aussi ajouté des tests pour être sûrs que les distances et les déplacements simples sont corrects.

### 2. Les agents : navires et cétacés (`agents`)

**Pour les navires — `ship.go`**

La structure `Ship` regroupe les infos d'un navire : son `ID`, sa `Position`, sa `Speed`, sa `Direction`, puis ses dimensions (`Length`, `Width`, `Draft`). `Draft`, c'est le tirant d'eau, donc la profondeur de la partie immergée du bateau.

On a aussi ajouté trois champs pour gérer les itinéraires :

- `NumeroRoute` : le numéro de la route attribuée au navire ;
- `PointSuivant` : le point de passage vers lequel il doit aller ;
- `EstArrive` : indique s'il a terminé sa route.

Il y a deux façons de faire avancer un navire :

- `Move(pasTemps)` le déplace simplement en ligne droite ;
- `SuivreRoute(pasTemps, points)` le fait suivre les points d'une route dans l'ordre.

Dans `SuivreRoute()`, on utilise `math.Atan2` pour calculer la direction du prochain point. Quand le bateau l'atteint, on passe au suivant. Si le bateau arrive sur un point avant la fin du pas de temps, il continue avec le temps restant. Une fois arrivé au dernier point, `EstArrive` passe à `true`.

**Pour les cétacés — `cetacean.go`**

On a la structure `Cetacean`, avec notamment l'espèce (`Species`), la position, la vitesse, la direction, la profondeur (`Depth`) et `Alive` pour savoir si l'animal est vivant.

On a rajouté quelques paramètres de comportement :

- `VitesseRotation` : pour changer progressivement de direction ;
- `VitesseVerticale` : pour plonger ou remonter ;
- `ProfondeurMax` : profondeur maximale dans notre modèle actuel.

La méthode `Move()` gère maintenant le déplacement horizontal et la profondeur. Quand le cétacé arrive à la surface ou à sa profondeur maximale, sa vitesse verticale change de signe et il repart dans l'autre sens. Et si `Alive` vaut `false`, il ne se déplace plus.

Pour le moment, c'est vraiment un **premier modèle de comportement**, pas quelque chose de calibré scientifiquement. Les cétacés ne prennent pas encore de décisions aléatoires, et les plongées sont assez mécaniques.

### 3. Le monde, les zones et les routes (`environment`)

Dans `world.go`, on a créé la structure `World`. C'est elle qui regroupe les dimensions de notre zone, les navires (`Ships`), les cétacés (`Cetaceans`), les zones sensibles (`Zones`) et les routes (`Routes`).

On a plusieurs petites fonctions utiles :

- `World.Contains()` : regarde si une position est à l'intérieur du monde ;
- `Zone.Contains()` : regarde si une position est dans une zone sensible ;
- `World.IsInSensitiveZone()` : vérifie si une position appartient à au moins une zone sensible ;
- `Route.Length()` : calcule la longueur d'une route en additionnant les segments entre ses points (`Waypoints`) ;
- `World.TrouverRoute()` : retrouve une route à partir de son identifiant.

Pour l'instant, une zone sensible est juste un cercle avec un centre et un rayon. C'est pratique pour commencer, même si les vraies zones maritimes seront évidemment plus compliquées.

On a aussi les fonctions pour savoir si un agent est dans les limites du monde, mais **on ne bloque pas encore son déplacement** s'il essaie d'en sortir. Et nos routes ne tiennent pas encore compte des îles ou d'autres obstacles.

### 4. Le moteur et l'horloge (`simulation`)

C'est dans ce dossier qu'on a relié les différents morceaux.

`config.go` contient la structure `Config` :

- `PasTemps` : de combien de secondes simulées on avance à chaque étape ;
- `Duree` : la durée totale de la simulation.

`Validate()` vérifie que ces valeurs sont valides (positives et finies).

Dans `clock.go`, l'horloge garde deux informations : `TempsEcoule` et `Iteration`. La fonction `Advance()` met les deux à jour.

Enfin, `engine.go` contient l'`Engine`. Il connaît notre monde, notre configuration, notre horloge et l'état actuel de la simulation. On a prévu plusieurs états : `ready`, `running`, `paused`, `stopped` et `finished`.

Pour piloter le moteur, on a ajouté `Start()`, `Pause()`, `Resume()` et `Stop()`.

Mais la fonction vraiment centrale, c'est **`Step()`**. À chaque appel :

1. On vérifie que la simulation est bien en cours.
2. On calcule le pas de temps à utiliser (le dernier peut être un peu plus court).
3. On fait avancer tous les navires, en ligne droite ou en suivant leur route.
4. On fait avancer les cétacés, avec leur rotation et leur profondeur.
5. On avance l'horloge.
6. On vérifie si on a atteint la fin de la simulation.

`NewEngine()` vérifie aussi que les routes attribuées aux navires existent.

Un truc important : on simule du **temps virtuel**. Une simulation de 10 secondes n'a pas besoin de prendre 10 secondes en vrai. Le moteur effectue les calculs sans attendre entre les itérations.

### 5. Notre exemple dans `main.go`

Pour vérifier que tout fonctionne ensemble, on a créé un petit monde fictif de **1000 × 1000 m** avec :

- deux navires qui suivent deux routes différentes ;
- un cachalot et un dauphin ;
- une zone sensible circulaire de 150 m de rayon ;
- une simulation de 10 secondes avec un pas de 1 seconde.

Le premier navire suit une route horizontale. Le deuxième commence par se diriger vers le nord, puis tourne vers l'est. Le cachalot plonge et remonte, tandis que le dauphin change progressivement de direction.

Dans le terminal, on affiche les positions et les profondeurs à chaque itération. À la fin, le moteur passe à `finished`.

L'intérêt de cet exemple, c'est qu'on peut déjà tester le moteur sans attendre que le plugin QGIS soit prêt. Par contre, **toutes les données utilisées ici sont fictives**.

## Les tests qu'on a ajoutés

On a créé des fichiers `*_test.go` au fur et à mesure. Ça permet de vérifier qu'on n'a pas cassé une fonction quand on en modifie une autre.

| Partie | Ce qu'on vérifie |
| --- | --- |
| Géométrie | Distances, déplacements vers l'est et le nord, temps nul |
| Agents | Déplacements de base et immobilité d'un cétacé mort |
| Comportements | Suivi d'une route, arrivée, plongée/remontée, rotation |
| Environnement | Position dans le monde, zone sensible, longueur d'une route |
| Moteur | Itérations, horloge, pause/reprise/arrêt, fin de simulation, paramètres invalides |
| Gestion des routes | Suivi d'une route attribuée et erreur si la route n'existe pas |

Les derniers tests lancés pendant le développement sont passés. Ça montre que notre prototype tourne correctement sur les cas testés, mais ça ne veut pas encore dire que la simulation représente fidèlement la réalité.

## Ce qu'il nous reste à faire

### 1. Détecter les collisions (prochaine étape)

C'est la prochaine partie sur laquelle on va travailler. Aujourd'hui, un bateau et un cétacé peuvent se croiser sans que le moteur remarque quoi que ce soit.

Il faudra détecter quand ils sont suffisamment proches, en prenant en compte les dimensions du navire et la profondeur du cétacé. Il faudra aussi regarder ce qui se passe **entre deux positions calculées**, sinon un bateau qui avance vite pourrait passer sur un cétacé entre deux itérations sans que la collision soit détectée.

On devra ensuite enregistrer l'événement (navire, cétacé, position, moment) et faire attention à ne pas compter plusieurs fois la même collision.

### 2. Ajouter la mortalité

On veut bien séparer **collision** et **décès**. Une collision simulée n'entraîne pas forcément la mort du cétacé. Après avoir détecté l'impact, on devra donc estimer la probabilité qu'il soit mortel, en fonction des paramètres qu'on retiendra avec le groupe et des sources scientifiques.

On ne va pas reprendre l'ancien modèle qui utilisait une loi de Poisson pour corriger les collisions non recensées : cette piste a été abandonnée pour notre moteur actuel. On travaille maintenant à partir des déplacements et des interactions entre agents. On pourra quand même utiliser certaines probabilités si elles sont justifiées (esquive, létalité, etc.).

### 3. Calculer des statistiques

Pour comparer des scénarios, il va falloir sortir autre chose que des positions affichées dans un terminal.

On prévoit notamment de calculer le nombre de collisions, la mortalité estimée, la durée et la distance des trajets, les retards, les détours et les zones où les rencontres sont les plus fréquentes.

Il faudra également conserver l'historique des événements et prévoir un export des résultats, en JSON ou en CSV par exemple.

### 4. Tester les stratégies de prévention

Le but final est de comparer quatre scénarios :

| Scénario | Idée |
| --- | --- |
| Normal | Les navires gardent leurs routes et vitesses habituelles |
| Ralentissement | Ils réduisent leur vitesse dans les zones sensibles |
| Déviation | Ils passent par d'autres routes pour éviter certaines zones |
| Combinaison | On applique à la fois le ralentissement et la déviation |

Les routes et les zones sensibles existent déjà dans le code, mais **les stratégies ne sont pas encore programmées**.

Pour que la comparaison soit intéressante, il faudra utiliser des conditions de départ similaires d'un scénario à l'autre. Et si on ajoute de l'aléatoire, on pourra faire plusieurs simulations avec des graines contrôlées pour comparer les résultats correctement.

### 5. Utiliser de vraies données des Canaries

Pour l'instant, on teste surtout des positions inventées dans un carré de 1000 mètres de côté.

La suite sera d'importer des données géographiques et de trafic, choisir un système de coordonnées cohérent pour mesurer les distances en mètres, définir des zones de présence des cétacés et éviter les trajets qui traversent les terres.

Il faudra aussi reprendre les vitesses, les profondeurs et les comportements des animaux avec des données ou hypothèses scientifiques mieux justifiées. Les cercles pour les zones sensibles et les plongées en va-et-vient sont des solutions provisoires.

### 6. Brancher le moteur sur Python et QGIS

Selon l'architecture prévue avec le groupe : **Go fait les calculs**, **Python envoie les commandes et reçoit les données**, puis **QGIS les affiche sur une carte**.

La communication doit passer par :

- une **API REST** pour démarrer, mettre en pause, arrêter ou configurer la simulation et récupérer ses résultats ;
- un **WebSocket** pour envoyer régulièrement les positions, les collisions et les statistiques au plugin Python.

Pour l'instant, il n'y a pas de serveur HTTP ni de WebSocket dans notre partie Go. On devra d'abord se mettre d'accord sur le format des messages JSON avec la personne qui travaille sur le plugin, puis remplir le fichier `contracts/openapi.yaml`.

### 7. Renforcer les tests et regarder les performances

Une fois les collisions et les stratégies codées, il faudra tester davantage de cas, notamment quand beaucoup d'agents se déplacent en même temps, quand une route est vide ou quand un agent sort de la zone de simulation.

On pourra aussi regarder si les goroutines sont utiles pour accélérer certains traitements ou gérer le serveur et les communications. Mais pour l'instant, je préfère garder un moteur séquentiel simple à tester, plutôt que d'ajouter de la concurrence trop tôt.

## Les points sur lesquels il faudra encore se mettre d'accord

Il reste quelques sujets à discuter avec le groupe :

- Le modèle exact pour détecter une collision (seuil de distance, géométrie plus précise du bateau, etc.).
- La façon de représenter les cétacés et leurs comportements, surtout la plongée et l'esquive.
- La formule utilisée pour estimer la mortalité après une collision.
- Les données géographiques et les règles qu'on prendra pour dévier les routes.
- Les formats échangés entre Go et le plugin Python.

Pour le moment, on a fait des choix assez simples pour pouvoir avancer sans être bloqués. On pourra les ajuster quand ces points seront clarifiés.

## Petit bilan

On a déjà une bonne première base : un monde avec des navires et des cétacés, des calculs de déplacement, des routes, une horloge et un moteur qui fait évoluer les agents. On a aussi commencé à ajouter leurs comportements et des tests pour vérifier le fonctionnement.

**La prochaine priorité, c'est la détection des collisions.** Après ça, on pourra s'occuper de la mortalité, des statistiques et des stratégies de prévention. C'est surtout à partir de là qu'on commencera à répondre à la problématique du projet.

Pour le projet dans son ensemble, il y a aussi le [README principal](../README.md) et la [documentation d'architecture](../docs/architecture/README.md).
