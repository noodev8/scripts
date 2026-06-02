"""Birkenstock size-weight curves for stock availability scoring."""

WOMENS = {35: 0.02, 36: 0.05, 37: 0.10, 38: 0.18, 39: 0.22, 40: 0.18, 41: 0.12, 42: 0.08, 43: 0.05}
MENS   = {39: 0.04, 40: 0.10, 41: 0.16, 42: 0.20, 43: 0.20, 44: 0.15, 45: 0.10, 46: 0.04, 47: 0.01}

WOMENS_TRIGGER_MAX_SIZE = 37

# Pseudocount strength for per-model size curves. A model needs ~SHRINK_K units
# of its own sales before its size mix outweighs the generic prior; below that it
# stays close to the prior. Also guarantees every prior size keeps a non-zero
# weight, so a size that happens to be OOS brand-wide right now is never scored
# as "free to be missing" (the OOS-censoring trap).
SHRINK_K = 30


def curve_for(size_universe):
    if any(s <= WOMENS_TRIGGER_MAX_SIZE for s in size_universe):
        return WOMENS
    return MENS


def blend_curve(prior, size_units):
    """Shrink an empirical per-model size distribution toward `prior`.

    prior: {size: weight} summing to 1.0 (WOMENS or MENS).
    size_units: {size: units sold} for one (model, gender) over the curve window.
    Returns {size: weight} over the prior's sizes, summing to 1.0. With no sales
    it returns the prior unchanged; with plenty it approaches the model's own mix.
    """
    n = sum(size_units.get(sz, 0) for sz in prior)
    denom = n + SHRINK_K
    return {sz: (size_units.get(sz, 0) + SHRINK_K * g) / denom for sz, g in prior.items()}
