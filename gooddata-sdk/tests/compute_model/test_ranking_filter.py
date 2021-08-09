# (C) 2021 GoodData Corporation
from __future__ import annotations

import json
import os

import pytest

from gooddata_sdk import RankingFilter, ObjId, SimpleMetric, Attribute

_current_dir = os.path.dirname(os.path.abspath(__file__))


def _scenario_to_snapshot_name(scenario: str):
    return f"{scenario.replace(' ', '_')}.snapshot.json"


_simple_measure = SimpleMetric(
    local_id="local_id2", item=ObjId(type="metric", id="metric_id")
)
_attribute = Attribute(local_id="local_id4", label="label.id")

test_ranking_filter = [
    [
        "ranking filter using just local ids",
        RankingFilter(
            metrics=["local_id1", _simple_measure],
            dimensionality=["local_id3", _attribute],
            operator="TOP",
            value=10,
        ),
    ],
    [
        "ranking filter using mix of ids for measures",
        RankingFilter(
            metrics=["local_id1", ObjId(type="metric", id="metric.id")],
            dimensionality=["local_id3"],
            operator="TOP",
            value=10,
        ),
    ],
    [
        "ranking filter using mix of ids for dimensionality",
        RankingFilter(
            metrics=["local_id1", _simple_measure],
            dimensionality=["local_id3", ObjId(type="label", id="label.id")],
            operator="TOP",
            value=10,
        ),
    ],
    [
        "bottom ranking filter",
        RankingFilter(
            metrics=["local_id1"],
            dimensionality=["local_id3"],
            operator="BOTTOM",
            value=10,
        ),
    ],
]


@pytest.mark.parametrize("scenario,filter", test_ranking_filter)
def test_attribute_filters_to_api_model(scenario, filter, snapshot):
    # it is essential to define snapshot dir using absolute path, otherwise snapshots cannot be found when
    # running in tox
    snapshot.snapshot_dir = os.path.join(_current_dir, "ranking_filter")

    snapshot.assert_match(
        json.dumps(filter.as_api_model().to_dict(), indent=4, sort_keys=True),
        _scenario_to_snapshot_name(scenario),
    )
