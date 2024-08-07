"""
Base model of DB object
"""

import time
import json
import string
import random
from abc import abstractmethod
from typing import Union, Optional, Any, Callable, List, Tuple, Set
from copy import deepcopy
from collections import defaultdict

from ._db import DuplicateKeyError
from .errors import ErrorInvalid, ErrorWrong, ErrorRepeat, ErrorUnsaved


SYMBOLS = string.digits + string.ascii_letters


# pylint: disable=too-many-return-statements
def _search(value, search):
    """Search for matches by value"""

    if isinstance(value, str):
        return search in value.lower()

    if isinstance(value, (int, float)):
        return search.isdigit() and int(search) == value

    if isinstance(value, (list, tuple, set)):
        for el in value:
            if _search(el, search):
                return True
        return False

    if isinstance(value, dict):
        for el in value.values():
            if _search(el, search):
                return True
        return False

    return False


def _generate(length: int = 32) -> str:
    """ID generation"""
    return "".join(random.choice(SYMBOLS) for _ in range(length))


class Attribute:
    """Descriptor"""

    name: str = None
    types: Any = None
    default: Any = None
    checking: Callable = None
    pre_processing: Callable = None
    processing: Callable = None
    ignore: bool = False

    def __init__(
        self,
        types=None,
        default=None,
        checking=None,
        pre_processing=None,
        processing=None,
        ignore=False,
    ):
        self.types = types
        self.default = default
        self.checking = checking
        self.pre_processing = pre_processing
        self.processing = processing
        self.ignore = ignore

        # Auto default values
        # TODO: [{}]
        if self.default is None:
            if self.types == list:
                self.default = []

            if self.types == dict:
                self.default = {}

            if self.types == set:
                self.default = set()

    def __set_name__(self, instance, name):
        self.name = name

    def __get__(self, instance, owner):
        if not instance:
            # pylint: disable=isinstance-second-argument-not-valid-type
            if isinstance(self.default, Callable):
                return self.default(owner)

            return deepcopy(self.default)

        if self.name in instance.__dict__:
            return instance.__dict__[self.name]

        if self.default is not None:
            # NOTE: Otherwise, the auto values will remain after accessing them
            # and will not change after changing the dependent values
            # pylint: disable=isinstance-second-argument-not-valid-type
            if isinstance(self.default, Callable):
                return self.default(instance)

            instance.__dict__[self.name] = deepcopy(self.default)
            return instance.__dict__[self.name]

        return None

    def __set__(self, instance, value) -> None:
        # NOTE: Or we can delete the attribute by `=None`,
        # but there could be problem if we just passed undeclared parameter
        if value is None:
            return

        if self.pre_processing:
            value = self.pre_processing(value)

        if self.types is not None and not isinstance(value, self.types):
            try:
                value = self.types(value)
            except ValueError as e:
                if self.ignore:
                    return

                raise ErrorInvalid(self.name) from e

        if self.checking and not self.checking(
            instance._coll,
            instance.id,
            value,
        ):
            if self.ignore:
                return

            raise ErrorInvalid(self.name)

        if self.processing:
            value = self.processing(value)

        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        if self.name in instance.__dict__:
            del instance.__dict__[self.name]


