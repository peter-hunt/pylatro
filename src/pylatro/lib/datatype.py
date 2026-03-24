"""Generic DataType Framework for Type-Safe Data Models

This module provides a lightweight type system for defining structured data objects
with optional fields, validation, custom serialization, and JSON compatibility.

Key Components:
    Variable: Descriptor for a single typed field in a DataType
    DataType: Base class for creating strongly-typed data models
    get_var: Utility to retrieve a Variable by name from a list

Usage Example:
    >>> class User(DataType):
    ...     variables = [
    ...         Variable("name", str),
    ...         Variable("age", int),
    ...         Variable("email", str, default=None),
    ...     ]
    >>> user = User("Alice", 30, "alice@example.com")
    >>> print(user.dumps())  # Serialize to dict
    >>> user_copy = User.loads(user.dumps())  # Deserialize from dict

Designed for game engines, API models, configuration objects, and any project
requiring clean, type-safe data structures with serialization support.
"""

from collections.abc import Callable
from enum import Enum
from io import TextIOWrapper
from re import fullmatch
from typing import Any

from pylatro.myjson import load as json_load, dump as json_dump
from pylatro.lib.str_convert import to_snake_case
from .utils import TypeLike, istype


__all__ = [
    "Variable", "get_var",
    "DataType",
]


# Sentinel value to distinguish "no default provided" from "None as default value"
_UNSET = object()


Immutable = int | float | complex | bool | str | tuple | bytes | range | frozenset | type(
    None) | Enum


class Variable:
    """Descriptor for a single typed field within a DataType.

    Defines a named field with type information, optional defaults, validation,
    and custom serialization logic. Used by DataType subclasses to define their structure.

    Attributes:
        name (str): Field name (must be valid Python identifier)
        type (TypeLike): Expected type or type union
        default (Any): Immutable default value (defaults to _UNSET if not provided)
        default_factory (Callable | None): Function to generate default values
        validator (Callable[[Any], bool] | None): Optional validation function
        loader (Callable[[Any], Any] | None): Optional deserialization function
        dumper (Callable[[Any], Any] | None): Optional serialization function
        optional (bool): True if default or default_factory is provided
    """

    name: str
    type: TypeLike
    default: Any | None
    default_factory: Callable[[], Any] | None
    validator: Callable[[Any], bool] | None
    loader: Callable[[Any], Any] | None
    dumper: Callable[[Any], Any] | None

    def __init__(self, name: str, type: TypeLike,
                 default=_UNSET, default_factory: Callable | None = None,
                 validator: Callable[[Any], bool] | None = None,
                 loader: Callable[[Any], Any] | None = None,
                 dumper: Callable[[Any], Any] | None = None):
        """Initialize a Variable field descriptor.

        Args:
            name: Field name (alphanumeric and underscores only)
            type: Type or type union (e.g., int, str, list[str])
            default: Immutable default value (optional; None can be used as an explicit default)
            default_factory: Callable that returns default value (for mutable types)
            validator: Function(value) -> bool to validate values
            loader: Function(value) -> deserialized_value to deserialize from stored format
            dumper: Function(value) -> serialized_value to serialize to stored format

        Raises:
            NameError: If name is invalid or reserved
            ValueError: If both default and default_factory are provided
        """
        if not fullmatch(r"[A-Za-z_]\w*", name):
            raise NameError(
                f"variable name must be contain only letters,"
                f" non-leading digits, and underscores, not {name!r}")
        if name in DataType.__annotations__:
            raise NameError(
                f"cannot override DataType class attribute: {name}")
        if name == "type":
            raise NameError("variable 'type' is reserved for JSON dumping")
        if name == "datatype_id":
            raise NameError(
                "variable 'datatype_id' is reserved for DataType identification")
        if name == "variables":
            raise NameError(
                "variable 'variable' is reserved for DataType variables storing")
        if name == "DUMP_DEFAULTS":
            raise NameError(
                "variable 'DUMP_DEFAULTS' is reserved for DataType dumping")
        self.name = name
        self.type = type
        if default is not _UNSET and default_factory is not None:
            raise ValueError(
                "both default and default_factory are given, conflict")
        self.default = default
        self.default_factory = default_factory
        self.optional = self.default is not _UNSET or self.default_factory is not None
        self.validator = validator
        self.loader = loader
        self.dumper = dumper

    @property
    def default_value(self):
        """Get the default value for this variable.

        Returns:
            The default value (from default or default_factory).

        Raises:
            ValueError: If no default is available and variable is required.
        """
        if self.default is not _UNSET:
            return self.default
        elif self.default_factory is not None:
            return self.default_factory()
        else:
            raise ValueError(f"default value not provided"
                             f" for variable {self.name!r}")

    def load(self, value: any, /):
        """Deserialize a value from storage format.

        Args:
            value: Value from storage (dict, JSON, etc.)

        Returns:
            Deserialized value, or original if no loader is defined.
        """
        return value if self.loader is None else self.loader(value)

    def dump(self, value: any, /):
        """Serialize a value to storage format.

        Args:
            value: Value to serialize

        Returns:
            Serialized value, or original if no dumper is defined.
        """
        return value if self.dumper is None else self.dumper(value)

    def validate(self, value: any, /):
        """Validate a value against this variable's validator (if any).

        Args:
            value: Value to validate

        Returns:
            True if valid (or no validator defined), False otherwise.
        """
        return True if self.validator is None else self.validator(value)


