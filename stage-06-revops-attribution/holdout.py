import numpy as np

rng = np.random.default_rng(7)

def holdout(odds_multiplier, n):
    intent = rng.beta(2, 5, n)
    treated = rng.random(n) < 0.5
    logit = -3.2 + 4 * intent + np.where(treated, np.log(odds_multiplier), 0)
    opp = rng.random(n) < 0.35 + 0.4 * intent
    won = opp & (rng.random(n) < 1 / (1 + np.exp(-logit)))
    p1, p0 = won[treated].mean(), won[~treated].mean()
    se = np.sqrt(p1 * (1 - p1) / treated.sum() + p0 * (1 - p0) / (~treated).sum())
    return p1 - p0, 1.96 * se

print("=== RANDOMIZED HOLDOUT EXPERIMENT ===")
for name, mult in [("webinar", 2.0), ("linkedin_ads", 1.15), ("cold_email", 1.10)]:
    for n in (4_000, 100_000):
        lift, ci = holdout(mult, n)
        print(f"{name:13} n={n:>7,}  lift {lift:+.3f} +/- {ci:.3f}  {'clear' if abs(lift) > ci else 'noise'}")
