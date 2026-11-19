"""Plugin — main plugin class.

A mock dock panel.
"""

import os

from qgis.PyQt.QtCore import Qt, QTimer, pyqtSignal
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import (
    QAction, QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QRadioButton, QButtonGroup, QPushButton, QGroupBox, QPlainTextEdit,
    QCheckBox,
)
from qgis.core import (
    QgsProject, QgsCoordinateReferenceSystem, QgsCoordinateTransform,
    QgsRectangle, QgsPointXY, QgsWkbTypes, QgsMessageLog, Qgis,
)
from qgis.gui import (
    QgsMapTool, QgsRubberBand, QgsCollapsibleGroupBox, QgsHighlight,
)

class Plugin:
    def __init__(self, iface):
        pass