from automon.integrations.xsoar.api.v6 import Files


class V1:
    xsoar: str = 'xsoar'
    public: str = f'{xsoar}/public'
    v1: str = f'{public}/v1'


class Incidents:
    incidents: str = f'{V1.v1}/incident'

    def __init__(self):
        pass

    def get_by_id(self, id: int):
        return f'{V1.v1}/incident/load/{id}'


class Reports:
    """xsoar/public/v1/reports"""
    reports: str = f'{V1.v1}/reports'


class Api:
    files = Files()
    incidents = Incidents()
    reports = Reports()
