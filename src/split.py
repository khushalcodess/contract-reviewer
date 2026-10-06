import random
from collections import defaultdict


def company_key(title):
    return title.split("_")[0].lower()


def split_contracts(contracts, test_frac=0.3, seed=42):
    groups = defaultdict(list)
    for i, c in enumerate(contracts):
        groups[company_key(c["title"])].append(i)

    keys = sorted(groups)
    random.Random(seed).shuffle(keys)

    target = int(len(contracts) * test_frac)
    dev_idx, test_idx = [], []
    for k in keys:
        if len(test_idx) < target:
            test_idx += groups[k]
        else:
            dev_idx += groups[k]
    return sorted(dev_idx), sorted(test_idx)