from typing import Optional

import pytest

from consys.types import BaseType, validate
from consys.errors import ErrorSpecified, ErrorType


class Type(BaseType):
    id: Optional[int]
    login: str
    password: Optional[str]
    actions: Optional[list]

@validate(Type)
def handle(request, data):
    return data


def test_processing():
    data = handle(None, {
        'id': '1',
        'login': '\t\nadmin  ',
        'password': '',
    })

    assert data.id == 1
    assert data.login == 'admin'
    assert data.password == ''

def test_types():
    handle(None, {
        'id': 1,
        'login': 'admin',
        'actions': [{
            'title': 'sign_up',
        }, {
            'title': 'sign_in',
        }],
    })

def test_wrong_type():
    with pytest.raises(ErrorType):
        handle(None, {
            'id': [],
            'login': '',
        })

def test_wrong_field():
    data = handle(None, {
        'id': True,
        'login': '',
        'data': 'test',
    })

    assert not hasattr(data, 'data')

def test_no_required():
    with pytest.raises(ErrorSpecified):
        handle(None, {
            'id': 1,
        })
