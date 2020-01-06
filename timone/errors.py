class BadBatchRequestException(Exception):
    def __init__(self, org, repo, message=None):
        super()
        self.org = org
        self.repo = repo
        self.message = message


class UnknownBatchOperationException(Exception):
    def __init__(self, org, repo, operation, message=None):
        super()
        self.org = org
        self.repo = repo
        self.operation = operation


class StorageException(Exception):
    def __init__(self, org, repo, oid, operation, message=None):
        super()
        self.org = org
        self.repo = repo
        self.oid = oid
        self.operation = operation
        self.message = message


class AuthException(Exception):
    def __init__(self, message=None):
        self.message = message

