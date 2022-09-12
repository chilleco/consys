from consys import make_base, Attribute


Base = make_base('localhost:27017', 'test', 'admin', 'asdrqwerty09')


__all__ = (
    'Base',
    'Attribute',
)
