class ResponseError(Exception):
    def __init__(self, response):
        self.response = response

    def __str__(self):
        return self.response

class RequestError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class AuthenticationError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class TransactionError(Exception):
    def __init__(self, transaction_type):
        self.transaction_type = transaction_type

    def __str__(self):
        msg = "The transaction '{0}' is not available".format(self.transaction_type)
        return msg

