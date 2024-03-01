from werkzeug.exceptions import HTTPException
from flask import make_response
import json


class CategoryNotFoundError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        data = {"error_message" : error_message, "error_code" : error_code}
        self.response = make_response(json.dumps(data), status_code)


class EmptyEntriesError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        data = {"error_message" : error_message, "error_code" : error_code}
        self.response = make_response(json.dumps(data), status_code)


class ProductNotFoundError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        data = {"error_message" : error_message, "error_code" : error_code}
        self.response = make_response(json.dumps(data), status_code)


class UniqueConstraintFailed(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        data = {"error_message" : error_message, "error_code" : error_code}
        self.response = make_response(json.dumps(data), status_code)