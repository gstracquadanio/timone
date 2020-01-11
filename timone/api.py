from dataclasses import dataclass, field, asdict
from typing import List
import json

BATCH_CONTENT_TYPE: str = "application/vnd.git-lfs+json"
BATCH_OPERATION_DOWNLOAD: str = "download"
BATCH_OPERATION_UPLOAD: str = "upload"
BATCH_TRANSFER_BASIC: str = "basic"


@dataclass
class BatchBase(object):
    def as_dict(self):
        return {k: v for k,v in self.__dict__.items() if v is not None}


@dataclass
class BatchObjectAction(BatchBase):
    href: str
    header: str = field(default=None)
    expires_in: str = field(default=None)
    expires_at: str = field(default=None)


@dataclass
class BatchObjectError(BatchBase):
    code: str
    message: str


@dataclass
class BatchObject(BatchBase):
    oid: str = field(default=None)
    size: int = field(default=None)
    authenticated: bool = field(default=True)
    actions: dict = field(default_factory=dict)
    error: BatchObjectError = field(default=None)


@dataclass
class BatchRequest(BatchBase):
    operation: str = field(default=None)
    transfers: str = BATCH_TRANSFER_BASIC
    ref: str = field(default=None)
    objects: List[BatchObjectAction] = field(default=None)

    def __post_init__(self):
        self.objects = [BatchObject(**_) for _ in self.objects]


@dataclass
class BatchResponse(BatchBase):
    operation: str = field(default=None)
    transfer: str = BATCH_TRANSFER_BASIC
    objects: List[BatchObject] = field(default_factory=list)
