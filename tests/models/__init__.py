from consys import make_base, Attribute


Base = make_base("localhost:27017", "test", "admin", "")


def get_ids(objs):
    return [obj.id for obj in objs]


def filter_ids(objs, tmps):
    ids = get_ids(tmps)
    return [obj.id for obj in objs if obj.id in ids]


__all__ = (
    "Base",
    "Attribute",
    "get_ids",
)
