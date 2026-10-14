import json
from pathlib import Path

import numpy as np

THRESHOLD_FILE = Path(__file__).resolve().parent.parent / "eval" / "thresholds.json"


def pick_threshold(positive_scores, target_recall=0.90):
    return float(np.quantile(np.asarray(positive_scores, dtype=float), 1 - target_recall))


def load_thresholds(path=THRESHOLD_FILE):
    return json.loads(Path(path).read_text())


def clause_is_present(clause, signals, thresholds):
    rule = thresholds[clause]
    return signals[rule["signal"]] >= rule["threshold"]