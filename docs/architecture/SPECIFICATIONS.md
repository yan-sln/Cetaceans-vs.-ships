#### **Les trois types de messages WebSocket à prévoir**

**1. Initialisation / snapshot**

```
{
  "type": "snapshot",
  "entities": [
    {
      "id": "ship_001",
      "entity_type": "ship",
      "coordinates": {
        "longitude": -15.42,
        "latitude": 28.13
      },
      "rotation": 120.0,
      "extra": {
        "speed": 15.0
      }
    },
    {
      "id": "cetacean_001",
      "entity_type": "cetacean",
      "coordinates": {
        "longitude": -15.40,
        "latitude": 28.15
      },
      "rotation": 90.0,
      "extra": {
        "species": "dolphin"
      }
    }
  ]
}
```

**2. Mise à jour d'une entité**

```
{
  "type": "entity_update",
  "id": "ship_001",
  "entity_type": "ship",
  "coordinates": {
    "longitude": -15.40,
    "latitude": 28.14
  },
  "rotation": 125.0,
  "extra": {
    "speed": 14.5
  }
}
```

**3. Événement de collision**

```
{
  "type": "collision",
  "id": "collision_001",
  "coordinates": {
    "longitude": -15.39,
    "latitude": 28.15
  },
  "extra": {
    "ship_id": "ship_001",
    "cetace_id": "cetacean_001",
    "fatal": false
  }
}
```

L'avantage est que Python n'aura qu'un seul mécanisme de réception et de traitement des messages.

#### Séquence 1 - Chargement du plugin et initialisation

```mermaid
sequenceDiagram
    actor U as Utilisateur
    participant P as Plugin QGIS
    participant UI as SimulationDock
    participant C as SimulationController
    participant LM as LayerManager
    participant SM as ServerManager
    participant G as Moteur Go
    participant H as HttpClient
    participant WS as WebSocketClient
    participant EU as EntityUpdater

    U->>P: Ouvrir le plugin
    P->>UI: Créer le dock
    P->>C: Initialiser le contrôleur
    C->>LM: Préparer les couches QGIS
    LM->>LM: Créer les couches si nécessaire
    C->>SM: Lancer le moteur Go
    SM->>G: Démarrer le processus
    G->>G: Charger les données initiales

    loop Vérification de disponibilité
        C->>H: GET /health
        H->>G: Vérifier disponibilité
        G-->>H: Statut
        H-->>C: Résultat
    end

    C->>WS: Établir la connexion
    WS->>G: Connexion WebSocket
    G-->>WS: Snapshot initial
    WS->>C: Transmettre le snapshot
    C->>EU: Enregistrer les états initiaux
    EU->>LM: Préparer les entités à afficher
    LM->>LM: Créer les features
    C->>UI: Actualiser le statut
    UI-->>U: Moteur prêt
```

#### Séquence 2 - Démarrage et contrôle de la simulation

```mermaid
sequenceDiagram
    actor U as Utilisateur
    participant UI as SimulationDock
    participant C as SimulationController
    participant H as HttpClient
    participant G as Moteur Go
    participant WS as WebSocketClient

    U->>UI: Cliquer sur Play
    UI->>C: start_simulation()
    C->>UI: État pending
    C->>H: POST /simulation/start
    H->>G: Commande de démarrage
    G-->>H: Succès ou erreur
    H-->>C: Résultat

    alt Commande acceptée
        G->>G: Démarrer les goroutines
        G-->>WS: simulation_status = running
        WS->>C: État running
        C->>UI: Afficher running
    else Erreur
        C->>UI: Afficher l'erreur
    end

    opt Pause
        U->>UI: Cliquer sur Pause
        UI->>C: pause_simulation()
        C->>H: POST /simulation/pause
        H->>G: Commande de pause
        G->>G: Bloquer les goroutines
        G-->>H: Succès
        H-->>C: Confirmation
        G-->>WS: simulation_status = paused
        WS->>C: État paused
        C->>UI: Afficher paused
    end

    opt Reprise
        U->>UI: Cliquer sur Resume
        UI->>C: resume_simulation()
        C->>H: POST /simulation/resume
        H->>G: Commande de reprise
        G->>G: Réactiver les goroutines
        G-->>H: Succès
        H-->>C: Confirmation
        G-->>WS: simulation_status = running
        WS->>C: État running
        C->>UI: Afficher running
    end
```

#### Séquence 3 - Actualisation des entités géographiques

