#Services
from enum import Enum
import os

class EnvEnum(Enum):
    ENV = os.getenv("ENV")
    ACCOUNT_ID = os.getenv("ACCOUNT_ID")
 