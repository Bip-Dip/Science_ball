from __future__ import annotations

from typing import List, Dict, Any, Optional
from app.search.index_names import ESIndexNames
from app.schemas.query import QueryIntent


class SearchQueryBuilder:
    """
    Constructs Elasticsearch DSL queries based on a structured search intent
    and user access permissions.
    """

    @staticmethod
    def build_chunks_query(intent: QueryIntent, allowed_access_levels: List[str]) -> Dict[str, Any]:
        """
        Builds a query for the rd_chunks_v1 index.

        Args:
            intent: The validated search intent derived from NL.
            allowed_access_levels: Access levels the current user is permitted to see.

        Returns:
            A dictionary representing the ES query DSL.
        """
        # Base bool query
        query = {
            "bool": {
                "must": [],
                "filter": [],
                "should": [],
                "minimum_should_match": 0
            }
        }

        # 1. Mandatory Access Level Filter
        # Every search MUST be constrained by the user's access levels.
        query["bool"]["filter"].append({
            "terms": {
                "access_level": allowed_access_levels
            }
        })

        # 2. Text Search (BM25)
        # Use the original query text for a full-text search on the 'text' field of chunks.
        if intent.query_text:
            query["bool"]["must"].append({
                "multi_match": {
                    "query": intent.query_text,
                    "fields": ["text"],
                    "type": "best_fields",
                    "operator": "or"
                }
            })

        # 3. Metadata Filters from Intent
        # Year range
        if intent.year_from is not None or intent.year_to is not None:
            year_filter = {"range": {"year": {}}}
            if intent.year_from is not None:
                year_filter["range"]["year"]["gte"] = intent.year_from
            if intent.year_to is not None:
                year_filter["range"]["year"]["lte"] = intent.year_to
            query["bool"]["filter"].append(year_filter)

        # Practice region (domestic vs foreign)
        if intent.practice_region:
            query["bool"]["filter"].append({
                "term": {"practice_region": intent.practice_region}
            })

        # Source types
        if intent.source_types:
            query["bool"]["filter"].append({
                "terms": {"source_type": intent.source_types}
            })

        # Geography (any of the listed locations)
        if intent.geography:
            query["bool"]["filter"].append({
                "terms": {"geography": intent.geography}
            })

        # 4. Numeric Constraints (Nested Queries)
        for cond in intent.numeric_conditions:
            # Nested query for the 'numeric_conditions' field as defined in mappings.py
            query["bool"]["filter"].append({
                "nested": {
                    "path": "numeric_conditions",
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {"numeric_conditions.property": cond.property_name}},
                                {"term": {"numeric_conditions.unit": cond.unit}}
                            ],
                            "filter": []
                        }
                    }
                }
            })

            # Add range filters to the nested bool if values are provided
            nested_bool = query["bool"]["filter"][-1]["nested"]["query"]["bool"]
            if cond.min_value is not None:
                nested_bool["filter"].append({
                    "range": {"numeric_conditions.min_value": {"gte": cond.min_value}}
                    # Note: we typically filter on the actual value or the range bounds
                    # depending on how facts were indexed. Here we follow a simple approach.
                })
            if cond.max_value is not None:
                nested_bool["filter"].append({
                    "range": {"numeric_conditions.max_value": {"lte": cond.max_value}}
                })

        # Clean up empty clauses to avoid ES errors
        if not query["bool"]["must"]:
            # If no text search, we move the filter's behavior into must or leave it as is.
            # For basic search, usually there is a query_text.
            pass

        if not query["bool"]["should"]:
            del query["bool"]["should"]
            del query["bool"]["minimum_should_match"]

        return query
