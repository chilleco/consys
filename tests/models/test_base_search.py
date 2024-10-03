import pytest
from libdev.gen import generate

from . import Base, Attribute, get_ids
from consys.errors import ErrorInvalid


class ObjectModel(Base):
    _name = "tests_search"
    _search_fields = {
        "search_int",
        "search_str",
        "search_list",
        "search_dict",
    }

    search_int = Attribute(types=int)
    search_str = Attribute(types=str)
    search_list = Attribute(types=list)
    search_dict = Attribute(types=dict)


def test_search():
    uniq = generate()

    instance1 = ObjectModel(
        data=uniq,
        search_int=111,
        search_str="aaa",
        search_list=[111, 222, 333],
        search_dict={"a": 111, "b": 222},
    )
    instance1.save()

    instance2 = ObjectModel(
        data=uniq,
        search_int=111,
        search_str="cbbbbd",
        search_list=[111, 222, 333],
        search_dict={"a": 111},
    )
    instance2.save()

    instance3 = ObjectModel(
        data=uniq,
        search_int=0,
        search_list=[],
        search_dict={"c": 111222},
    )
    instance3.save()

    instance4 = ObjectModel(
        data=uniq,
        search_int=4,
        search_str="",
        search_list=[111, 111, 111],
        search_dict={"aaa": "bbb"},
    )
    instance4.save()

    assert get_ids(ObjectModel.get(data=uniq, search="aaa")) == get_ids([instance1])

    with pytest.raises(ErrorInvalid):
        assert get_ids(ObjectModel.get(data=uniq, search="a"))

    assert get_ids(ObjectModel.get(data=uniq, search="bbb")) == get_ids(
        # [instance4, instance2]
        [instance2]
    )

    assert get_ids(ObjectModel.get(data=uniq, search="111")) == get_ids(
        # [instance4, instance3, instance2, instance1]
        [instance4, instance2, instance1]
    )

    assert get_ids(ObjectModel.get(data=uniq, search=1)) == get_ids([])

    assert get_ids(ObjectModel.get(data=uniq, search=4)) == get_ids([instance4])

    assert get_ids(ObjectModel.get(data=uniq, search=0)) == get_ids(
        [instance4, instance3, instance2, instance1]
    )


def test_search_case():
    uniq = generate()

    instance1 = ObjectModel(
        data=uniq,
        search_str="Abc",
    )
    instance1.save()

    instance2 = ObjectModel(
        data=uniq,
        search_str="ABCD",
    )
    instance2.save()

    instance3 = ObjectModel(
        data=uniq,
        search_str="abcde",
    )
    instance3.save()

    assert get_ids(ObjectModel.get(data=uniq, search="aBc")) == get_ids(
        [instance3, instance2, instance1]
    )
