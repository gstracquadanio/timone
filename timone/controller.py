import os
import logging
import json
from dataclasses import asdict

import timone
import timone.api as api
from timone.api import (
    BatchBase,
    BatchRequest,
    BatchResponse,
    BatchObject,
    BatchObjectError,
    BatchObjectAction,
)
from timone.errors import (
    BadBatchRequestException,
    UnknownBatchOperationException,
    StorageException,
)
from timone.storage import DumbStorageDriver


class BatchController(object):
    def __init__(self, storage):
        self.storage = storage

    def handle(self, org, repo, request):
        # parsing the Batch API request
        try:
            #  parse the request
            api_request = BatchRequest(**(json.load(request.stream)))
            # check if operation is a valid one
            if (
                api_request.operation == api.BATCH_OPERATION_DOWNLOAD
                or api_request.operation == api.BATCH_OPERATION_UPLOAD
            ):
                # object holding Batch API response
                api_response = BatchResponse(api_request.operation)

                # looping through the objects and adding them to the response
                for obj in api_request.objects:
                    # checking if an object exist
                    obj_exist = self.storage.object_exists(org, repo, obj.oid)
                    # add an upload action if the object does not exist
                    if (
                        api_request.operation == api.BATCH_OPERATION_UPLOAD
                        and not obj_exist
                    ):
                        # add an upload action
                        obj.actions[api_request.operation] = BatchObjectAction(
                            self.storage.get_object_upload_url(org, repo, obj.oid),
                            expires_in=int(
                                os.getenv(
                                    "TIMONE_OBJECT_EXPIRESIN",
                                    timone.DEFAULT_OBJECT_EXPIRESIN,
                                )
                            ),
                        )
                    # if the requests specifies an existing object, add a download action
                    else:
                        # check if it is a download operation
                        if api_request.operation == api.BATCH_OPERATION_DOWNLOAD:
                            # check if the object exist
                            if obj_exist:
                                # add a download action
                                obj.actions[api_request.operation] = BatchObjectAction(
                                    self.storage.get_object_download_url(
                                        org, repo, obj.oid
                                    ),
                                    expires_in=int(
                                        os.getenv(
                                            "TIMONE_OBJECT_EXPIRESIN",
                                            timone.DEFAULT_OBJECT_EXPIRESIN,
                                        )
                                    ),
                                )
                            else:
                                # the object does not exist. Send an object error
                                obj.error = BatchObjectError(
                                    "404",
                                    "Object {} does not exist on {}".format(
                                        obj.oid, repo
                                    ),
                                )
                                logging.debug(
                                    "{} does not exist in {} repo.".format(
                                        obj.oid, repo
                                    )
                                )

                    api_response.objects.append(obj)

                # return JSON encoded response
                return json.dumps(
                    api_response,
                    default=lambda x: x.as_dict()
                    if isinstance(x, BatchBase)
                    else x.__dict__,
                )
            else:
                raise UnknownBatchOperationException(org, repo, api_request.operation)
        except json.JSONDecodeError:
            raise BadBatchRequestException(org, repo)