def get_var(variables: list[Variable], name: str, /) -> Variable | None:
    """Find a Variable by name in a list.

    Utility function to search for a Variable descriptor by name.

    Args:
        variables: List of Variable objects to search
        name: Name of the variable to find

    Returns:
        The Variable object if found, None otherwise.
    """
    for var in variables:
        if var.name == name:
            return var


class DataType:
    """Base class for creating strongly-typed data models.

    Subclass DataType to define structured data with type checking, validation,
    and automatic JSON serialization/deserialization.

    Subclasses must define:
        variables (class attribute): List of Variable descriptors
        datatype_id (optional): String identifier for this type (auto-generated from class name)

    Features:
        - Type-safe field initialization and access
        - Automatic validation on construction
        - JSON serialization via dumps()/loads()
        - File I/O via dump()/load()
        - Introspection via is_valid()

    Example:
        >>> class Item(DataType):
        ...     variables = [
        ...         Variable("name", str),
        ...         Variable("price", float),
        ...         Variable("quantity", int, default=1),
        ...     ]
        >>> item = Item("Widget", 9.99)
        >>> item.dumps()  # {'name': 'Widget', 'price': 9.99, 'quantity': 1, 'type': 'item'}
    """

    datatype_id: str  # Type identifier for serialization
    variables: list[Variable]  # List of field definitions
    # DUMP_DEFAULTS: Include optional fields with default values in dumps() output
    DUMP_DEFAULTS: bool = True

    def __init_subclass__(cls):
        """Validate and initialize a DataType subclass.

        Called automatically when a subclass is defined. Validates that:
        - The class defines a 'variables' attribute
        - All items in variables are Variable instances
        - Variable names don't conflict with reserved names
        - Optional fields come after required fields
        - Mutable defaults use default_factory, not default

        Raises:
            TypeError: If validation fails
            NameError: If invalid variable names are used
            ValueError: If mutable defaults are used incorrectly
        """
        if "datatype_id" not in cls.__dict__:
            cls.datatype_id = to_snake_case(cls.__name__)
        if "variables" not in cls.__dict__:
            raise TypeError(
                f"{cls.__name__} must define class attribute 'variables'")
        variables = cls.variables
        for var in variables:
            if not isinstance(var, Variable):
                raise TypeError(
                    f"{cls.__name__}.variables must only contain"
                    f" Variable instances, not {type(var).__name__}: {var}")
            if var.name in DataType.__annotations__:
                raise NameError(
                    f"variable {var.name!r} is reserved for DataType"
                    f" class attribute: cannot be used")
        used_names = {*()}
        seen_optional = False
        for var in variables:
            if var.name in used_names:
                raise TypeError(f"{cls.__name__} contains multiple variables"
                                f" of the same name: {var.name}")
            used_names.add(var.name)
            if seen_optional and not var.optional:
                raise TypeError(f"variable without a default follows"
                                f" variable with a default: {var.name}")
            elif var.optional:
                seen_optional = True
            if var.default is not _UNSET and not isinstance(var.default, Immutable):
                raise ValueError(
                    f"for mutable default values, use getter functions with"
                    f" default_factory instead of default: {var.name}")

    def __init__(self, *args, **kwargs):
        """Initialize a DataType instance with field values.

        Accepts positional or keyword arguments matching the variables list.
        Validates all values against their Variable definitions.
        Sets optional fields to their defaults if not provided.

        Args:
            *args: Positional values in variable order
            **kwargs: Keyword arguments by variable name

        Raises:
            TypeError: If wrong number of args, unexpected keywords, or type mismatch
            ValueError: If validation fails
        """
        if len(args) + len(kwargs) > len(self.variables):
            raise TypeError(f"{self.__class__.__name__}() takes at most"
                            f" {len(self.variables)} arguments"
                            f" ({len(args) + len(kwargs)} given)")

        used_names = {*()}
        for i, value in enumerate(args):
            var = self.variables[i]
            used_names.add(var.name)
            if not istype(value, var.type):
                raise TypeError(
                    f"expected {var.type} for variable"
                    f" {var.name!r}, got {value} ({type(value).__name__})")
            if not istype(value, var.type):
                raise TypeError(
                    f"variable {var.name!r} obtained value {value!r},"
                    f" which is not of type {var.type}")
            if var.validator is not None:
                if not var.validator(value):
                    raise ValueError(
                        f"invalid value for variable {var.name!r}: {value!r}")
            setattr(self, var.name, value)

        for key, value in kwargs.items():
            var = get_var(self.variables, key)
            if var is None:
                raise TypeError(
                    f"{self.__class__.__name__}() got an unexpected"
                    f" keyword argument {key!r}")
            if key in used_names:
                raise TypeError(
                    f"{self.__class__.__name__}() got multiple"
                    f" values for argument {var.name!r}")
            if not istype(value, var.type):
                raise TypeError(f"variable {var.name!r} obtained value {value!r},"
                                f" which is not of type {var.type}")
            if var.validator is not None:
                if not var.validator(value):
                    raise ValueError(
                        f"invalid value for variable {var.name!r}: {value!r}")
            used_names.add(var.name)
            setattr(self, key, value)

        for pos, var in enumerate(self.variables, 1):
            if var.optional:
                break
            elif var.name not in used_names:
                raise TypeError(
                    f"{self.__class__.__name__}() missing required"
                    f" argument {var.name!r} (pos {pos})")
        for var in self.variables:
            if var.optional and not hasattr(self, var.name):
                setattr(self, var.name, var.default_value)

    def __repr__(self):
        """Return detailed string representation showing all field values."""
        result = f"{self.__class__.__name__}("
        result += ", ".join(
            f"{var.name}={getattr(self, var.name)!r}"
            for var in self.variables
        )
        return result + ')'

    def __str__(self):
        """Return simple string representation with values only."""
        result = f"{self.__class__.__name__}("
        result += ", ".join(
            f"{getattr(self, var.name)!r}"
            for var in self.variables
        )
        return result + ')'

    def dumps(self):
        """Serialize this instance to a dictionary.

        Converts all fields to their serialized form using dumper functions
        (if defined). Includes a 'type' field with the datatype_id.

        Optional fields are included or omitted based on DUMP_DEFAULTS setting.

        Returns:
            dict with serialized field values and 'type' identifier.
        """
        result = {}
        for var in self.variables:
            if not self.DUMP_DEFAULTS and var.optional:
                if getattr(self, var.name) == var.default_value:
                    continue
            result[var.name] = var.dump(getattr(self, var.name))
        result["type"] = self.datatype_id
        return result

    def dump(self, file: TextIOWrapper, /):
        """Serialize this instance to a JSON file.

        Args:
            file: Open file object to write JSON to.
        """
        json_dump(self.dumps(), file)

    @classmethod
    def loads(cls, obj: dict[str, any], /):
        """Deserialize an instance from a dictionary.

        Creates a new instance from serialized data, converting each field
        using its loader function (if defined). Validates type tag matches.

        Args:
            obj: Dictionary with 'type' key and serialized field values.

        Returns:
            New instance of this class populated with deserialized values.

        Raises:
            TypeError: If type tag doesn't match
            NameError: If required fields are missing
        """
        if "type" not in obj:
            raise TypeError(f"type tag missing from data.")
        elif obj["type"] != cls.datatype_id:
            raise TypeError(f"expected type tag {cls.datatype_id!r},"
                            f" got {obj['type']}")
        values = []
        for var in cls.variables:
            if var.name in obj:
                values.append(var.load(obj[var.name]))
            elif var.optional:
                values.append(var.default_value)
            else:
                raise NameError(f"variable {var.name!r} not found from data.")
        return cls(*values)

    @classmethod
    def load(cls, file: TextIOWrapper, /):
        """Deserialize an instance from a JSON file.

        Args:
            file: Open file object to read JSON from.

        Returns:
            New instance deserialized from the file.
        """
        return cls.loads(json_load(file))

    @classmethod
    def is_valid(cls, obj: dict[str, any]):
        """Check if a dictionary represents a valid instance of this type.

        Validates structure, type tag, required fields, and types without
        raising exceptions. Useful for pre-validation before loading.

        Args:
            obj: Dictionary to validate.

        Returns:
            True if the dictionary can be successfully deserialized, False otherwise.
        """
        if not istype(obj, dict[str, any]):
            return False
        if "type" not in obj or obj["type"] != cls.datatype_id:
            return False
        for var in cls.variables:
            if var.name not in obj and not var.optional:
                return False
        for var in cls.variables:
            if var.name not in obj:
                continue
            value = obj[var.name]
            try:
                loaded_value = var.load(value)
            except:
                return False
            if not istype(loaded_value, var.type):
                return False
            if not var.validate(loaded_value):
                return False
        return True


def main():
    """Example usage demonstration.

    Creates and manipulates DataType instances to show typical usage patterns.
    """
    class Sword(DataType):
        variables = [
            Variable("name", str),
            Variable("damage", int),
            Variable("knockback", int, 0),
            Variable("lores", list[str], default_factory=lambda: []),
        ]

    a = Sword("Errata", 133)
    b = Sword("Byakko", 100)
    print(a)
    print(b)
    a.lores.append("It was worth the wait.")
    b.lores.append("Spent most of the time collecting dust on Wakako's desk.")
    b.lores.append("Except for the occasional heated negotiation.")
    print(a)
    print(b)


if __name__ == "__main__":
    """Run example when module is executed directly."""
    main()
