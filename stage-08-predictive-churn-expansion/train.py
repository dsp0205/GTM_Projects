import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from features import FEATURES, build, load

WINDOW = pd.Timedelta(45, "D")
accounts, usage = load()
known = accounts[accounts["renewed"].notna()].set_index("account_id")
snap = known["renewal_date"] - WINDOW
X = build(known.reset_index(), usage, snap)
known = known.loc[X.index]
y = 1 - known["renewed"].astype(int)

cutoff = known["renewal_date"].quantile(0.7)
train = known["renewal_date"] < cutoff
test = known["renewal_date"] >= cutoff + WINDOW
print(f"train {train.sum()} (churn {y[train].mean():.1%})  test {test.sum()} (churn {y[test].mean():.1%})")

def precision_at_k(y_true, score, k):
    top = np.argsort(-np.asarray(score))[:k]
    return np.asarray(y_true)[top].mean()

def rules_score(f):
    usage_drop = np.clip((1 - f["ratio_28_prev28"]) / 0.5, 0, 1)
    trend = np.clip(-f["slope_12w"] / 0.15, 0, 1)
    silent = np.clip(f["days_since_call"] / 14, 0, 1)
    below_peak = np.clip((1 - f["drawdown"]) / 0.7, 0, 1)
    return 100 * (0.35 * usage_drop + 0.25 * trend + 0.20 * below_peak + 0.20 * silent)

models = {
    "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
    "boosting": HistGradientBoostingClassifier(max_iter=150, learning_rate=0.05,
                                               max_depth=3, random_state=0),
}
scores = {"rules": rules_score(X[test])}
for name, m in models.items():
    m.fit(X.loc[train, FEATURES], y[train])
    scores[name] = m.predict_proba(X.loc[test, FEATURES])[:, 1]

k = 25
print(f"base churn rate in test: {y[test].mean():.1%}")
for name, s in scores.items():
    print(f"{name:9s} AUC {roc_auc_score(y[test], s):.3f}  PR-AUC {average_precision_score(y[test], s):.3f}"
          f"  precision@{k} {precision_at_k(y[test], s, k):.2f}")

p = scores["boosting"]
frac_pos, mean_pred = calibration_curve(y[test], p, n_bins=5, strategy="quantile")
print("calibration (predicted -> actual):",
      " ".join(f"{a:.2f}->{b:.2f}" for a, b in zip(mean_pred, frac_pos)),
      f" Brier {brier_score_loss(y[test], p):.3f}")

joblib.dump(models["boosting"].fit(X[FEATURES], y), "churn_model.joblib")
print("Saved churn_model.joblib")