```mermaid
sequenceDiagram
    participant G as Moteur Go
    participant WS as WebSocketClient
    participant C as SimulationController
    participant EU as EntityUpdater
    participant T as QTimer
    participant LM as LayerManager
    participant Q as Couches QGIS

    loop Réception des messages WebSocket
        G-->>WS: entity_updates
        WS->>C: Transmettre les changements
        C->>EU: Enregistrer les mises à jour
        EU->>EU: Vérifier les révisions
        EU->>EU: Conserver le dernier état par ID
    end

    opt Suppression d'une entité
        G-->>WS: entity_delete (ID)
        WS->>C: Transmettre la suppression
        C->>EU: Ajouter à la file des suppressions
    end

    opt Événement de collision
        G-->>WS: collision
        WS->>C: Transmettre l'événement
        C->>EU: Ajouter à la file des événements
    end

    loop Toutes les 200 à 500 ms
        T->>EU: Récupérer les changements en attente
        EU-->>T: États, suppressions et événements
        T->>LM: Appliquer le lot
        LM->>Q: Modifier géométries et attributs
        LM->>Q: Supprimer les entités disparues
        LM->>Q: Ajouter les collisions
    end
```

#### Séquence 4 - Redémarrage et purge des entités

```mermaid
sequenceDiagram
    actor U as Utilisateur
    participant UI as SimulationDock
    participant C as SimulationController
    participant H as HttpClient
    participant G as Moteur Go
    participant WS as WebSocketClient
    participant EU as EntityUpdater
    participant LM as LayerManager
    participant Q as Couches QGIS

    U->>UI: Cliquer sur Restart
    UI->>C: restart_simulation()
    C->>UI: État pending
    C->>H: POST /simulation/restart
    H->>G: Commande de redémarrage

    G->>G: Arrêter l'exécution courante
    G->>G: Réinitialiser les agents
    G->>G: Réinitialiser les compteurs
    G->>G: Recharger l'état initial

    G-->>H: Succès ou erreur
    H-->>C: Résultat

    alt Redémarrage accepté
        C->>EU: Vider les états et files en attente
        C->>LM: Purger les données de simulation
        LM->>Q: Supprimer les navires
        LM->>Q: Supprimer les cétacés
        LM->>Q: Supprimer les collisions

        Note over LM,Q: Les routes statiques sont conservées

        G-->>WS: Snapshot initial
        WS->>C: Transmettre le snapshot
        C->>EU: Enregistrer les états initiaux

        loop Prochaine mise à jour QGIS
            C->>EU: Récupérer le snapshot
            EU-->>C: États initiaux
            C->>LM: Recréer les features
            LM->>Q: Afficher les entités initiales
        end

        G-->>WS: simulation_status
        WS->>C: Nouvel état
        C->>UI: Actualiser le statut
    else Erreur
        C->>UI: Afficher l'erreur
    end
```

#### Séquence 5 - Modification d'un paramètre

```mermaid
sequenceDiagram
    actor U as Utilisateur
    participant UI as SimulationDock
    participant C as SimulationController
    participant H as HttpClient
    participant G as Moteur Go

    U->>UI: Modifier un paramètre
    UI->>C: update_parameter(name, value)
    C->>UI: Afficher pending
    C->>H: PUT /simulation/parameters/{name}
    H->>G: Envoyer la nouvelle valeur

    alt Modification acceptée
        G-->>H: Succès
        H-->>C: Confirmation
        C->>C: Enregistrer la valeur confirmée
        C->>UI: Afficher synced
    else Modification refusée
        G-->>H: Erreur
        H-->>C: Message d'erreur
        C->>C: Conserver l'ancienne valeur confirmée
        C->>UI: Afficher error
    end
```

#### Séquence 6 - Déconnexion et resynchronisation

```mermaid
sequenceDiagram
    participant G as Moteur Go
    participant WS as WebSocketClient
    participant C as SimulationController
    participant EU as EntityUpdater
    participant T as QTimer
    participant LM as LayerManager
    participant Q as Couches QGIS
    participant UI as SimulationDock

    G--xWS: Connexion perdue
    WS->>C: Déconnexion détectée
    C->>UI: Afficher disconnected

    loop Tentatives de reconnexion
        WS->>G: Nouvelle connexion
        alt Connexion réussie
            G-->>WS: Connexion établie
        else Échec
            WS->>WS: Attendre avant nouvelle tentative
        end
    end

    G-->>WS: Snapshot complet
    WS->>C: Transmettre le snapshot
    C->>EU: Préparer la resynchronisation

    loop Prochaine mise à jour QGIS
        T->>EU: Récupérer le snapshot
        EU-->>T: État complet des entités
        T->>LM: Réconcilier les entités
        LM->>Q: Mettre à jour les features existantes
        LM->>Q: Ajouter les entités manquantes
        LM->>Q: Supprimer les entités absentes du snapshot
    end

    C->>UI: Afficher connected
```

### **Synthèse des responsabilités**

|Composant|Responsabilité|
|---|---|
|`Plugin`|Cycle de vie du plugin QGIS|
|`SimulationDock`|Interface et interactions utilisateur|
|`SimulationController`|Orchestration générale|
|`ServerManager`|Démarrage et arrêt du processus Go|
|`HttpClient`|Envoi des commandes REST|
|`WebSocketClient`|Réception des messages du moteur|
|`EntityUpdater`|Gestion des changements, suppressions et événements en attente|
|`LayerManager`|Création, modification et suppression des features QGIS|