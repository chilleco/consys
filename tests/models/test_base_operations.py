import time

import pytest
from libdev.gen import generate

from . import Base, Attribute
from consys.errors import ErrorWrong


class ObjectModel(Base):
    _name = "tests"

    meta = Attribute(types=str)
    delta = Attribute(types=str, default="")
    extra = Attribute(types=str, default=lambda instance: f"u{instance.delta}o")
    multi = Attribute(types=list)
    sodzu = Attribute(types=dict)

    @property
    def teta(self):
        return self.delta + (self.meta or "")

    # FIXME: how to unify?
    @teta.deleter
    def teta(self):
        pass


class ObjectModel2(Base):
    _name = "tests2"

    id = Attribute(types=str)


def test_load():
    now = time.time()
    instance = ObjectModel(
        title="test_load",
        user=2,
        status=3,
        meta="onigiri",
        delta="hinkali",
        extra="ramen",
    )
    instance.save()

    recieved = ObjectModel.get(ids=instance.id)

    assert isinstance(recieved, ObjectModel)
    assert recieved.id == instance.id
    assert recieved.title == "test_load"
    assert instance.created < now + 1
    assert instance.updated < now + 1
    assert instance.user == 2
    assert instance.status == 3
    assert recieved.meta == "onigiri"
    assert recieved.delta == "hinkali"
    assert recieved.extra == "ramen"


def test_load_zero():
    with pytest.raises(ErrorWrong):
        ObjectModel.get(0)

    with pytest.raises(ErrorWrong):
        ObjectModel.get([])


def test_load_unknown():
    assert ObjectModel.get(delta="ola") == []


def test_load_complex_fields():
    instance = ObjectModel(
        sodzu={
            "sake": [
                "onigiri",
                "hinkali",
                "ramen",
            ]
        },
    )
    instance.save()

    instances = ObjectModel.get(
        extra={
            "sodzu.sake": "ramen",
        }
    )
    instances = {ins.id: ins for ins in instances}

    assert instances[instance.id]


def test_system_fields():
    instance = ObjectModel(
        title="test_system_fields",
        meta="onigiri",
    )
    instance.save()

    instance = ObjectModel.get(ids=instance.id, fields={})
    assert instance.json().get("_loaded_values") is None

    instances = ObjectModel.get(search="")
    assert all(instance.json().get("_loaded_values") is None for instance in instances)


def test_list():
    now = time.time()

    instance1 = ObjectModel(
        title="test_list",
        user=2,
        status=3,
        meta="onigiri",
        delta="hinkali",
        extra="ramen",
    )
    instance1.save()

    instance2 = ObjectModel()
    instance2.save()

    recieved = ObjectModel.get(
        ids=(
            instance1.id,
            instance2.id,
        )
    )

    assert isinstance(recieved, list)

    with recieved[1] as recieved1:
        assert isinstance(recieved1, ObjectModel)
        assert recieved1.id == instance1.id
        assert recieved1.title == "test_list"
        assert recieved1.created < now + 1
        assert recieved1.updated < now + 1
        assert recieved1.user == 2
        assert recieved1.status == 3
        assert recieved1.meta == "onigiri"
        assert recieved1.delta == "hinkali"
        assert recieved1.extra == "ramen"

    with recieved[0] as recieved2:
        assert isinstance(recieved2, ObjectModel)
        assert recieved2.id == instance2.id
        assert recieved2.created < now + 1
        assert recieved2.updated < now + 1


def test_update():
    instance = ObjectModel(
        title="test_create",
        delta="hinkali",
    )
    instance.save()

    assert instance.title == "test_create"
    assert instance.meta is None
    assert instance.delta == "hinkali"

    instance_id = instance.id
    instance = ObjectModel.get(ids=instance_id)

    instance.title = "test_update"
    instance.meta = "onigiri"

    instance.save()

    assert instance_id == instance.id

    instance = ObjectModel.get(ids=instance.id)

    assert instance.title == "test_update"
    assert instance.meta == "onigiri"
    assert instance.delta == "hinkali"


