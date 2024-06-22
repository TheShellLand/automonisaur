class V1:
    xsoar: str = 'xsoar'
    public: str = f'{xsoar}/public'
    v1: str = f'{public}/v1'


class Reports:
    """xsoar/public/v1/reports"""
    reports: str = f'{V1.v1}/reports'
