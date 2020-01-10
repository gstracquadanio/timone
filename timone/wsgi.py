import os
import logging
import falcon
import json
import base64
import importlib
from dataclasses import asdict

from dotenv import load_dotenv

import timone
import timone.api as api
from timone.api import BatchRequest, BatchResponse, BatchObject
from timone.controller import BatchController
from timone.errors import (
    BadBatchRequestException,
    UnknownBatchOperationException,
    StorageException,
)
from timone.storage import DumbStorageDriver, S3StorageDriver, StorageDriverFactory
from timone.auth import TokenAuthMiddleware


class BatchObjectResource(object):
    def __init__(self, controller):
        self.controller = controller

    def on_post(self, req, resp, org, repo):
        # dispatching request to the controller
        try:
            # processing request
            api_response = self.controller.handle(org, repo, req)
            resp.status = falcon.HTTP_200
            resp.content_type = api.BATCH_CONTENT_TYPE
            resp.body = api_response
        except BadBatchRequestException as ex:
            logging.debug(str(ex))
            # error decoding the request
            resp.status = falcon.HTTP_501
        except UnknownBatchOperationException as ex:
            # request decoded, but action unknown
            logging.debug(str(ex))
            resp.status = falcon.HTTP_501
        except StorageException as ex:
            # something wrong happend while access
            # an object
            logging.debug(str(ex))
            resp.status = falcon.HTTP_501


class BatchObjectStorageResource(object):
    def __init__(self, storage):
        self.storage = storage

    def on_get(self, req, resp, org, repo, oid):
        try:
            logging.debug("Downloading: {}".format(oid))
            obj = BatchObject(oid=oid, size=req.content_length)
            self.storage.download_object(org, repo, obj)
            resp.status = falcon.HTTP_200
        except StorageException as ex:
            # something wrong happend while access
            # an object
            logging.debug(str(ex))
            resp.status = falcon.HTTP_501
        except NotImplementedError:
            logging.debug("Download not implemented")
            resp.status = falcon.HTTP_501

    def on_put(self, req, resp, org, repo, oid):
        try:
            logging.debug("Uploading: {}".format(oid))
            obj = BatchObject(oid=oid, size=req.content_length)
            self.storage.upload_object(org, repo, obj, req.stream)
            resp.status = falcon.HTTP_200
        except StorageException as ex:
            # something wrong happend while access
            # an object
            logging.debug(str(ex))
            resp.status = falcon.HTTP_501
        except NotImplementedError:
            logging.debug("Upload not implemented")
            resp.status = falcon.HTTP_501

class BatchObjectLockResource(object):

    def on_post(self, req, resp, org, repo):
        resp.status = falcon.HTTP_501

def run():
    # booting the logger
    logging.basicConfig(
        format="[%(asctime)s] [%(process)d] [%(module)s.%(funcName)s] [%(levelname)s] %(message)s",
        level=logging.getLevelName(
            os.getenv("TIMONE_LOG_LEVEL", timone.DEFAULT_LOG_LEVEL)
        ),
    )

    # loading the environment variables
    load_dotenv()
    # get storage instance
    storage = StorageDriverFactory.get_storage()
    # build new controller
    controller = BatchController(storage())
    # build new BatchObjectResource
    resource = BatchObjectResource(controller)
    # proxy for Large Batch Object
    storage_proxy = BatchObjectStorageResource(storage())
    # build REST endpoint
    server = falcon.API(middleware=TokenAuthMiddleware())
    # add Batch API route
    server.add_route("/{org}/{repo}/info/lfs/objects/batch", resource)
    # add proxy multipart
    server.add_route("/{org}/{repo}/{oid}", storage_proxy)
    #
    server.add_route("/{org}/{repo}/info/lfs/locks/verify", BatchObjectLockResource())
    # return app to the WSGI server
    return server