def test_update_empty():
    instance = ObjectModel(
        title="test_create",
        meta="onigiri",
    )
    instance.save()

    assert instance.title == "test_create"
    assert instance.meta == "onigiri"

    instance_id = instance.id
    instance = ObjectModel.get(ids=instance_id)

    instance.title = None

    instance.save()

    assert instance_id == instance.id

    instance = ObjectModel.get(ids=instance.id)

    assert instance.title == "test_create"
    assert instance.meta == "onigiri"


def test_update_resave():
    instance = ObjectModel(title="test_create", delta="hinkali")
    instance.save()

    instance_id = instance.id

    instance.title = "test_update"
    instance.meta = "onigiri"
    instance.save()

    assert instance_id == instance.id

    instance = ObjectModel.get(ids=instance.id)

    assert instance.title == "test_update"
    assert instance.meta == "onigiri"
    assert instance.delta == "hinkali"


def test_rm():
    instance = ObjectModel()
    instance.save()

    instance.rm()

    with pytest.raises(ErrorWrong):
        ObjectModel.get(ids=instance.id)


def test_rm_nondb():
    instance = ObjectModel()

    with pytest.raises(ErrorWrong):
        instance.rm()


def test_rm_attr():
    instance = ObjectModel(
        meta="onigiri",
        delta="hinkali",
    )
    instance.save()

    instance = ObjectModel.get(ids=instance.id)

    del instance.meta
    instance.delta = "hacapuri"

    instance.save()
    instance = ObjectModel.get(ids=instance.id)

    assert instance.meta is None
    assert instance.delta == "hacapuri"


def test_rm_attr_resave():
    instance = ObjectModel(
        title="test_attr_resave",
        meta="onigiri",
        delta="hinkali",
    )
    instance.save()

    del instance.meta
    instance.delta = "hacapuri"

    instance.save()
    instance = ObjectModel.get(ids=instance.id)

    assert instance.title == "test_attr_resave"
    assert instance.meta is None
    assert instance.delta == "hacapuri"


def test_reload():
    instance = ObjectModel(
        delta="hinkali",
    )
    instance.save()

    recieved1 = ObjectModel.get(ids=instance.id)
    recieved2 = ObjectModel.get(ids=instance.id)

    assert recieved1._specified_fields is None
    assert recieved2._specified_fields is None

    recieved1.delta = "hacapuri"
    recieved1.save()

    assert recieved1.delta == "hacapuri"
    assert recieved2.delta == "hinkali"

    recieved2.reload()

    assert recieved2._specified_fields is None
    assert recieved2.id == recieved1.id == instance.id
    assert recieved2.delta == "hacapuri"

    recieved1.reload()

    assert recieved1._specified_fields is None
    assert recieved1.id == recieved1.id == instance.id
    assert recieved1.delta == "hacapuri"


def test_resave():
    instance = ObjectModel(
        delta="hinkali",
    )

    instance.save()

    updated = instance.updated

    instance.save()

    assert instance.updated == updated


def test_complex():
    instance = ObjectModel(
        meta="onigiri",
        delta="hinkali",
    )

    instance.save()

    def handler(obj):
        obj["teta"] = obj["meta"].upper()
        return obj

    recieved = ObjectModel.complex(
        ids=instance.id,
        fields={"id", "meta"},
        handler=handler,
    )

    assert recieved == {
        "id": instance.id,
        "meta": "onigiri",
        "teta": "ONIGIRI",
    }


