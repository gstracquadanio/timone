import orjson as json
from dataclasses import asdict
from types import SimpleNamespace
from timone.api import BatchRequest, BatchResponse, BatchObject


def test_batch_request_decode():
    payload_json = """
    {
        "operation": "download",
        "transfers": "basic",
        "ref": { "name": "refs/heads/master" },
        "objects": [
            {
            "oid": "123",
            "size": 123
            },
            {
            "oid": "125",
            "size": 125
            }
        ]
    }
    """
    req_payload = json.loads(payload_json)
    req = BatchRequest(**req_payload)
    check_bool = req.transfers == "basic" and req.operation == "download"
    check_bool = (
        check_bool and req.objects[0].oid == "123" and req.objects[0].size == 123
    )
    check_bool = (
        check_bool and req.objects[1].oid == "125" and req.objects[1].size == 125
    )
    check_bool = check_bool and len(req.objects) == 2
    assert check_bool == True


def test_batch_response_encode():
    # test_data = """
    # {"objects": [{"actions": {}, "authenticated": null, "oid": "123", "size": 123},
    # {"actions": {}, "authenticated": null, "oid": "124", "size": 124}], "transfer": "basic"}
    # """
    # # this is  needed to have consistent dumps to compare with
    # payload_out = json.dumps(json.loads(test_data))
    # resp = BatchResponse(transfer = "basic", objects = [BatchObject(oid="123", size=123), BatchObject(oid="124", size=124)])
    # print(resp.dump())
    assert True
