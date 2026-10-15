import json

from src.pipeline import review_contract

TEXT = "6.9 Governing Law. This Agreement is to be construed according to the laws of the State of Illinois."
CONTRACT = {"title": "t", "text": TEXT}
GOOD = json.dumps({
    "clause": "Governing Law", "found": True, "risk_level": "Low", "explanation": "e",
    "suggested_redline": "r", "cited_text": "construed according to the laws of the State of Illinois",
})
FAKED = GOOD.replace("construed according to the laws of the State of Illinois", "governed by French law")
TH = {
    "Governing Law": {"signal": "bm25", "threshold": 5.0},
    "Renewal Term": {"signal": None, "threshold": None},
}


def ranker(score):
    return lambda contract, clause: [{"start": 0, "end": len(TEXT), "text": TEXT, "score": score}]


def llm_returning(reply):
    calls = []

    def llm(system, user):
        calls.append(1)
        return reply

    llm.calls = calls
    return llm


def run(score, reply, clauses):
    llm = llm_returning(reply)
    out = review_contract(CONTRACT, ranker(0), {"bm25": ranker(score)}, TH, llm, clauses=clauses)
    return out, llm


def test_gate_blocks_without_calling_the_llm():
    out, llm = run(1.0, GOOD, ["Governing Law"])
    assert (out[0].status, out[0].decided_by) == ("not_found", "gate")
    assert len(llm.calls) == 0


def test_gate_passes_then_llm_answers_with_positions():
    out, llm = run(9.0, GOOD, ["Governing Law"])
    assert (out[0].status, out[0].decided_by) == ("found", "llm")
    assert out[0].finding.citation_start is not None


def test_ungated_clause_always_asks_the_llm():
    reply = json.dumps({"clause": "Renewal Term", "found": False})
    out, llm = run(0.0, reply, ["Renewal Term"])
    assert (out[0].status, out[0].decided_by) == ("not_found", "llm")
    assert len(llm.calls) == 1


def test_unverifiable_quote_is_flagged_not_hidden():
    out, llm = run(9.0, FAKED, ["Governing Law"])
    assert (out[0].status, out[0].decided_by) == ("unverified", "verifier")
    assert len(llm.calls) == 2
    
