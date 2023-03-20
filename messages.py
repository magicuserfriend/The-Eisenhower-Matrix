class Request:
    def __init__(self, method, target, version, headers, query=None, body=None):
        self.method = method
        self.target = target
        self.version = version
        self.headers = headers
        self.query = query
        self.body = body

class Response:
    def __init__(self, status, reason, headers=None, body=None):
        self.status = status
        self.reason = reason
        self.headers = headers
        self.body = body
