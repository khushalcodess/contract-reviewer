from typing import Literal, Optional

from pydantic import BaseModel, model_validator

RiskLevel = Literal["Low", "Medium", "High"]
DETAIL_FIELDS = ("risk_level", "explanation", "cited_text", "suggested_redline")


class ClauseFinding(BaseModel):
    clause: str
    found: bool
    risk_level: Optional[RiskLevel] = None
    explanation: Optional[str] = None
    cited_text: Optional[str] = None
    suggested_redline: Optional[str] = None
    citation_start: Optional[int] = None
    citation_end: Optional[int] = None

    @model_validator(mode="after")
    def check_consistency(self):
        present = [f for f in DETAIL_FIELDS if getattr(self, f)]
        if self.found and len(present) != len(DETAIL_FIELDS):
            missing = sorted(set(DETAIL_FIELDS) - set(present))
            raise ValueError(f"found=True but missing: {missing}")
        if not self.found and present:
            raise ValueError("found=False must not contain risk, explanation, citation or redline")
        return self