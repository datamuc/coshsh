from monitoring_detail import MonitoringDetail

def __detail_ident__(params={}): 
    if params["monitoring_type"] == "VOLUME":
        return MonitoringDetailVolume


class MonitoringDetailVolume(MonitoringDetail):
    """
    """
    property = "volumes"
    property_type = list

    def __init__(self, params):
        self.monitoring_type = params["monitoring_type"]
        self.name = params["monitoring_0"]
        self.warning = params.get("monitoring_1", "10")
        self.critical = params.get("monitoring_2", "5")
        self.units = params.get("monitoring_3", "%")

    def __str__(self):
        return "%s %s:%s:0:100" % (self.name, self.warning, self.critical)

