from src.queries import CLAUSE_KEYWORDS, CLAUSE_QUERIES
from src.reference_clauses import REFERENCE


def test_every_reference_clause_has_search_queries():
    for name in REFERENCE:
        assert name in CLAUSE_QUERIES, f"missing question for {name}"
        assert name in CLAUSE_KEYWORDS, f"missing keywords for {name}"