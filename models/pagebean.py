class PageBean:
    def __init__(self, data, count):
        self.response: dict[str, any] = {
            "data": data,
            "count": count
        }

    @staticmethod
    def data(data, count):
        return PageBean(data, count).response
