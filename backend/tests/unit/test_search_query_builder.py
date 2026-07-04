from __future__ import annotations

import pytest
from app.search.query_builder import SearchQueryBuilder
from app.schemas.query import QueryIntent, NumericConstraint, RequestedOutput


@pytest.fixture
def builder():
    return SearchQueryBuilder()


@pytest.fixture
def basic_intent():
    return QueryIntent(
        intent="technology_review",
        query_text="electrowinning of nickel",
        materials=["nickel"],
        processes=["electrowinning"],
        requested_output=RequestedOutput()
    )


def test_build_chunks_query_access_filter(builder, basic_intent):
    """Verify that access_level filter is always present and correct."""
    allowed = ["public", "internal"]
    query = builder.build_chunks_query(basic_intent, allowed)

    # Check if the 'terms' filter for access_level exists
    filters = query["bool"]["filter"]
    access_filter = next((f for f in filters if "terms" in f and "access_level" in f["terms"]), None)

    assert access_filter is not None
    assert access_filter["terms"]["access_level"] == allowed


def test_build_chunks_query_text_search(builder, basic_intent):
    """Verify that the text search is correctly added to the 'must' clause."""
    allowed = ["public"]
    query = builder.build_chunks_query(basic_intent, allowed)

    must_clause = query["bool"]["must"]
    text_search = next((m for m in must_clause if "multi_match" in m), None)

    assert text_search is not None
    assert text_search["multi_match"]["query"] == "electrowinning of nickel"
    assert "text" in text_search["multi_match"]["fields"]


def test_build_chunks_query_year_filter(builder, basic_intent):
    """Verify that year range filters are correctly added."""
    basic_intent.year_from = 2010
    basic_intent.year_to = 2020
    allowed = ["public"]

    query = builder.build_chunks_query(basic_intent, allowed)
    filters = query["bool"]["filter"]

    year_filter = next((f for f in filters if "range" in f and "year" in f["range"]), None)
    assert year_filter is not None
    assert year_filter["range"]["year"]["gte"] == 2010
    assert year_filter["range"]["year"]["lte"] == 2020


def test_build_chunks_query_numeric_constraints(builder, basic_intent):
    """Verify that numeric constraints are translated to nested queries."""
    basic_intent.numeric_conditions = [
        NumericConstraint(
            property_name="temperature",
            min_value=50.0,
            max_value=100.0,
            unit="C"
        )
    ]
    allowed = ["public"]

    query = builder.build_chunks_query(basic_intent, allowed)
    filters = query["bool"]["filter"]

    nested_filter = next((f for f in filters if "nested" in f), None)
    assert nested_filter is not None
    assert nested_filter["nested"]["path"] == "numeric_conditions"

    # Check the inner bool query of the nested filter
    inner_bool = nested_filter["nested"]["query"]["bool"]
    assert any("temperature" in str(m) for m in inner_bool["must"])
    assert any("C" in str(m) for m in inner_bool["must"])

    # Check ranges
    range_filters = inner_bool.get("filter", [])
    assert any("numeric_conditions.min_value" in str(r) for r in range_filters)
    assert any("numeric_conditions.max_value" in str(r) for r in range_filters)


def test_build_chunks_query_empty_text(builder, basic_intent):
    """Verify behavior when query_text is empty."""
    basic_intent.query_text = ""
    allowed = ["public"]
    query = builder.build_chunks_query(basic_intent, allowed)

    assert len(query["bool"]["must"]) == 0
