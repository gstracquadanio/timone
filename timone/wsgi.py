import os
import logging
import falcon
import json
import base64
import importlib
from dataclasses import asdict

from dotenv import load_dotenv

import timone.api as api
from timone.api import BatchRequest, BatchResponse
from timone.controller import BatchController
from timone.errors import (
    BadBatchRequestException,
    UnknownBatchOperationException,
    StorageException,
)
from timone.storage import DumbStorage, S3Storage
from timone.auth import TokenAuthMiddleware


class BatchObjectResource(object):
    def __init__(self, controller):
        self.controller = controller

    def on_post(self, req, resp, repo=None):
        # dispatching request to the controller
        try:
            # processing request
            api_response = self.controller.handle(repo, req)
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


def run():
    # booting the logger
    logging.basicConfig(
        format="[%(asctime)s] [%(process)d] [%(module)s.%(funcName)s] [%(levelname)s] %(message)s",
        level=logging.DEBUG,
    )

    load_dotenv()
    storage = getattr(
        importlib.import_module("timone.storage"), os.getenv("TIMONE_STORAGE")
    )
    controller = BatchController(storage())
    resource = BatchObjectResource(controller)
    server = falcon.API(middleware=[TokenAuthMiddleware()])
    server = falcon.API()
    server.add_route("/{repo}/info/lfs/objects/batch", resource)
    return server
