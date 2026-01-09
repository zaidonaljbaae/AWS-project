#Services
from enum import Enum

class StatusEnum(Enum):
    PROCESSING = 'PROCESSING'
    READY = 'READY'
    FAIL = 'FAIL'
    COMPLETED = 'COMPLETED'
    CLOSED = 'CLOSED'
    PENDING = 'PENDING'
    OPEN = 'OPEN'
    REQUEST_APPROVAL = 'REQUEST APPROVAL'
    APPROVED = 'APPROVED'