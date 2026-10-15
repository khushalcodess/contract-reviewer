import time
from typing import Literal, Optional

from pydantic import BaseModel

from src.abstain import clause_is_present
from src.generate import review_clause
from src.reference_clauses import REFERENCE
from src.schema import ClauseFinding


class ClauseResult(BaseModel):
    clause: str
    status: Literal["found", "not_found", "unverified"]
    decided_by: Literal["gate", "llm", "verifier"]
    finding: Optional[ClauseFinding] = None


def review_contract(contract, hybrid, signal_rankers, thresholds, llm,
                    clauses=None, k=3, pause=0.0):
    results = []
    for clause in clauses or list(REFERENCE):
        rule = thresholds.get(clause)
        signals = {}
        if rule and rule["signal"]:
            name = rule["signal"]
            signals[name] = signal_rankers[name](contract, clause)[0]["score"]

        if not clause_is_present(clause, signals, thresholds):
            results.append(ClauseResult(
                clause=clause, status="not_found", decided_by="gate",
                finding=ClauseFinding(clause=clause, found=False),
            ))
            continue

        passages = hybrid(contract, clause)[:k]
        finding = review_clause(contract["text"], clause, passages, llm)
        if finding is None:
            results.append(ClauseResult(clause=clause, status="unverified", decided_by="verifier"))
        else:
            results.append(ClauseResult(
                clause=clause,
                status="found" if finding.found else "not_found",
                decided_by="llm", finding=finding,
            ))
        if pause:
            time.sleep(pause)
    return results  