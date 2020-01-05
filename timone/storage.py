import os
import logging
from pathlib import Path
import importlib

import boto3
from botocore.exceptions import ClientError

import timone
from timone.errors import StorageException


class StorageSystem(object):
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


class StorageFactory(object):
    @staticmethod
    def get_storage():
        # loading the storage system to use
        try:
            storage = getattr(
                importlib.import_module("timone.storage"),
                os.getenv("TIMONE_STORAGE", timone.DEFAULT_STORAGE),
            )
            return storage
        except AttributeError as ex:
            logging.error(
                "Cannot find storage driver: {}.".format(os.getenv("TIMONE_STORAGE"))
            )


class DumbStorage(StorageSystem):
    def __init__(self):
        super()
        # this is purely for testing
        self.endpoint = os.getenv("TIMONE_ENDPOINT_URL", timone.DEFAULT_ENDPOINT_URL)

    def object_exists(self, repo, oid):
        logging.debug("repo: {} object: {}.".format(repo, oid))
        return True

    def get_object_upload_url(self, repo, oid):
        return "{}/{}/object/{}".format(self.endpoint, repo, oid)

    def get_object_download_url(self, repo, oid):
        return "{}/{}/object/{}".format(self.endpoint, repo, oid)


class FileSystemStorage(StorageSystem):
    def __init__(self):
        self.url = os.getenv("URL")
        self.base_dir = Path(os.getenv("STORAGE_FS_BASE_DIR"))

    def object_exists(self, repo, oid):
        return (self.base_dir / self.get_object_uri(repo, oid)).exists()

    def get_object_upload_url(self, repo, oid):
        return self.url.format(repo, oid)

    def get_object_download_url(self, repo, oid):
        return self.url.format(repo, oid)


class S3Storage(StorageSystem):
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=os.getenv("TIMONE_STORAGE_S3_URL"),
            region_name=os.getenv("TIMONE_STORAGE_S3_REGION"),
            aws_access_key_id=os.getenv("TIMONE_STORAGE_S3_KEY"),
            aws_secret_access_key=os.getenv("TIMONE_STORAGE_S3_SECRET"),
        )

    def object_exists(self, repo, oid):
        try:
            uri = str(self.get_object_uri(repo, oid))
            obj_list = self.client.list_objects_v2(
                Bucket=os.getenv("TIMONE_STORAGE_S3_BUCKET"), Prefix=uri
            )
            for obj in obj_list.get("Contents", []):
                if obj["Key"] == uri:
                    return True
        except ClientError as ex:
            raise StorageException(repo, oid, "object_exists", str(ex))
        return False

    def get_object_upload_url(self, repo, oid):
        try:
            url = self.client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": os.getenv("TIMONE_STORAGE_S3_BUCKET"),
                    "Key": str(self.get_object_uri(repo, oid)),
                },
                ExpiresIn=int(
                    os.getenv(
                        "TIMONE_OBJECT_EXPIRESIN", timone.DEFAULT_OBJECT_EXPIRESIN
                    )
                ),
            )
            return url
        except ClientError as ex:
            raise StorageException(repo, oid, "get_object_upload_url", str(ex))

    def get_object_download_url(self, repo, oid):
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": os.getenv("TIMONE_STORAGE_S3_BUCKET"),
                    "Key": str(self.get_object_uri(repo, oid)),
                },
                ExpiresIn=int(
                    os.getenv(
                        "TIMONE_OBJECT_EXPIRESIN", timone.DEFAULT_OBJECT_EXPIRESIN
                    )
                ),
            )
            return url
        except ClientError as ex:
            raise StorageException(repo, oid, "get_object_download_url", str(ex))
