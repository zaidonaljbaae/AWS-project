class CustomException(Exception):
    
    status_code = 400
    is_custom = True

    def __init__(self, message, status_code=None, is_custom=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if is_custom is not None:
            self.is_custom = is_custom

    def to_dict(self):       
        body = dict()
        body['message'] = self.message
        body['is_custom'] = self.is_custom
        error = dict()
        error['error'] = body
        return error