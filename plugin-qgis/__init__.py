# -*- coding: utf-8 -*-

from .main import CetaceansVsShipsPlugin

def classFactory(iface):
    """Point d'entrée du plugin QGIS."""
    return CetaceansVsShipsPlugin(iface)