import time
import json

import pytest

from . import Base, Attribute
from consys.errors import ErrorInvalid


class ObjectModel(Base):
    _name = 'tests'

    meta = Attribute(types=str)
    delta = Attribute(types=str, default='')
    extra = Attribute(types=str, default=lambda instance: f'u{instance.delta}o')
    teta = Attribute(types=str, ignore=True)
    multi = Attribute(types=list, default=[])
    pompa = Attribute()
    tulpa = Attribute(types=int)
    rampa = Attribute(types=int, ignore=True)


def test_attr():
    now = time.time()
    instance = ObjectModel()

    assert instance.id == 0
    assert instance.title is None
    assert instance.user == 0
    assert instance.created < now + 1
    assert instance.updated is None
    assert instance.status is None
    assert instance.meta is None
    assert instance.delta == ''
    assert instance.extra == 'uo'

    with pytest.raises(AttributeError):
        assert instance.undefined_field

def test_item():
    now = time.time()
    instance = ObjectModel()

    assert instance['id'] == 0
    assert instance['title'] is None
    assert instance['user'] == 0
    assert instance['created'] < now + 1
    assert instance['updated'] is None
    assert instance['status'] is None
    assert instance['meta'] is None
    assert instance['delta'] == ''
    assert instance['extra'] == 'uo'

    with pytest.raises(AttributeError):
        assert instance['undefined_field']

def test_data():
    now = time.time()
    instance = ObjectModel({
        'id': 1,
        'title': 'test_data',
        'user': 2,
        'status': 3,
        'meta': 'onigiri',
        'delta': 'hinkali',
        'extra': 'ramen',
    })

    assert instance.id == 1
    assert instance.title == 'test_data'
    assert instance.created < now + 1
    assert instance.user == 2
    assert instance.status == 3
    assert instance.meta == 'onigiri'
    assert instance.delta == 'hinkali'
    assert instance.extra == 'ramen'

def test_kwargs():
    now = time.time()
    instance = ObjectModel(
        id=1,
        title='test_kwargs',
        user=2,
        status=3,
        meta='oNiGiRi',
        delta='HINKali',
        extra='RAMEN',
    )

    assert instance.id == 1
    assert instance.title == 'test_kwargs'
    assert instance.created < now + 1
    assert instance.user == 2
    assert instance.status == 3
    assert instance.meta == 'oNiGiRi'
    assert instance.delta == 'HINKali'
    assert instance.extra == 'RAMEN'

def test_create_empty():
    instance = ObjectModel()

    now = time.time()
    instance.save()

    assert instance.id > 0
    assert instance.updated < now + 1

def test_create():
    instance = ObjectModel(
        title='test_create',
        meta='onigiri',
    )

    now = time.time()
    instance.save()

    assert instance.id > 0
    assert instance.updated < now + 1

def test_init_print():
    instance = ObjectModel(
        meta='onigiri',
        multi=[1, 2, 3],
    )

    text = str(instance)
    assert text[:19] == 'Object ObjectModel('
    assert text[-1] == ')'
    assert json.loads(text[19:-1]) == {
        'id': 0,
        'title': None,
        'data': None,
        'meta': 'onigiri',
        'delta': '',
        'extra': 'uo',
        'teta': None,
        'multi': [1, 2, 3],
        'pompa': None,
        'tulpa': None,
        'rampa': None,
        'status': None,
        'user': 0,
        'created': instance.created,
        'updated': None,
        'expired': None,
    }

def test_change_type():
    # Initialization
    instance = ObjectModel(meta=1)
    assert instance.meta == '1'

    # Changing
    instance.meta = [1, 2, 3]
    assert instance.meta == '[1, 2, 3]'

def test_ignore():
    # Initialization error
    with pytest.raises(ErrorInvalid):
        ObjectModel(tulpa='onigiri')

    # Ignore in case of an error during initialization
    instance = ObjectModel(rampa='onigiri')
    assert instance.rampa is None

    # Ignore in case of an error during assignment
    instance.rampa = 'onigiri'
    assert instance.rampa is None

    # Ignore in case of an error during initialization
    instance = ObjectModel(ignore={'tulpa'}, tulpa='onigiri')
    assert instance.tulpa is None

    # Ignore in case of an error during assignment
    with pytest.raises(ErrorInvalid):
        instance.tulpa = 'onigiri'

def test_multi_type():
    instance = ObjectModel(pompa='onigiri')
    instance.pompa = 0
    instance.pompa = {'ola': 'ulu'}