def test_to_default():
    instance = ObjectModel(
        delta="hinkali",
        multi=[1, 2, 3],
    )
    instance.save()

    instances = ObjectModel.get(delta={"$exists": False}, fields={"id"})
    assert instance.id not in [i.id for i in instances]

    instances = ObjectModel.get(multi={"$exists": False}, fields={"id"})
    assert instance.id not in [i.id for i in instances]

    instance.delta = ""
    instance.save()

    assert instance.delta == ""
    assert instance.multi == [1, 2, 3]

    instances = ObjectModel.get(delta={"$exists": False}, fields={"id"})
    assert instance.id in [i.id for i in instances]

    instance = ObjectModel.get(instance.id)

    assert instance.delta == ""
    assert instance.multi == [1, 2, 3]

    instance.multi = []
    instance.save()

    assert instance.multi == []

    instances = ObjectModel.get(multi={"$exists": False}, fields={"id"})
    assert instance.id in [i.id for i in instances]


def test_wrong_ids():
    instance1 = ObjectModel2(id=generate())
    instance2 = ObjectModel2(id=generate())
    instance3 = ObjectModel2(id=generate())

    instance1.save()
    instance3.save()

    instances = ObjectModel2.get(
        {
            instance1.id,
            instance2.id,
            instance3.id,
        }
    )

    assert len(instances) == 2


def test_get_with_none_field():
    instance = ObjectModel(meta="hinkali")
    instance.save()

    instance = ObjectModel.get(
        ids=instance.id,
        meta=None,
    )
    assert instance


def test_count():
    assert ObjectModel.count() > 0

    meta = generate()
    ObjectModel(meta=meta).save()
    assert ObjectModel.count(meta=meta) == 1

    ObjectModel(meta=meta).save()
    assert ObjectModel.count(meta=meta) == 2
    assert ObjectModel.count(meta=meta, offset=1) == 1


def test_get_last():
    ObjectModel(meta="hinkali", delta="onigiri").save()
    ObjectModel(meta="hinkali", delta="hacapuri").save()

    last = ObjectModel.get(meta="hinkali", limit=1)
    assert len(last) == 1
    assert last[0].delta == "hacapuri"


def test_resave_changed():
    instance = ObjectModel(meta="123")
    instance.save()
    assert instance.multi == []

    instance = ObjectModel(delta="456")
    instance.save()
    assert instance.multi == []

    instance.multi.append(1)
    assert instance.multi == [1]

    instance.meta = "789"
    instance.save()
    assert instance.multi == [1]

    instance.multi.extend([2, 3])
    instance.multi.append(4)
    instance.save()
    assert instance.multi == [1, 2, 3, 4]

    # instance.multi = instance.multi + [5]
    # instance.save()
    # assert instance.multi == [1, 2, 3, 4, 5]


def test_get_resaved():
    instance = ObjectModel(meta="123")
    instance.save()

    instance.delta = "456"
    instance.save()

    instance.multi.append(1)
    instance.multi += [2]
    instance.multi.append(3)
    instance.save()

    instance.multi += [4]
    instance.save()

    instance.multi.append(5)
    instance.save()

    assert ObjectModel.get(instance.id).multi == [1, 2, 3, 4, 5]


def test_property():
    instance = ObjectModel(meta="ulu")
    instance.save()

    assert instance.teta == "ulu"
    instance.save()


def test_get_changes():
    instance = ObjectModel(
        # meta = None,
        delta="",
        extra=None,
        multi=[1, 2, 3],
        sodzu={"a": "b", "b": "c"},
    )

    assert instance.get_changes() == {
        "created": (None, instance.created),
        "multi": (None, [1, 2, 3]),
        "sodzu": (None, {"a": "b", "b": "c"}),
    }

    instance.save()

    instance.meta = 123
    instance.delta = ""
    # instance.extra
    instance.multi.append(4)
    instance.multi[0] = 5
    instance.sodzu.update({"a": "c", "c": "d"})

    assert instance.get_changes() == {
        "meta": (None, "123"),
        "multi": ([1, 2, 3], [5, 2, 3, 4]),
        "sodzu": ({"a": "b", "b": "c"}, {"a": "c", "b": "c", "c": "d"}),
    }


def test_load_by():
    uniq = generate()
    instance = ObjectModel(meta=uniq)
    instance.save()

    assert ObjectModel.get(uniq, by="meta").id == instance.id
