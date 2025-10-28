from .ofdsqgisplugin.plugin import OFDSQGISPlugin


def classFactory(iface):
    return OFDSQGISPlugin(iface)
