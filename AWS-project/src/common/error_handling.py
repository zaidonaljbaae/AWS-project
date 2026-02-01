#Services
from .custom_exception import CustomException
#Libs
from flask import jsonify

def all_exception_handler(e):
    if isinstance(e, CustomException):
        return jsonify(e.to_dict()), e.status_code
    raise e


def flask_parameter_validation_handler(e):
    raise CustomException(str(e))