"""Internal helpers shared by V1 services."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from typing import Any, Dict, List, Optional, Type, TypeVar

T = TypeVar("T")


def from_dict(cls: Type[T], data: Any) -> Optional[T]:
    """Build a dataclass from a server-side dict (PascalCase keys)."""
    if data is None:
        return None
    if isinstance(data, cls):
        return data
    if not isinstance(data, dict):
        return None
    if not is_dataclass(cls):
        raise TypeError(f"from_dict requires a dataclass; got {cls!r}")
    init_kwargs: Dict[str, Any] = {}
    for fld in fields(cls):
        json_name = fld.metadata.get("json", fld.name) if fld.metadata else fld.name
        # Permit lookup by the json key OR the snake_case attribute name.
        for key in (json_name, fld.name):
            if key in data:
                value = data[key]
                init_kwargs[fld.name] = _decode_field(fld, value)
                break
    try:
        return cls(**init_kwargs)  # type: ignore[call-arg]
    except TypeError:
        # Some dataclasses have required positional fields — fall back: instantiate
        # with available kwargs and silently drop missing ones by using getattr fallback.
        # Build a "safe" version by providing defaults for missing required fields.
        instance = cls.__new__(cls)  # type: ignore[call-arg]
        for fld in fields(cls):
            setattr(instance, fld.name, init_kwargs.get(fld.name, _default_for_field(fld)))
        return instance


def _decode_field(fld, value: Any) -> Any:
    # Detect List[X] of dataclass and dict-of-X
    inner = _list_of_dataclass(fld.type)
    if inner and isinstance(value, list):
        return [from_dict(inner, v) if isinstance(v, dict) else v for v in value]
    nested = _dataclass_type(fld.type)
    if nested and isinstance(value, dict):
        return from_dict(nested, value)
    return value


def _dataclass_type(tp: Any):
    # str type-hints (PEP 563) won't resolve here; we rely on generic dict pass-through.
    if isinstance(tp, type) and is_dataclass(tp):
        return tp
    return None


def _list_of_dataclass(tp: Any):
    # Best-effort: handle typing.List[X]
    origin = getattr(tp, "__origin__", None)
    if origin is list:
        args = getattr(tp, "__args__", ())
        if args and isinstance(args[0], type) and is_dataclass(args[0]):
            return args[0]
    return None


def _default_for_field(fld) -> Any:
    if fld.default is not None and fld.default is not getattr(fld, "_MISSING_TYPE", None):
        try:
            from dataclasses import MISSING

            if fld.default is not MISSING:
                return fld.default
        except Exception:
            pass
    if fld.default_factory is not None:  # type: ignore[attr-defined]
        try:
            from dataclasses import MISSING

            if fld.default_factory is not MISSING:  # type: ignore[attr-defined]
                return fld.default_factory()  # type: ignore[misc]
        except Exception:
            pass
    return None


def list_from_items(cls: Type[T], data: Any, key: str = "Items") -> List[T]:
    if data is None:
        return []
    items = data.get(key) if isinstance(data, dict) else None
    if not isinstance(items, list):
        return []
    out: List[T] = []
    for item in items:
        decoded = from_dict(cls, item)
        if decoded is not None:
            out.append(decoded)
    return out


def drop_empty(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in d.items() if v not in (None, "", [], {})}
