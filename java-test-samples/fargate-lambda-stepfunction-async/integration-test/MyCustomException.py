class MyCustomException(Exception):
    def __init__(self, message="Default error message"):
        self.message = message
        super().__init__(self.message)