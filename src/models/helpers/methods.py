from enum import Enum


# Handles methods
class Methods(str, Enum):
    GET = "get"
    POST = "post"
    PATCH = "patch"
    PUT = "put"
    DELETE = "delete"
    OPTIONS = "options"
