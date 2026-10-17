import json

from src.generate import build_prompt, parse_json, review_clause

TEXT = "6.9 Governing Law. This Agreement is to be construed according to the laws    of the State of Illinois."
PASSAGES = [{"start": 0, "end": len(TEXT), "text": TEXT}]
GOOD = {
    "clause": "Governing Law", "found": True, "risk_level": "Low",
    "explanation": "e", "suggested_redline": "r",
    "cited_text": "construed according to the laws of the State of Illinois",
}
FAKED = {**GOOD, "cited_text": "governed by the laws of France"}


def fake(*replies):
    it = iter(replies)
    calls = []

    def llm(system, user):
        calls.append(user)
        return next(it)

    llm.calls = calls
    return llm


def test_valid_answer_gets_positions():
    f = review_clause(TEXT, "Governing Law", PASSAGES, fake(json.dumps(GOOD)))
    assert f.found and TEXT[f.citation_start : f.citation_end].lower().startswith("construed")


def test_fabricated_quote_is_retried_then_accepted():
    llm = fake(json.dumps(FAKED), json.dumps(GOOD))
    f = review_clause(TEXT, "Governing Law", PASSAGES, llm)
    assert f is not None and len(llm.calls) == 2 and "rejected" in llm.calls[1]


def test_always_fabricated_returns_none():
    llm = fake(json.dumps(FAKED), json.dumps(FAKED))
    assert review_clause(TEXT, "Governing Law", PASSAGES, llm) is None


def test_not_found_passes_through():
    reply = json.dumps({"clause": "Governing Law", "found": False})
    f = review_clause(TEXT, "Governing Law", PASSAGES, fake(reply))
    assert f.found is False


def test_code_fence_and_chatter_are_tolerated():
    assert parse_json("Sure!\n```json\n" + json.dumps(GOOD) + "\n```")["found"] is True


def test_garbage_twice_returns_none():
    assert review_clause(TEXT, "Governing Law", PASSAGES, fake("nope", "still nope")) is None


def test_prompt_wraps_passages_in_tags():
    p = build_prompt("Governing Law", PASSAGES)
    assert "<passages>" in p and "Illinois" in p

def test_prompt_contains_rubric_and_customer():
    p = build_prompt("Governing Law", PASSAGES, customer="Acme Corp")
    assert "Acme Corp" in p and "- Low:" in p and "- High:" in p


def test_prompt_without_customer_says_not_to_guess():
    assert "not named" in build_prompt("Governing Law", PASSAGES)


def test_old_example_lists_are_gone():
    assert "High risk examples" not in build_prompt("Governing Law", PASSAGES)

def test_prompt_has_not_this_clause_hint():
    assert "Not this clause" in build_prompt("Non-Compete", PASSAGES)
    assert "Not this clause" not in build_prompt("Governing Law", PASSAGES)