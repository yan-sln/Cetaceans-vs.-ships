def classFactory(iface):
    """Entry point required by QGIS to load the plugin."""
    from .main import Plugin
    return Plugin(iface)