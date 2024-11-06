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
        "search_dict.ru",
        "search_dict.en",
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


def test_search_count():
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

    instance4 = ObjectModel(
        data=uniq,
        search_str="xyz",
    )
    instance4.save()

    assert ObjectModel.count(data=uniq, search="aBc") == 3
    assert ObjectModel.count(data=uniq, search="xyz") == 1
    assert ObjectModel.count(data=uniq, search="123") == 0
    assert ObjectModel.count(data=uniq, search=1) == 0


def test_search_nested():
    uniq = generate()

    instance1 = ObjectModel(
        data=uniq,
        search_dict={
            "ru": 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "БИПИЭМТИМ"',
            "en": "LLC BPMTEAM",
        },
    )
    instance1.save()

    instance2 = ObjectModel(
        data=uniq,
        search_dict={
            "ru": 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "КОМАНДНОЕ ВЗАИМОДЕЙСТВИЕ"',
            "en": "TEAM COORDINATION LIMITED LIABILITY COMPANY",
        },
    )
    instance2.save()

    instance3 = ObjectModel(
        data=uniq,
        search_dict={
            "ru": 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "ПОЛИТИМ ИННОВАЦИИ"',
            "en": "POLYTEAM INNOVATION",
        },
    )
    instance3.save()

    instance4 = ObjectModel(
        data=uniq,
        search_dict={
            "ru": 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "ХРОНИКАЛС РЕСЕРЧ ТИМ"',
            "en": 'LIMITED LIABILITY COMPANY  "CHRONICLES RESEARCH TEAM"',
        },
    )
    instance4.save()

    instance5 = ObjectModel(
        data=uniq,
        search_dict={
            "ru": 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "ОЛЛИ ТИМ"',
            "en": 'LIMITED LIABILITY COMPANY "OLLY TEAM"',
        },
    )
    instance5.save()

    instance6 = ObjectModel(
        data=uniq,
        search_dict={
            "ru": 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "ТОМОРУ ТИМ"',
            "en": "TOMORU.TEAM",
        },
    )
    instance6.save()

    instance7 = ObjectModel(
        data=uniq,
        search_dict={"ru": "MooTeam"},
    )
    instance7.save()

    instance8 = ObjectModel(
        data=uniq,
        search_dict={"ru": "Thank.Team"},
    )
    instance8.save()

    instance9 = ObjectModel(
        data=uniq,
        search_dict={"ru": "Solotea"},
    )
    instance9.save()

    instance10 = ObjectModel(
        data=uniq,
        search_dict={"ru": "TEAMLY"},
    )
    instance10.save()

    assert len(ObjectModel.complex(data=uniq, search="tea")) == 10
    assert ObjectModel.count(data=uniq, search="tea") == 10
    assert ObjectModel.count(data=uniq, search="team") == 9
    assert ObjectModel.count(data=uniq, search="teaml") == 1
    assert ObjectModel.count(data=uniq, search="teamlx") == 0