class BaseModel:
    """Base model"""

    id = Attribute(types=int, default=0)  # TODO: unique
    title = Attribute(types=str, default="")  # TODO: required
    data = Attribute(types=str, default="")
    image = Attribute(types=str)  # TODO: handler
    user = Attribute(types=int, default=0)  # 0 → unauth
    status = Attribute(types=int)
    locale = Attribute(types=str)  # None → multi locale
    created = Attribute(types=int)
    updated = Attribute(types=int)
    expired = Attribute(types=int)

    @property
    @abstractmethod
    def _db(self):
        """Database"""
        return None

    @property
    @abstractmethod
    def _name(self) -> str:
        """Collection name"""
        return None

    @property
    def _coll(self):
        """Database collection"""

        if self._name is None:
            return None

        return self._db[self._name]

    # Loaded fields and values of an instance from DB
    _loaded_values: dict = None
    # Specified fields on getting
    _specified_fields: set = None
    # Fields of the class for searching
    _search_fields: set = {"title"}
    # Ignored fields in case of an error
    _ignore_fields: set = {}

    def __init__(
        self,
        arg_data: dict = None,
        arg_fields: set = None,
        arg_ignore: set = None,
        **kwargs,
    ) -> None:
        if arg_ignore is None:
            arg_ignore = self._ignore_fields

        if not arg_data:
            arg_data = kwargs

        # Save the loaded values from DB for further saving only changed ones
        if arg_fields is not None:
            self._loaded_values = deepcopy(arg_data)
            self._specified_fields = arg_fields or None

        # Autocomplete
        # NOTE: Instead of `Attribute(auto=...)`
        # NOTE: Will be added only if it is not a loaded instance
        if arg_fields is None:
            self.created = time.time()

        # Subobject
        if arg_data.get("id", None) is None and self._name is None:
            arg_data["id"] = _generate()

        for name, value in arg_data.items():
            try:
                if arg_fields is not None:
                    # Without fields checking & processing
                    self.__dict__[name] = value
                else:
                    # With fields checking & processing
                    setattr(self, name, value)

            except Exception as e:
                if name in arg_ignore:
                    continue

                raise e

    def __setattr__(self, name, value):
        if not hasattr(self, name):
            raise AttributeError("key")

        super().__setattr__(name, value)

    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        setattr(self, name, value)

    def __repr__(self):
        if self._specified_fields is None:
            pure = self.json(none=True)
            prefix = ""
        else:
            # UGLY: Changed fields are not displayed
            pure = self.json(fields=self._specified_fields)
            prefix = "Partial"

        return (
            f"{prefix}Object {self.__class__.__name__}"
            f"({json.dumps(pure, ensure_ascii=False)})"
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __iter__(self):
        iters = {key: value for key, value in self.__dict__.items() if key[:2] != "__"}

        for key, value in iters.items():
            yield key, value

    @classmethod
    def _next_id(cls):
        """Next DB ID"""

        last = list(cls._db[cls._name].find().sort("id", -1).limit(1))

        if last:
            return last[0]["id"] + 1

        return 1

    def _is_default(self, name):
        """Check the value for the default value"""

        # Get full copy of the instance to restore the dependent default values
        data = deepcopy(self)
        delattr(data, name)

        return getattr(self, name) == getattr(data, name)

    @staticmethod
    def _is_subobject(data):
        """Checking for subobject

        Theoretically, it is object, which has own model, but without DB
        Practically, it is dictionary with `id`
        """

        if (
            isinstance(data, (list, tuple))
            and data
            and isinstance(data[0], dict)
            and "id" in data[0]
        ):
            return True

        return False

    # pylint: disable=too-many-branches
    def _get_changes(self, data):
        loaded = self._loaded_values or {}

        data_set = {}
        data_unset = loaded.keys() - data.keys()
        data_push = defaultdict(list)
        data_pull = defaultdict(list)
        data_update = defaultdict(list)

        for key in data:
            if key in loaded and data[key] == loaded[key]:
                continue

            if self._is_subobject(data[key]):
                for el in data[key]:
                    if (
                        key not in loaded
                        or el["id"] not in {i["id"] for i in loaded[key]}
                        or el not in loaded[key]
                    ):
                        data_push[key].append(el)

                if key not in loaded:
                    continue

                for el in loaded[key]:
                    if key not in data or el["id"] not in {i["id"] for i in data[key]}:
                        data_pull[key].append(el["id"])

                continue

            data_set[key] = data[key]

        # Add subobjects to existing ones
        if data_push:
            # NOTE: I can't find way to select elements from array
            fields = {"_id": False, **{field: True for field in data_push}}
            data_prepush = self._coll.find_one({"id": self.id}, fields)

            for field in data_prepush:
                for value in data_prepush[field]:
                    for i in range(len(data_push[field])):
                        if data_push[field][i]["id"] == value["id"]:
                            break
                    else:
                        continue

                    if data_push[field][i] != value:
                        # NOTE: More often we save point changes,
                        # so it's better to make specific update requests
                        data_update[field].append(data_push[field][i])

                    del data_push[field][i]

                if not data_push[field]:
                    del data_push[field]

        return data_set, data_unset, data_push, data_pull, data_update

    # pylint: disable=too-many-locals,too-many-statements,too-many-arguments
    @classmethod
    def get(
        cls,
        ids: Union[list, tuple, set, int, str, None] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        search: Optional[str] = None,
        fields: Union[List[str], Tuple[str], Set[str], None] = None,
        extra: dict = None,
        sort: str = "desc",
        sortby: str = "id",
        **kwargs,
    ):
        """Get instances of the object"""

        # TODO: key: Callable for complex conditions
        # TODO: optimize count limit to DB rule

        process_one = False

        if ids:
            if isinstance(ids, (list, tuple, set)):
                db_condition = {
                    "id": {"$in": tuple(ids)},
                }
            else:
                process_one = True
                db_condition = {
                    "id": ids,
                }
        elif ids is None:
            db_condition = {}

        else:
            raise ErrorWrong("id")

        if kwargs:
            for key, value in kwargs.items():
                if value is None:
                    continue

                db_condition[key] = value

        if extra:
            for key, value in extra.items():
                db_condition[key] = value

        db_filter = {
            "_id": False,
        }

        if fields is not None:
            # Add `id` for further saving the instance
            # NOTE: Leave `id` in `fields` for fields selections in the end
            fields = set(fields)
            fields.add("id")

            for field in fields:
                db_filter[field] = True

            if search:
                for field in cls._search_fields:
                    db_filter[field] = True

        res = cls._db[cls._name].find(db_condition, db_filter)
        els = []

        if search:
            if len(search) < 3:
                raise ErrorInvalid("search")

            search = search.lower()

            for el in res:
                match = False

                for field in cls._search_fields:
                    if field in el:
                        if _search(el[field], search):
                            match = True
                            break

                if match:
                    els.append(el)

            els.sort(key=lambda el: el[sortby], reverse=sort == "desc")

        else:
            els = res.sort(sortby, -1 if sort == "desc" else 1)

        if offset is None:
            offset = 0

        last = limit + offset if limit else None
        els = els[offset:last]

        # `fields` to indicate:
        # 1. that the instance was loaded and avoid unnecessary data saving
        # 2. what fields were requested and use it for `reload`
        # NOTE: `fields={}` to not confuse unloaded and loaded with fields
        # NOTE: `fields` can't be partially loaded with `{}`, only `{'id'}`
        els = list(
            map(
                lambda el: cls(
                    arg_data=el,
                    arg_fields=fields or {},
                ),
                els,
            )
        )

        # Leave requested attributes, clear of unnecessary ones:
        # 1. after searching
        # 2. autocomplete
        if fields:
            for el in els:
                for key in set(el.__dict__):
                    if key not in fields and key[0] != "_":
                        del el.__dict__[key]

        if process_one:
            if not els:
                raise ErrorWrong("id")

            return els[0]

        # # Not all IDs found
        # if ids and len(ids) != len(els):
        #     raise ErrorWrong('id')

        return els

    # pylint: disable=too-many-locals
    def save(
        self,
    ):
        """Save the instance

        What attributes are not written to DB:
        * None values (via `.json(none=False)`)
        * Static & callable default values (via `.json(default=False)`)
        * Replaced autocomplete values (via fields cleaning in the `get` method)

        If the object has subobjects (list of dicts with `id`),
        1. there will be added only subobjects with new ids,
        2. unspecified subobjects won't be deleted,
        3. the order of subobjects won't be changed.
        To delete subobjects, you can also use `.rm_sub()`

        We can get a save conflict if:
        * Create instance with already existed `id`
        * Parallel saving of instances without `id`
        * Saving changes for an instances that has already changed in DB
        ! We will not get a save conflict if we change a field
        that was not loaded from the database (`_loaded_values`)
        """

        exists = self.id and self._coll.count_documents({"id": self.id})

        if exists and self._loaded_values is None:
            raise ErrorRepeat(self._name)

        # Update
        if exists:
            data = self.json(default=False)
            data["updated"] = int(time.time())

            # Only changes
            (
                data_set,
                data_unset,
                data_push,
                data_pull,
                data_update,
            ) = self._get_changes(data)

            changed = (
                set(data_set)
                | data_unset
                | set(data_push)
                | set(data_pull)
                | set(data_update)
            ) - {"updated"}

            if not changed:
                return

            # Update time
            # NOTE: After checking that there are changes
            self.updated = data["updated"]

            # Update in DB

            db_request = {
                "$set": data_set,
            }

            if data_unset:
                db_request["$unset"] = {key: "" for key in data_unset}

            if data_push:
                db_request["$push"] = {
                    key: {"$each": value} for key, value in data_push.items()
                }

            if data_pull:
                db_request["$pull"] = {
                    key: {"id": {"$in": value}} for key, value in data_pull.items()
                }

            loaded_values = {
                key: self._loaded_values[key]
                for key in changed
                if key in self._loaded_values
            }
            loaded_values["id"] = self.id

            res = self._coll.update_one(loaded_values, db_request)

            if not res.modified_count and not set(data_update):
                raise ErrorRepeat(self._name)

            if data_update:
                for key, value in data_update.items():
                    for el in value:
                        self._coll.update_one(
                            {"id": self.id, f"{key}.id": el["id"]},
                            {"$set": {f"{key}.$": el}},
                        )

            # Update saved fields
            self._loaded_values = data

            return

        # Create

        # NOTE: `id` may not be int
        if self.id == 0:
            self.id = self._next_id()

        # Update time
        self.updated = time.time()

        data = self.json(default=False)

        try:
            self._coll.insert_one({"_id": self.id, **data})
        except DuplicateKeyError as e:
            raise ErrorRepeat(self._name) from e

        # Update saved fields
        self._loaded_values = data

    def rm(
        self,
    ):
        """Delete the instance"""

        res = self._coll.delete_one({"id": self.id}).deleted_count

        if not res:
            raise ErrorWrong("id")

    def rm_sub(
        self,
        field: str,
        ids: Union[int, str],
    ):
        """Delete the subobject of the instance

        After calling this function, all unsaved instance data will be erased
        """

        if not self._coll.count_documents({"id": self.id}):
            raise ErrorUnsaved("id")

        # Update time
        self.updated = time.time()

        self._coll.update_one(
            {"id": self.id},
            {
                "$set": {"updated": self.updated},
                "$pull": {field: {"id": ids}},
            },
        )

        self.reload()

        if self._is_default(field):
            self._coll.update_one({"id": self.id}, {"$unset": {field: ""}})

    def json(
        self,
        default=True,  # Return default values
        none=False,  # Return None values
        fields=None,
    ):
        """Get dictionary of the object

        If default is True and there are fields,
        it will return only fields with non-default values
        """

        data = {}

        for attr in dir(self):
            if fields and attr not in fields:
                continue

            value = getattr(self, attr)

            if attr[0] == "_" or callable(value):
                continue

            if not default and self._is_default(attr):
                continue

            if not none and value is None:
                continue

            data[attr] = value

        return data

    def reload(
        self,
        fields: set = None,
    ):
        """Update the object according to the data from the DB

        After calling this function, all unsaved instance data will be erased
        """

        # TODO: Reloading from Partial Object to Object with all fields

        fields = fields or self._specified_fields

        try:
            data = self.get(ids=self.id, fields=fields)
        except ErrorWrong as e:
            raise ErrorUnsaved(e) from e

        self.__dict__ = data.__dict__

    @classmethod
    def complex(
        cls,
        *args,
        handler: Callable = lambda obj: obj,
        fields: Union[List[str], Tuple[str], Set[str], None] = None,
        **kwargs,
    ):
        """Use combination of functions"""

        instances = cls.get(*args, fields=fields, **kwargs)

        if isinstance(instances, list):
            for i, instance in enumerate(instances):
                instances[i] = handler(instance.json(fields=fields))

            return instances

        return handler(instances.json(fields=fields))

    @classmethod
    def count(
        cls,
        offset: int = 0,
        extra: dict = None,
        **kwargs,
    ):
        """Count of instances of the object"""

        db_condition = {}

        if kwargs:
            for key, value in kwargs.items():
                if value is None:
                    continue

                db_condition[key] = value

        if extra:
            for key, value in extra.items():
                db_condition[key] = value

        return cls._db[cls._name].count_documents(db_condition, skip=offset)
