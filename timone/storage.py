import os
import sys
import logging
from pathlib import Path
import importlib

import boto3
from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError

import timone
from timone.errors import StorageException


class StorageDriver(object):
    def __init__(self):
        super()

    def object_exists(self, org, repo, obj):
        return False

    def get_object_upload_url(self, org, repo, obj):
        return None

    def get_object_upload_proxy_url(self, org, repo, obj):
        return "{}/{}/{}/{}".format(
            os.getenv("TIMONE_ENDPOINT_URL", timone.DEFAULT_ENDPOINT_URL),
            org,
            repo,
            obj.oid,
        )

    def get_object_download_url(self, org, repo, obj):
        return None

    def get_object_uri(self, org, repo, obj):
        return Path(org) / Path(repo) / obj.oid[:2] / obj.oid[2:4] / obj.oid

    def get_object_path(self, org, repo, obj, mkdir=False):
        return self.get_object_uri(org, repo, obj)

    def upload_object(self, org, repo, obj, data):
        raise NotImplementedError()

    def download_object(self, org, repo, obj):
        raise NotImplementedError()


class StorageDriverFactory(object):
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
            sys.exit(-1)


class DumbStorageDriver(StorageDriver):
    def __init__(self):
        super()
        # this is purely for testing
        self.endpoint = os.getenv("TIMONE_ENDPOINT_URL", timone.DEFAULT_ENDPOINT_URL)

    def object_exists(self, org, repo, obj):
        logging.debug("org: {} repo: {} object: {}.".format(org, repo, obj.oid))
        return False

    def get_object_upload_url(self, org, repo, obj):
        return "{}/{}/{}/{}".format(self.endpoint, org, repo, obj.oid), True

    def get_object_download_url(self, org, repo, obj):
        return "{}/{}/{}/{}".format(self.endpoint, org, repo, obj.oid), True


class S3StorageDriver(StorageDriver):
    def __init__(self):
        self.config = TransferConfig(
            multipart_threshold=int(
                os.getenv("TIMONE_STORAGE_S3_MAX_FILE", timone.DEFAULT_MAX_FILE)
            )
            * timone.DEFAULT_BLOCK_SIZE
        )
        self.client = boto3.client(
            "s3",
            endpoint_url=os.getenv("TIMONE_STORAGE_S3_URL"),
            region_name=os.getenv("TIMONE_STORAGE_S3_REGION"),
            aws_access_key_id=os.getenv("TIMONE_STORAGE_S3_KEY"),
            aws_secret_access_key=os.getenv("TIMONE_STORAGE_S3_SECRET"),
        )

    def object_exists(self, org, repo, obj):
        try:
            uri = str(self.get_object_uri(org, repo, obj))
            obj_list = self.client.list_objects_v2(
                Bucket=os.getenv("TIMONE_STORAGE_S3_BUCKET"), Prefix=uri
            )
            for obj in obj_list.get("Contents", []):
                if obj["Key"] == uri:
                    return True
        except ClientError as ex:
            raise StorageException(org, repo, obj.oid, "object_exists", str(ex))
        return False

    def get_object_upload_url(self, org, repo, obj):
        if obj.size >= self.config.multipart_threshold:
            return self.get_object_upload_proxy_url(org, repo, obj), True
        else:
            try:
                url = self.client.generate_presigned_url(
                    "put_object",
                    Params={
                        "Bucket": os.getenv("TIMONE_STORAGE_S3_BUCKET"),
                        "Key": str(self.get_object_uri(org, repo, obj)),
                    },
                    ExpiresIn=int(
                        os.getenv(
                            "TIMONE_OBJECT_EXPIRESIN", timone.DEFAULT_OBJECT_EXPIRESIN
                        )
                    ),
                )
                return url, False
            except ClientError as ex:
                raise StorageException(
                    org, repo, obj.oid, "get_object_upload_url", str(ex)
                )

    def get_object_download_url(self, org, repo, obj):
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": os.getenv("TIMONE_STORAGE_S3_BUCKET"),
                    "Key": str(self.get_object_uri(org, repo, obj)),
                },
                ExpiresIn=int(
                    os.getenv(
                        "TIMONE_OBJECT_EXPIRESIN", timone.DEFAULT_OBJECT_EXPIRESIN
                    )
                ),
            )
            return url, False
        except ClientError as ex:
            raise StorageException(
                org, repo, obj.oid, "get_object_download_url", str(ex)
            )

    def upload_object(self, org, repo, obj, data):
        try:
            self.client.upload_fileobj(
                data,
                os.getenv("TIMONE_STORAGE_S3_BUCKET"),
                str(self.get_object_uri(org, repo, obj)),
                Config=self.config,
            )
        except ClientError as ex:
            raise StorageException(org, repo, obj.oid, "object_upload_proxy", str(ex))

