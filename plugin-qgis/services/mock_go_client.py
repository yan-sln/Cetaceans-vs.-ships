# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QObject, QTimer, pyqtSignal


class MockGoClient(QObject):
    """Simulation temporaire de l'interface du moteur Go."""

    messageReceived = pyqtSignal(dict)
    statusChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.connected = False
        self.running = False
        self.simulation_time = 0.0
        self.revision = 0
        self.tick_count = 0

        self.ship_longitude = -15.42
        self.ship_latitude = 28.13

        self.needs_snapshot = False

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self._generate_update)


    def connect_mock(self):
        """Simule la connexion et envoie le snapshot initial."""

        self.connected = True
        self.statusChanged.emit("Connecté au moteur mock")

        self.messageReceived.emit({
            "type": "entity_updates",
            "entities": self._initial_entities(),
        })


    def start_simulation(self):
        if not self.connected:
            return False

        # Après une réinitialisation, renvoyer les entités
        # au prochain démarrage de la simulation.
        if self.needs_snapshot:
            self.messageReceived.emit({
                "type": "entity_updates",
                "entities": self._initial_entities(),
            })
            self.needs_snapshot = False

        self.running = True
        self.timer.start()
        self.statusChanged.emit("Simulation en cours")
        return True

    def pause_simulation(self):
        self.running = False
        self.timer.stop()
        self.statusChanged.emit("Simulation en pause")
        return True

    def resume_simulation(self):
        return self.start_simulation()

    def restart_simulation(self):
        self.timer.stop()
        self.running = False

        self.simulation_time = 0.0
        self.revision = 0
        self.tick_count = 0

        self.ship_longitude = -15.42
        self.ship_latitude = 28.13

        # Ne pas envoyer de snapshot maintenant :
        # les couches doivent rester vides après réinitialisation.
        self.needs_snapshot = True

        self.statusChanged.emit("Simulation réinitialisée")
        return True

    def set_parameter(self, name, value):
        """Accepte temporairement un paramètre sans calcul métier."""

        self.statusChanged.emit(
            f"Paramètre mock reçu : {name} = {value}"
        )
        return True

    def disconnect_mock(self):
        self.timer.stop()
        self.running = False
        self.connected = False
        self.statusChanged.emit("Déconnecté du moteur mock")

    def _initial_entities(self):
        return [
            {
                "id": "ship_001",
                "entity_type": "ship",
                "coordinates": {
                    "longitude": self.ship_longitude,
                    "latitude": self.ship_latitude,
                },
                "rotation": 90.0,
                "extra": {
                    "speed": 12.0,
                    "length": 120.0,
                },
                "revision": self.revision,
            },
            {
                "id": "cetacean_001",
                "entity_type": "cetacean",
                "coordinates": {
                    "longitude": -15.45,
                    "latitude": 28.16,
                },
                "rotation": 45.0,
                "extra": {
                    "speed": 3.0,
                    "size": 8.0,
                },
                "revision": self.revision,
            },
        ]

    def _generate_update(self):
        if not self.running:
            return

        self.tick_count += 1
        self.simulation_time += 0.1
        self.revision += 1

        # Déplacement fictif du navire pour tester l'affichage.
        self.ship_longitude += 0.0002

        self.messageReceived.emit({
            "type": "entity_updates",
            "entities": [
                {
                    "id": "ship_001",
                    "entity_type": "ship",
                    "coordinates": {
                        "longitude": self.ship_longitude,
                        "latitude": self.ship_latitude,
                    },
                    "rotation": 90.0,
                    "extra": {
                        "speed": 12.0,
                        "length": 120.0,
                    },
                    "revision": self.revision,
                }
            ],
        })

        # Un événement fictif, envoyé une seule fois.
        if self.tick_count == 40:
            self.messageReceived.emit({
                "type": "collision",
                "event": {
                    "event_id": "collision_mock_001",
                    "ship_id": "ship_001",
                    "cetacean_id": "cetacean_001",
                    "simulation_time": self.simulation_time,
                    "fatal": False,
                    "coordinates": {
                        "longitude": self.ship_longitude,
                        "latitude": self.ship_latitude,
                    },
                },
            })