from consys import make_base, Attribute


Base = make_base("localhost:27017", "test", "admin", "")


def get_ids(objs):
    return [obj.id for obj in objs]


__all__ = (
    "Base",
    "Attribute",
    "get_ids",
)
