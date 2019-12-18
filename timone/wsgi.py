import logging
import falcon
import json
from dataclasses import asdict

from dotenv import load_dotenv

import timone.api as api
from timone.api import BatchRequest, BatchResponse
from timone.controller import BatchController
from timone.errors import BadRequestException, UnknownBatchOperationException
from timone.storage import DumbStorage



class BatchObjectResource(object):
    def __init__(self, controller):
        self.controller = controller

    def on_post(self, req, resp, repo=None):
        # dispatching request to the controller
        try:
            api_response = self.controller.handle(repo, req)
            resp.status = falcon.HTTP_200
            resp.content_type = api.BATCH_CONTENT_TYPE
            resp.body = api_response
        except BadRequestException:
            # error decoding the request
            resp.status = falcon.HTTP_501
        except UnknownBatchOperationException:
            # request decoded, but action unkown
            resp.status = falcon.HTTP_501

load_dotenv(verbose=True)
storage = DumbStorage()
controller = BatchController(storage)
resource = BatchObjectResource(controller)
server = falcon.API()
server.add_route("/{repo}/info/lfs/objects/batch", resource)
