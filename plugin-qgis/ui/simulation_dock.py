# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QLabel,
    QGroupBox,
    QPushButton,
)


class SimulationDock(QDockWidget):
    """Panneau latéral du plugin."""

    serverStartRequested = pyqtSignal()
    startRequested = pyqtSignal()
    pauseRequested = pyqtSignal()
    resumeRequested = pyqtSignal()
    restartRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("Cetaceans vs Ships", parent)

        self.setObjectName("CetaceansVsShipsDock")

        self.container = QWidget(self)
        self.layout = QVBoxLayout(self.container)

        self.title_label = QLabel("<b>Cetaceans vs Ships</b>")
        self.status_label = QLabel("Plugin chargé")
        self.simulation_status_label = QLabel(
            "Serveur non démarré"
        )

        # Serveur
        self.server_group = QGroupBox("Serveur")
        server_layout = QVBoxLayout(self.server_group)

        self.server_button = QPushButton("Démarrer le serveur")
        self.server_button.clicked.connect(
            self.serverStartRequested.emit
        )

        server_layout.addWidget(self.server_button)

        # Simulation
        self.controls_group = QGroupBox("Simulation")
        controls_layout = QVBoxLayout(self.controls_group)
        self.controls_group.setEnabled(False)

        self.start_button = QPushButton("Démarrer")
        self.pause_button = QPushButton("Pause")
        self.resume_button = QPushButton("Reprendre")
        self.restart_button = QPushButton("Réinitialiser")

        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(self.pause_button)
        controls_layout.addWidget(self.resume_button)
        controls_layout.addWidget(self.restart_button)

        self.start_button.clicked.connect(self.startRequested.emit)
        self.pause_button.clicked.connect(self.pauseRequested.emit)
        self.resume_button.clicked.connect(self.resumeRequested.emit)
        self.restart_button.clicked.connect(self.restartRequested.emit)

        # Couches
        self.layers_group = QGroupBox("Couches QGIS")
        self.layers_layout = QVBoxLayout(self.layers_group)

        self.layer_labels = {}

        for layer_name in (
            "routes",
            "ships",
            "cetaceans",
            "collisions",
        ):
            label = QLabel(f"{layer_name} : non initialisée")
            self.layer_labels[layer_name] = label
            self.layers_layout.addWidget(label)

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.simulation_status_label)
        self.layout.addWidget(self.server_group)
        self.layout.addWidget(self.controls_group)
        self.layout.addWidget(self.layers_group)
        self.layout.addStretch()

        self.setWidget(self.container)

    def updateLayerStatus(self, layers):
        for name, layer in layers.items():
            label = self.layer_labels.get(name)

            if label is None:
                continue

            if layer is not None and layer.isValid():
                label.setText(f"{name} : prête")
            else:
                label.setText(f"{name} : erreur")

    def updateSimulationStatus(self, status):
        self.simulation_status_label.setText(status)

    def updateSimulationState(self, state, message):
        """Actualise le statut et les commandes disponibles."""

        self.simulation_status_label.setText(message)

        self.start_button.setEnabled(state == "ready")
        self.pause_button.setEnabled(state == "running")
        self.resume_button.setEnabled(state == "paused")
        self.restart_button.setEnabled(
            state in ("ready", "running", "paused")
        )


    def setServerStarted(self, started):
        """Actualise l'état du serveur et du panneau."""

        self.server_button.setEnabled(not started)

        if started:
            self.server_button.setText("Serveur démarré")
        else:
            self.server_button.setText("Démarrer le serveur")

        self.controls_group.setEnabled(started)

        if not started:
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(False)
            self.resume_button.setEnabled(False)
            self.restart_button.setEnabled(False)