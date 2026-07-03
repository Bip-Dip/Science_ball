from typing import Any, Dict
from app.search.index_names import ESIndexNames

def get_vector_dimension() -> int:
    # In a real scenario, this would come from settings.py
    # For now, we assume 384 for e5-small as per SDD's embedding recommendation
    return 384

MAPPINGS: Dict[str, Dict[str, Any]] = {
    ESIndexNames.DOCS: {
        "settings": {
            "analysis": {
                "analyzer": {
                    "ru_en_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "icu_folding", "russian", "english"]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "document_id": {"type": "keyword"},
                "title": {
                    "type": "text",
                    "analyzer": "ru_en_analyzer",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "source_type": {"type": "keyword"},
                "language": {"type": "keyword"},
                "year": {"type": "integer"},
                "authors": {"type": "text", "analyzer": "ru_en_analyzer"},
                "organizations": {"type": "text", "analyzer": "ru_en_analyzer"},
                "geography": {"type": "text", "analyzer": "ru_en_analyzer"},
                "practice_region": {"type": "keyword"},
                "domains": {"type": "keyword"},
                "access_level": {"type": "keyword"},
            }
        }
    },
    ESIndexNames.CHUNKS: {
        "settings": {
            "analysis": {
                "analyzer": {
                    "ru_en_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "icu_folding", "russian", "english"]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "chunk_id": {"type": "keyword"},
                "document_id": {"type": "keyword"},
                "text": {
                    "type": "text",
                    "analyzer": "ru_en_analyzer",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "language": {"type": "keyword"},
                "page": {"type": "integer"},
                "section": {"type": "keyword"},
                "year": {"type": "integer"},
                "source_type": {"type": "keyword"},
                "geography": {"type": "text", "analyzer": "ru_en_analyzer"},
                "practice_region": {"type": "keyword"},
                "access_level": {"type": "keyword"},
                "entities": {"type": "keyword"},
                "numeric_conditions": {
                    "type": "nested",
                    "properties": {
                        "property": {"type": "keyword"},
                        "min_value": {"type": "float"},
                        "max_value": {"type": "float"},
                        "unit": {"type": "keyword"},
                        "raw_text": {"type": "text", "analyzer": "ru_en_analyzer"}
                    }
                },
                "embedding": {
                    "type": "dense_vector",
                    "dims": get_vector_dimension(),
                    "index": True,
                    "similarity": "cosine"
                }
            }
        }
    },
    ESIndexNames.FACTS: {
        "mappings": {
            "properties": {
                "fact_id": {"type": "keyword"},
                "subject": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "type": {"type": "keyword"},
                        "name": {"type": "text", "analyzer": "standard"}
                    }
                },
                "predicate": {"type": "keyword"},
                "object": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "type": {"type": "keyword"},
                        "name": {"type": "text", "analyzer": "standard"}
                    }
                },
                "numeric": {
                    "properties": {
                        "property": {"type": "keyword"},
                        "min_value": {"type": "float"},
                        "max_value": {"type": "float"},
                        "unit": {"type": "keyword"}
                    }
                },
                "source_document_id": {"type": "keyword"},
                "source_chunk_id": {"type": "keyword"},
                "confidence": {"type": "float"},
                "verification_status": {"type": "keyword"},
                "access_level": {"type": "keyword"},
            }
        }
    },
    ESIndexNames.ENTITIES: {
        "mappings": {
            "properties": {
                "entity_id": {"type": "keyword"},
                "name": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "canonical_name": {"type": "keyword"},
                "type": {"type": "keyword"},
                "aliases": {"type": "keyword"},
                "access_level": {"type": "keyword"},
            }
        }
    },
    ESIndexNames.EXPERIMENTS: {
        "mappings": {
            "properties": {
                "experiment_id": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "standard"},
                "description": {"type": "text", "analyzer": "standard"},
                "document_id": {"type": "keyword"},
                "access_level": {"type": "keyword"},
            }
        }
    },
    ESIndexNames.EXPERTS: {
        "mappings": {
            "properties": {
                "expert_id": {"type": "keyword"},
                "name": {"type": "text", "analyzer": "standard"},
                "organization": {"type": "text", "analyzer": "standard"},
                "expertise": {"type": "keyword"},
                "access_level": {"type": "keyword"},
            }
        }
    }
}
