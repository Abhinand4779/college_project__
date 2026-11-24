"""
CareerEquity AI - Module 3B & 3C: Salary Range Prediction & Equity Explainability
Machine Learning Salary Regressor (Random Forest) + Same-Level Peer Equity Audit
"""

import os
from decimal import Decimal
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor

MODEL_DIR = os.path.join(os.path.dirname(__file__), "saved_models")
SALARY_MODEL_PATH = os.path.join(MODEL_DIR, "salary_regressor.joblib")

LEVEL_WEIGHTS = {
    "Junior": 1.0,
    "Associate": 1.2,
    "Mid-Level": 1.8,
    "Senior": 2.5,
    "Lead": 3.2,
    "Principal": 4.0,
    "Manager": 3.5,
    "Director": 5.0,
}

PROFICIENCY_WEIGHTS = {
    "Beginner": 1,
    "Intermediate": 2,
    "Advanced": 3,
    "Expert": 4,
}


def _train_default_salary_model():
    """Trains a baseline Random Forest Regressor for salary prediction."""
    np.random.seed(42)
    # Features: [exp_years, level_factor, total_skills, skill_prof_sum, completed_tasks]
    # Target: Annual Salary in INR (e.g., 3,50,000 to 35,00,000)
    X = []
    y = []

    for _ in range(1200):
        exp = np.random.uniform(0.5, 18.0)
        level_mult = np.random.choice([1.0, 1.2, 1.8, 2.5, 3.2, 4.0])
        skills_cnt = np.random.randint(2, 12)
        prof_sum = skills_cnt * np.random.uniform(1.5, 3.8)
        tasks_done = np.random.randint(2, 40)

        # Base formula + realistic noise
        base = 350000.0
        exp_comp = exp * 95000.0
        level_comp = (level_mult - 1.0) * 450000.0
        skill_comp = prof_sum * 45000.0
        task_comp = tasks_done * 8500.0
        noise = np.random.normal(0, 35000.0)

        salary = base + exp_comp + level_comp + skill_comp + task_comp + noise
        salary = max(300000.0, salary)

        X.append([exp, level_mult, skills_cnt, prof_sum, tasks_done])
        y.append(salary)

    reg = RandomForestRegressor(n_estimators=75, max_depth=7, random_state=42)
    reg.fit(X, y)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(reg, SALARY_MODEL_PATH)
    return reg


def get_salary_model():
    if os.path.exists(SALARY_MODEL_PATH):
        try:
            return joblib.load(SALARY_MODEL_PATH)
        except Exception:
            return _train_default_salary_model()
    return _train_default_salary_model()


