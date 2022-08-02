"""
Test the feature wherein the descriptions (metadata, structure_family,
structure, etc.) for a node's children may be included with the
description of a node. This is used in xarray_dataset now and may
be used more widely later.
"""

import xarray

from ..adapters.mapping import MapAdapter
from ..adapters.xarray import DatasetAdapter
from ..client import from_tree, record_history

tree = MapAdapter(
    {
        "dataset": DatasetAdapter.from_dataset(
            xarray.Dataset(
                data_vars={"temperature": ("time", [100, 99, 98])},
                coords={"time": [1, 2, 3]},
            )
        ),
    },
    metadata={"thing": "stuff"},
)
client = from_tree(tree)


def test_lookup():
    "Accessing a child node should trigger one request."
    with record_history() as history:
        client["dataset"]
    assert len(history.requests) == 1


def test_iter():
    "Iteration should be free because the contents were in-lined."
    expected = ["temperature", "time"]
    dsc = client["dataset"]
    with record_history() as history:
        assert list(dsc) == expected
    assert not history.requests

    # Implementation detail:
    # Without inlined contents, a request is needed.
    with record_history() as history:
        assert list(dsc.__iter__(_ignore_inlined_contents=True)) == expected
    assert history.requests


def test_keys_slice():
    "Iteration should be free because the contents were in-lined."
    expected = ["temperature", "time"]
    dsc = client["dataset"]
    with record_history() as history:
        assert list(dsc.keys()) == expected
    assert not history.requests

    with record_history() as history:
        assert dsc.keys()[:] == expected
    assert not history.requests

    with record_history() as history:
        assert dsc.keys().first() == "temperature"
        assert dsc.keys().last() == "time"
    assert not history.requests

    # Implementation detail:
    # Without inlined contents, a request is needed.
    with record_history() as history:
        list(dsc._keys_slice(0, 1, 1, _ignore_inlined_contents=True))
    assert history.requests


def test_items_slice():
    "Iteration should be free because the contents were in-lined."
    dsc = client["dataset"]
    with record_history() as history:
        list(dsc.items())
    assert not history.requests

    with record_history() as history:
        dsc.items()
    assert not history.requests

    with record_history() as history:
        dsc.items().first()
    assert not history.requests

    with record_history() as history:
        dsc.items().last()
    assert not history.requests

    # Implementation detail:
    # Without inlined contents, a request is needed.
    with record_history() as history:
        list(dsc._items_slice(0, 1, 1, _ignore_inlined_contents=True))
    assert history.requests