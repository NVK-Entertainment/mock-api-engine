from enum import Enum


# Handles methods
class HttpMethods(str, Enum):
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
