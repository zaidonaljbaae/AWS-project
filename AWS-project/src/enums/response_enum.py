from enum import Enum

class ResponseEnum(Enum):
    SUCCESS = 'Request success'
    CREATED = 'Created'
    NO_CONTENT = 'No content'
    INVALID_INPUT = 'Invalid input'
    BAD_REQUEST = 'Bad request'
    UNAUTHORIZED = 'Unauthorized'
    NOT_FOUND = 'Not found'