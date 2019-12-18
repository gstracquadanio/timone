import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from timone.errors import StorageException

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


class DumbStorage(Storage):
    def __init__(self):
        super()
        # this is purely for testing
        self.endpoint = os.getenv("TIMONE_ENDPOINT_URL")

    def object_exists(self, repo, oid):
        return True

    def get_object_upload_url(self, repo, oid):
        return "{}/{}/object/{}".format(self.endpoint, repo, oid)

    def get_object_download_url(self, repo, oid):
        return "{}/{}/object/{}".format(self.endpoint, repo, oid)


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


class S3Storage(Storage):
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=os.getenv("TIMONE_STORAGE_S3_URL"),
            aws_access_key_id=os.getenv("TIMONE_STORAGE_S3_KEY"),
            aws_secret_access_key=os.getenv("TIMONE_STORAGE_S3_SECRET"),
        )

    def object_exists(self, repo, oid):
        try:
            uri = str(self.get_object_uri(repo, oid))
            obj_list = self.client.list_objects_v2(
                Bucket=os.getenv("TIMONE_STORAGE_S3_BUCKET"),
                Prefix=uri,
            )
            for obj in obj_list.get('Contents', []):
                if obj['Key'] == uri:
                    return True
        except ClientError as ex:
            raise StorageException()

        return False

    def get_object_upload_url(self, repo, oid):
        try:
            url = self.client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": os.getenv("TIMONE_STORAGE_S3_BUCKET"),
                    "Key": str(self.get_object_uri(repo, oid)),
                },
            )
            return url
        except ClientError:
            raise StorageException()

    def get_object_download_url(self, repo, oid):
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": os.getenv("TIMONE_STORAGE_S3_BUCKET"),
                    "Key": str(self.get_object_uri(repo, oid)),
                },
            )
            return url
        except ClientError:
            raise StorageException()

