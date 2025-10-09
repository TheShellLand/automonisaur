class V1:
    xsoar: str = 'xsoar'
    public: str = f'{xsoar}/public'
    v1: str = f'{public}/v1'


class Reports:
    """xsoar/public/v1/reports"""
    reports: str = f'{V1.v1}/reports'


class Incidents:
    incidents: str = f'{V1.v1}/incident'

    def __init__(self):
        pass

    def get_by_id(self, id: int):
        return f'{V1.v1}/incident/load/{id}'
