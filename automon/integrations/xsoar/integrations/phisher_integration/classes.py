## DEMISTO MOCK CLASSES FOR LOCAL DEBUGGING
try:
    from automon.integrations.xsoar.local_testing import *
    from automon.integrations.xsoar.demistoWrapper.funcs import *
    # from local_dev.common import *
except:
    pass


class PhisherHeader(Dict):
    data: str
    header: str
    order: str

    def __init__(self, header: dict = None):
        super().__init__()

        if header:
            self.update(header)

    def __repr__(self):
        return f"{self.order} :: {self.header} :: {self.data}"

    def __lt__(self, other) -> bool:
        if not isinstance(other, PhisherHeader):
            raise Exception(f"{type(other)=} is not PhisherHeader")

        if int(self.order) < int(other.order):
            return True
        return False

    def __bool__(self) -> bool:
        if self.header and self.data:
            return True
        return False

    def __eq__(self, other):
        if not isinstance(other, PhisherHeader):
            raise Exception(f"{type(other)=} is not PhisherHeader")

        if self.header == other.header:
            if self.data == other.data:
                return True
        return False


class PhisherMessage(Dict):
    id: str
    headers: list

    def __init__(self, message: dict = None):
        super().__init__()

        if message:
            self.update(message)

    def __bool__(self):
        if self.id:
            return True
        return False

    @property
    def automon_headers(self) -> list[PhisherHeader]:
        return [PhisherHeader(x) for x in self.headers]

    def automon_get_header_name(self, header: str) -> list[PhisherHeader]:
        results = []
        for header in self.automon_headers:
            if str(header).lower() in header.header.lower():
                debug(f"[PhisherMessage] :: automon_get_header_name :: FOUND :: {header}")
                results.append(header)
        return results

    def automon_get_header_data(self, data: str) -> list[PhisherHeader]:
        results = []
        for header in self.automon_headers:
            if str(data).lower() in header.data.lower():
                debug(f"[PhisherMessage] :: automon_get_header_data :: FOUND :: {header}")
                results.append(header)
        return results

    def automon_search_headers(self, search: str) -> list[PhisherHeader]:
        results = []
        results.extend(self.automon_get_header_name(search))
        results.extend(self.automon_get_header_data(search))
        filtered = []
        for result in results:
            if result not in filtered:
                filtered.append(result)
        return filtered


class Phisher(Dict):
    Message: dict

    def __init__(self, phisher: dict = None):
        super().__init__()

        if phisher:
            self.update(phisher)

    @property
    def automon_Message(self) -> PhisherMessage:
        return PhisherMessage(self.Message)
