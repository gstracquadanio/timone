import os
from pathlib import Path


class Storage(object):
    def __init__(self):
        super()

    def object_exists(self, repo, oid):
        return False

    def get_object_upload_url(self, repo, oid):
        return None

    def get_object_download_url(self, repo, oid):
        return None

    def get_object_uri(self, repo, oid):
        return Path(repo) / oid[:2] / oid[2:4] / oid

    def get_object_path(self, repo, oid, mkdir=False):
        return self.get_object_uri(repo, oid)

class FileSystemStorage(Storage):
    def __init__(self):
        self.url = os.getenv("URL")
        self.base_dir = Path(os.getenv("STORAGE_FS_BASE_DIR"))

    def object_exists(self, repo, oid):
        return (self.base_dir / self.get_object_uri(repo, oid)).exists()

    def get_object_upload_url(self, repo, oid):
        return self.url.format(repo, oid)

    def get_object_download_url(self, repo, oid):
        return self.url.format(repo, oid)

class DumbStorage(Storage):

    def __init__(self):
        super()
        # this is purely for testing purpose
        self.endpoint = os.getenv('TIMONE_ENDPOINT_URL')

    def object_exists(self, repo, oid):
        return True

    def get_object_upload_url(self, repo, oid):
        return "{}/{}/object/{}".format(self.endpoint,repo, oid)

    def get_object_download_url(self, repo, oid):
        return "{}/{}/object/{}".format(self.endpoint,repo, oid)
