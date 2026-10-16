import re
from pathlib import Path

RUBRIC_FILE = Path(__file__).resolve().parent.parent / "eval" / "labeling_rubric.md"


def load_rubric(path=RUBRIC_FILE):
    rubric, clause = {}, None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("## "):
            clause = line[3:].strip()
            rubric[clause] = {"Low": "", "Medium": "", "High": "", "notes": []}
        elif clause and line.startswith("- "):
            m = re.match(r"- (Low|Medium|High): (.+)", line)
            if m:
                rubric[clause][m.group(1)] = m.group(2)
            else:
                rubric[clause]["notes"].append(line[2:])
    rubric.pop("Rules", None)
    return rubric