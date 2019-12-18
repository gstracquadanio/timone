import json
from dataclasses import asdict

import timone.api as api
from timone.api import (
    BatchRequest,
    BatchResponse,
    BatchObject,
    BatchObjectError,
    BatchObjectAction,
)
from timone.errors import BadRequestException, UnknownBatchOperationException
from timone.storage import DumbStorage


class BatchController(object):
    def __init__(self, storage):
        self.store = storage

    def handle(self, repo, request):
        # parsing the Batch API request
        try:
            api_request = BatchRequest(**(json.load(request.stream)))
            print(api_request.operation)
            if (
                api_request.operation == api.BATCH_OPERATION_DOWNLOAD
                or api_request.operation == api.BATCH_OPERATION_UPLOAD
            ):
                # object holding Batch API response
                api_response = BatchResponse(api_request.operation)

                # looping through the objects and adding them to the response
                for obj in api_request.objects:
                    # checking if an object exist
                    obj_exist = self.store.object_exists(repo, obj.oid)
                    # add an upload action if the object does not exist
                    if (
                        api_request.operation == api.BATCH_OPERATION_UPLOAD
                        and not obj_exist
                    ):
                        obj.actions[api_request.operation] = BatchObjectAction(
                            self.store.get_object_upload_url(repo, obj.oid)
                        )
                    # if the requests specifies an existing object, add a download action
                    else:
                        if obj_exist:
                            obj.actions[api_request.operation] = BatchObjectAction(
                                self.store.get_object_download_url(repo, obj.oid)
                            )
                        else:
                            # the object does not exist. Send an object error
                            obj.error = BatchObjectError(
                                "404",
                                "Object {} does not exist on {}".format(obj.oid, repo),
                            )

                    api_response.objects.append(obj)
                return json.dumps(asdict(api_response))
            else:
                raise UnknownBatchOperationException(repo, api_request.operation)
        except json.JSONDecodeError:
            raise BadRequestException(repo)
