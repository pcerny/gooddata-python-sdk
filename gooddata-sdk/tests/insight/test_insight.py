# (C) 2021 GoodData Corporation
from __future__ import annotations

import json
import os

import pytest

from gooddata_sdk import Insight
from gooddata_sdk.compute_model import compute_model_to_api_model
from tests.insight.fixtures import load_vis_obj

_current_dir = os.path.dirname(os.path.abspath(__file__))
_resources_dir = os.path.join(_current_dir, "resources")


def _insight_filename_to_snapshot_name(absolute_path):
    return os.path.basename(absolute_path).replace(".json", ".snapshot.json")


@pytest.mark.parametrize("filename", [os.path.join(_resources_dir, d) for d in os.listdir(_resources_dir)])
def test_attribute_filters_to_api_model(filename, snapshot):
    vis_obj = load_vis_obj(filename)
    insight = Insight(vis_obj)

    # it is essential to define snapshot dir using absolute path, otherwise snapshots cannot be found when
    # running in tox
    snapshot.snapshot_dir = os.path.join(_current_dir, "snapshots")

    attributes = [a.as_computable() for a in insight.attributes]
    metrics = [m.as_computable() for m in insight.metrics]
    filters = [f.as_computable() for f in insight.filters]

    afm = compute_model_to_api_model(attributes, metrics, filters)

    snapshot.assert_match(
        json.dumps(afm.to_dict(), indent=4, sort_keys=True),
        _insight_filename_to_snapshot_name(filename),
    )
