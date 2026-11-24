"""
CareerEquity AI - ML Training & Evaluation Script
Trains Random Forest Classifier (Workload) and Random Forest Regressor (Salary)
"""

from Alpha.ml_engine.workload_model import _train_default_workload_model
from Alpha.ml_engine.salary_model import _train_default_salary_model


def train_all_models():
    print("[CareerEquity AI] Training Workload Risk Classifier (Random Forest)...")
    clf = _train_default_workload_model()
    print(f"[CareerEquity AI] Workload Classifier trained. Estimators: {len(clf.estimators_)}")

    print("[CareerEquity AI] Training Salary Range Regressor (Random Forest)...")
    reg = _train_default_salary_model()
    print(f"[CareerEquity AI] Salary Regressor trained. Estimators: {len(reg.estimators_)}")
    print("[CareerEquity AI] All ML models successfully saved in saved_models/ directory.")


if __name__ == "__main__":
    train_all_models()

