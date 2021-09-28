from ._db import get_db
from .base import BaseModel


def make_base(host, name, login=None, password=None):
    class Base(BaseModel):
        _db = get_db(host, name, login, password)

    return Base
