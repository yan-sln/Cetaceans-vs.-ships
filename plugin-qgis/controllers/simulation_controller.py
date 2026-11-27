# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QObject, QTimer
from qgis.core import (
    QgsCoordinateTransform,
    QgsProject,
    QgsRectangle,
)

from ..services.entity_updater import EntityUpdater
from ..services.mock_go_client import MockGoClient


class SimulationController(QObject):
    """Coordonne le moteur, les données reçues et les couches QGIS."""

    def __init__(self, layer_manager, dock, iface, parent=None):
        super().__init__(parent)

        self.layer_manager = layer_manager
        self.dock = dock
        self.iface = iface

        self.client = MockGoClient(self)
        self.entity_updater = EntityUpdater()

        self.server_started = False

        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(100)
        self.refresh_timer.timeout.connect(
            self.flush_pending_updates
        )

        self.client.messageReceived.connect(
            self.handle_message
        )
        self.simulation_state = "stopped"

        self.client.statusChanged.connect(
            self.handle_status_changed
        )

        self.dock.serverStartRequested.connect(
            self.start_server
        )
        self.dock.startRequested.connect(
            self.start_simulation
        )
        self.dock.pauseRequested.connect(
            self.pause_simulation
        )
        self.dock.resumeRequested.connect(
            self.resume_simulation
        )
        self.dock.restartRequested.connect(
            self.restart_simulation
        )

    def initialize(self):
        """Aucune couche ni connexion créée au chargement du plugin."""
        pass

    def start_server(self):
        """Démarre le mock et prépare les couches QGIS."""

        if self.server_started:
            return

        # Création des quatre couches.
        layers = self.layer_manager.initializeLayers()
        self.dock.updateLayerStatus(layers)

        # Préparation du rafraîchissement à 10 Hz.
        self.refresh_timer.start()

        # Connexion au mock et réception du snapshot initial.
        self.client.connect_mock()

        self.server_started = True
        self.dock.setServerStarted(True)

        # Appliquer immédiatement les entités initiales.
        self.flush_pending_updates()

        # Centrer la carte sur les entités reçues.
        self.zoom_to_entities()

    def handle_message(self, message):
        self.entity_updater.enqueue_message(message)

    def flush_pending_updates(self):
        if not self.entity_updater.has_pending_updates():
            return

        batch = self.entity_updater.take_pending_batch()
        self.layer_manager.applyBatch(batch)

    def start_simulation(self):
        if not self.server_started:
            return

        if self.simulation_state != "ready":
            return

        self.client.start_simulation()


    def pause_simulation(self):
        if not self.server_started:
            return

        if self.simulation_state != "running":
            return

        self.client.pause_simulation()


    def resume_simulation(self):
        if not self.server_started:
            return

        if self.simulation_state != "paused":
            return

        self.client.resume_simulation()


    def restart_simulation(self):
        if not self.server_started:
            return

        # Arrêter le mouvement uniquement si nécessaire.
        if self.simulation_state == "running":
            self.client.pause_simulation()

        # Supprimer les messages qui n'ont pas encore été appliqués.
        self.entity_updater.clear()

        # Vider les quatre couches, routes comprises.
        self.layer_manager.clearAllLayers()

        # Réinitialiser le mock.
        # Le snapshot sera envoyé au prochain démarrage.
        self.client.restart_simulation()

    def update_parameter(self, name, value):
        if self.server_started:
            self.client.set_parameter(name, value)

    def shutdown(self):
        self.refresh_timer.stop()
        self.client.disconnect_mock()
        self.entity_updater.clear()

        self.server_started = False
        self.simulation_state = "stopped"

        self.dock.setServerStarted(False)
        self.dock.updateSimulationState(
            "stopped",
            "Serveur arrêté",
        )
    
    def zoom_to_entities(self):
        """Centre la carte sur les couches des entités."""

        canvas = self.iface.mapCanvas()
        project = QgsProject.instance()

        layers = (
            self.layer_manager.ships_layer,
            self.layer_manager.cetaceans_layer,
        )

        destination_crs = canvas.mapSettings().destinationCrs()
        transform_context = project.transformContext()

        combined_extent = None

        for layer in layers:
            if layer is None or not layer.isValid():
                continue

            if layer.featureCount() == 0:
                continue

            transform = QgsCoordinateTransform(
                layer.crs(),
                destination_crs,
                transform_context,
            )

            layer_extent = transform.transformBoundingBox(
                layer.extent()
            )

            if combined_extent is None:
                combined_extent = QgsRectangle(layer_extent)
            else:
                combined_extent.combineExtentWith(layer_extent)

        if combined_extent is None:
            return

        # Ajouter une marge autour des entités.
        width = max(combined_extent.width(), 0.02)
        height = max(combined_extent.height(), 0.02)

        margin_x = width * 0.25
        margin_y = height * 0.25

        extent = QgsRectangle(
            combined_extent.xMinimum() - margin_x,
            combined_extent.yMinimum() - margin_y,
            combined_extent.xMaximum() + margin_x,
            combined_extent.yMaximum() + margin_y,
        )

        canvas.setExtent(extent)
        canvas.refresh()

    def handle_status_changed(self, status):
        """Met à jour l'état de la simulation dans le panneau."""

        if status == "Connecté au moteur mock":
            self.simulation_state = "ready"

        elif status == "Simulation en cours":
            self.simulation_state = "running"

        elif status == "Simulation en pause":
            self.simulation_state = "paused"

        elif status == "Simulation réinitialisée":
            self.simulation_state = "ready"

        elif status == "Déconnecté du moteur mock":
            self.simulation_state = "stopped"

        self.dock.updateSimulationState(
            self.simulation_state,
            status,
        )