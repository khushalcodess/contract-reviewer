import json
from pathlib import Path

CUAD_PATH = Path(__file__).resolve().parent.parent / "data" / "CUAD_v1" / "CUAD_v1.json"

TARGET_CLAUSES = [
    "Governing Law",
    "Renewal Term",
    "Notice Period To Terminate Renewal",
    "Termination For Convenience",
    "Non-Compete",
    "Cap On Liability",
    "Uncapped Liability",
]


def load_cuad(path=CUAD_PATH):
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    contracts = []
    for c in raw["data"]:
        para = c["paragraphs"][0]
        gold = {}
        for qa in para["qas"]:
            clause = qa["id"].split("__")[-1]
            if clause in TARGET_CLAUSES:
                gold[clause] = [
                    (a["answer_start"], a["answer_start"] + len(a["text"]))
                    for a in qa["answers"]
                ]
        contracts.append({"title": c["title"], "text": para["context"], "gold": gold})
    return contracts