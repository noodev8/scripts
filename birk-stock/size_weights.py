"""Birkenstock size-weight curves for stock availability scoring."""

WOMENS = {35: 0.02, 36: 0.05, 37: 0.10, 38: 0.18, 39: 0.22, 40: 0.18, 41: 0.12, 42: 0.08, 43: 0.05}
MENS   = {39: 0.04, 40: 0.10, 41: 0.16, 42: 0.20, 43: 0.20, 44: 0.15, 45: 0.10, 46: 0.04, 47: 0.01}

WOMENS_TRIGGER_MAX_SIZE = 37


def curve_for(size_universe):
    if any(s <= WOMENS_TRIGGER_MAX_SIZE for s in size_universe):
        return WOMENS
    return MENS
