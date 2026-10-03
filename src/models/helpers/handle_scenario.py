from enum import Enum


# Api handle scenarios
class HandleScenario(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"