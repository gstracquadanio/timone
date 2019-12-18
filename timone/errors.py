class BadRequestException(Exception):

    def __init__(self, repo):
        super()
        self.repo = repo

class UnknownBatchOperationException(Exception):

    def __init__(self, repo, operation):
        super()
        self.repo = repo
        self.operation = operation
