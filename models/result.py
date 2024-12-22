class Result:
    def __init__(self, message: str, code: int, data=None):
        self.response: dict[str, any] = {
            "message": message,
            "code": code,
            "data": data
        }

    @staticmethod
    def success(message: str = "操作成功", code: int = 0, data=None):
        return Result(message, code, data).response

    @staticmethod
    def error(message: str = "操作失败", code: int = 1):
        return Result(message, code).response