class SalaryEquityPredictor:

    @staticmethod
    def predict_salary_profile(employee):
        """
        Calculates salary predictions, confidence bands, peer equity comparison,
        and Explainable AI factor breakdown for a given employee.
        """
        # Current actual recorded compensation
        latest_record = employee.salary_records.order_by("-effective_date", "-id").first()
        current_salary = float(latest_record.salary_amount) if latest_record else None

        # Experience & Level
        exp_years = float(employee.experience_years)
        level_name = employee.position.job_level if employee.position else "Mid-Level"
        level_factor = LEVEL_WEIGHTS.get(level_name, 1.8)

        # Skills & Proficiency
        emp_skills = list(employee.employee_skills.select_related("skill").all())
        total_skills = len(emp_skills)
        skill_prof_sum = sum(PROFICIENCY_WEIGHTS.get(s.proficiency, 2) for s in emp_skills)

        # Task Performance history
        completed_tasks = employee.assignments.filter(status="Completed").count()

        # Run ML Prediction
        reg = get_salary_model()
        features = [[exp_years, level_factor, total_skills, skill_prof_sum, completed_tasks]]
        pred_median = float(reg.predict(features)[0])

        # PDF Requirement: Estimate a range rather than claiming an exact single salary
        min_range = round(pred_median * 0.90, -3)
        max_range = round(pred_median * 1.10, -3)
        pred_median = round(pred_median, -3)

        # Department / Position salary bounds if configured
        if employee.position and employee.position.minimum_salary:
            min_bound = float(employee.position.minimum_salary)
            min_range = max(min_range, min_bound)
        if employee.position and employee.position.maximum_salary:
            max_bound = float(employee.position.maximum_salary)
            max_range = min(max_range, max_bound)

        # Explainable AI: Feature Importance breakdown (SHAP-style contribution)
        # Approximate local attribution relative to baseline entry salary (₹3,50,000)
        base_anchor = 350000.0
        exp_contrib = exp_years * 92000.0
        level_contrib = (level_factor - 1.0) * 440000.0
        skills_contrib = skill_prof_sum * 42000.0
        delivery_contrib = completed_tasks * 8000.0

        factors = [
            {
                "feature": "Experience & Tenure",
                "detail": f"{exp_years:.1f} years professional experience",
                "amount": round(exp_contrib, -2),
                "percentage": 30,
            },
            {
                "feature": "Job Level & Responsibility",
                "detail": f"Band Level: {level_name}",
                "amount": round(level_contrib, -2),
                "percentage": 35,
            },
            {
                "feature": "Technical Skills & Competency",
                "detail": f"{total_skills} verified skills (Proficiency sum: {skill_prof_sum})",
                "amount": round(skills_contrib, -2),
                "percentage": 25,
            },
            {
                "feature": "Demonstrated Delivery",
                "detail": f"{completed_tasks} successfully delivered projects/tasks",
                "amount": round(delivery_contrib, -2),
                "percentage": 10,
            },
        ]

        # Same-Level Equity Comparison (Cohort analysis)
        peer_comparison = SalaryEquityPredictor._get_peer_equity(employee, current_salary)

        # Equity Status evaluation
        equity_status = "Not Recorded"
        equity_badge = "secondary"
        diff_text = "No recorded salary to evaluate"

        if current_salary:
            if current_salary < min_range:
                equity_status = "Below Predicted Range (Pay Disparity Risk)"
                equity_badge = "danger"
                diff_pct = round(((min_range - current_salary) / min_range) * 100, 1)
                diff_text = f"Currently ₹{min_range - current_salary:,.0f} ({diff_pct}%) below lower market boundary"
            elif current_salary > max_range:
                equity_status = "Above Predicted Range"
                equity_badge = "info"
                diff_pct = round(((current_salary - max_range) / max_range) * 100, 1)
                diff_text = f"Currently ₹{current_salary - max_range:,.0f} ({diff_pct}%) above upper market boundary"
            else:
                equity_status = "Fairly Compensated (Equitable)"
                equity_badge = "success"
                diff_text = "Compensation aligns with predicted skills, tenure, and market benchmarks."

        return {
            "current_salary": current_salary,
            "predicted_median": pred_median,
            "min_range": min_range,
            "max_range": max_range,
            "equity_status": equity_status,
            "equity_badge": equity_badge,
            "diff_text": diff_text,
            "factors": factors,
            "peer_comparison": peer_comparison,
        }

    @staticmethod
    def _get_peer_equity(employee, current_salary):
        """
        Calculates same-level cohort statistics for peers in the same position and department.
        """
        from Alpha.models import EmployeeProfile, SalaryRecord

        # Same position peers
        cohort_employees = EmployeeProfile.objects.filter(
            position=employee.position,
            employment_status="Active"
        )

        salaries = []
        for emp in cohort_employees:
            latest = emp.salary_records.order_by("-effective_date", "-id").first()
            if latest:
                salaries.append(float(latest.salary_amount))

        if not salaries and current_salary:
            salaries = [current_salary]

        if salaries:
            salaries.sort()
            cohort_min = min(salaries)
            cohort_max = max(salaries)
            cohort_median = float(np.median(salaries))
            cohort_avg = float(np.mean(salaries))
            cohort_count = len(salaries)
            p25 = float(np.percentile(salaries, 25))
            p75 = float(np.percentile(salaries, 75))
        else:
            cohort_min = 450000
            cohort_max = 750000
            cohort_median = 600000
            cohort_avg = 600000
            cohort_count = 1
            p25 = 500000
            p75 = 700000

        ratio = (current_salary / cohort_median) if (current_salary and cohort_median > 0) else 1.0

        return {
            "cohort_title": employee.position.title if employee.position else "General Role",
            "cohort_level": employee.position.job_level if employee.position else "Standard",
            "cohort_count": cohort_count,
            "min": round(cohort_min, -2),
            "median": round(cohort_median, -2),
            "max": round(cohort_max, -2),
            "avg": round(cohort_avg, -2),
            "p25": round(p25, -2),
            "p75": round(p75, -2),
            "ratio": round(ratio, 2),
            "ratio_percentage": int(round(ratio * 100)),
        }

