from typing import Type

from fastapi.responses import JSONResponse
from fastapi import status 


class BaseException(Exception):
    def __init__(self):
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.message = "Unknown Error"
    
    def __str__(self):
        return self.message

    def response(self):
        return JSONResponse(
            status_code=self.status_code,
            content={"message": self.message},
        )

class ValidationErr(BaseException):
    def __init__(self):
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        self.message = "Bad Request"
    
class AuthErr(BaseException):
    def __init__(self):
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        self.message = "CMT auth failed"
    
