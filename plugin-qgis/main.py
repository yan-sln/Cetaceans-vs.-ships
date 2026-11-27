# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QAction

from .services.layer_manager import LayerManager
from .ui.simulation_dock import SimulationDock
from .controllers.simulation_controller import SimulationController


class CetaceansVsShipsPlugin:
    """Classe principale du plugin QGIS."""

    def __init__(self, iface):
        self.iface = iface
        self.layer_manager = None
        self.dock = None
        self.controller = None
        self.action = None

    def initGui(self):
        # Le gestionnaire existe, mais ne crée aucune couche.
        self.layer_manager = LayerManager()

        self.dock = SimulationDock(self.iface.mainWindow())

        self.iface.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea,
            self.dock
        )
        self.dock.hide()

        self.controller = SimulationController(
            self.layer_manager,
            self.dock,
            self.iface,
        )

        self.controller.initialize()

        self.action = QAction(
            "Cetaceans vs Ships",
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)

        self.iface.addPluginToMenu(
            "&Cetaceans vs Ships",
            self.action
        )
        self.iface.addToolBarIcon(self.action)

    def run(self):
        if self.dock is not None:
            self.dock.show()
            self.dock.raise_()

    def unload(self):
        if self.controller is not None:
            self.controller.shutdown()
            self.controller = None

        if self.action is not None:
            self.iface.removePluginMenu(
                "&Cetaceans vs Ships",
                self.action
            )
            self.iface.removeToolBarIcon(self.action)
            self.action = None

        if self.dock is not None:
            self.iface.removeDockWidget(self.dock)
            self.dock.deleteLater()
            self.dock = None

        self.layer_manager = None