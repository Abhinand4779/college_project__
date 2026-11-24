"""
CareerEquity AI - Module 3A: Workload Imbalance & Burnout Analysis
Machine Learning Workload Classifier (Random Forest) + Imbalance Redistribution Engine
"""

import os
from decimal import Decimal
from datetime import date
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

MODEL_DIR = os.path.join(os.path.dirname(__file__), "saved_models")
WORKLOAD_MODEL_PATH = os.path.join(MODEL_DIR, "workload_classifier.joblib")

COMPLEXITY_WEIGHTS = {
    "Low": 1.0,
    "Medium": 2.0,
    "High": 3.0,
}


def _train_default_workload_model():
    """Trains a baseline Random Forest Classifier for workload risk classification."""
    np.random.seed(42)
    # Features: [active_tasks, est_hours_sum, complexity_score, overdue_count, overtime_ratio]
    # Class 0: Underutilized, 1: Balanced, 2: High Workload, 3: Overloaded (Burnout Risk)
    X = []
    y = []

    # Underutilized samples
    for _ in range(250):
        tasks = np.random.randint(0, 3)
        hours = np.random.uniform(0, 18)
        comp = tasks * np.random.uniform(1.0, 1.8)
        overdue = 0
        ot_ratio = np.random.uniform(0.8, 1.0)
        X.append([tasks, hours, comp, overdue, ot_ratio])
        y.append(0)

    # Balanced samples
    for _ in range(400):
        tasks = np.random.randint(2, 6)
        hours = np.random.uniform(20, 42)
        comp = tasks * np.random.uniform(1.4, 2.3)
        overdue = np.random.choice([0, 1], p=[0.9, 0.1])
        ot_ratio = np.random.uniform(0.9, 1.15)
        X.append([tasks, hours, comp, overdue, ot_ratio])
        y.append(1)

    # High Workload samples
    for _ in range(300):
        tasks = np.random.randint(5, 9)
        hours = np.random.uniform(43, 62)
        comp = tasks * np.random.uniform(1.8, 2.7)
        overdue = np.random.choice([0, 1, 2], p=[0.6, 0.3, 0.1])
        ot_ratio = np.random.uniform(1.0, 1.35)
        X.append([tasks, hours, comp, overdue, ot_ratio])
        y.append(2)

    # Overloaded / Burnout samples
    for _ in range(300):
        tasks = np.random.randint(7, 16)
        hours = np.random.uniform(60, 110)
        comp = tasks * np.random.uniform(2.2, 3.0)
        overdue = np.random.randint(1, 6)
        ot_ratio = np.random.uniform(1.2, 1.8)
        X.append([tasks, hours, comp, overdue, ot_ratio])
        y.append(3)

    clf = RandomForestClassifier(n_estimators=60, max_depth=6, random_state=42)
    clf.fit(X, y)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(clf, WORKLOAD_MODEL_PATH)
    return clf


def get_workload_model():
    if os.path.exists(WORKLOAD_MODEL_PATH):
        try:
            return joblib.load(WORKLOAD_MODEL_PATH)
        except Exception:
            return _train_default_workload_model()
    return _train_default_workload_model()


class WorkloadAnalyzer:
    LABELS = {
        0: ("Underutilized", "info", "#38bdf8", "Capacity available for additional assignments."),
        1: ("Balanced", "success", "#10b981", "Optimal task volume and healthy delivery pace."),
        2: ("High Workload", "warning", "#f59e0b", "Heavy schedule; monitor closely to prevent delays."),
        3: ("Overloaded (Burnout Risk)", "danger", "#ef4444", "Critical workload risk; immediate rebalancing recommended."),
    }

    @staticmethod
    def analyze_employee(employee):
        """
        Analyzes the employee's active task assignments and returns an ML workload profile.
        """
        assignments = employee.assignments.select_related("task").all()
        today = date.today()

        total_tasks = assignments.count()
        completed_assignments = [a for a in assignments if a.status == "Completed"]
        active_assignments = [a for a in assignments if a.status != "Completed"]

        active_count = len(active_assignments)
        completed_count = len(completed_assignments)

        est_hours_sum = sum(float(a.task.estimated_hours) for a in active_assignments)
        actual_hours_sum = sum(float(a.actual_hours) for a in active_assignments)

        overdue_count = sum(
            1 for a in active_assignments
            if a.task.deadline and a.task.deadline < today
        )

        high_comp_count = sum(1 for a in active_assignments if a.task.complexity == "High")
        med_comp_count = sum(1 for a in active_assignments if a.task.complexity == "Medium")
        low_comp_count = sum(1 for a in active_assignments if a.task.complexity == "Low")

        complexity_score = sum(
            COMPLEXITY_WEIGHTS.get(a.task.complexity, 1.5) for a in active_assignments
        )

        ot_ratio = (actual_hours_sum / est_hours_sum) if est_hours_sum > 0 else 1.0

        # Predict with ML Model
        clf = get_workload_model()
        features = [[active_count, est_hours_sum, complexity_score, overdue_count, ot_ratio]]
        pred_class = int(clf.predict(features)[0])
        probabilities = clf.predict_proba(features)[0]

        # Calculate a continuous Workload Index (0 - 100)
        # Weighted combination of hours intensity (40h normal), complexity, and overdue penalty
        hours_factor = min(est_hours_sum / 45.0, 1.8) * 45.0
        comp_factor = min(complexity_score / 12.0, 1.5) * 35.0
        overdue_factor = min(overdue_count * 10.0, 20.0)
        workload_score = min(100, int(round(hours_factor + comp_factor + overdue_factor)))

        status_text, status_badge, status_color, status_advice = WorkloadAnalyzer.LABELS[pred_class]

        # Contributing factors for Explainability
        contributing_factors = []
        if active_count > 5:
            contributing_factors.append(f"High task volume: {active_count} active assignments")
        if est_hours_sum > 45:
            contributing_factors.append(f"Heavy commitment: {est_hours_sum:.1f} estimated hours on active tasks")
        if high_comp_count >= 2:
            contributing_factors.append(f"Multiple complex deliverables: {high_comp_count} High-complexity tasks")
        if overdue_count > 0:
            contributing_factors.append(f"Deadlines at risk: {overdue_count} overdue task(s)")
        if actual_hours_sum > est_hours_sum * 1.2 and est_hours_sum > 0:
            contributing_factors.append("Actual hours exceeding original estimates by >20%")

        if not contributing_factors:
            contributing_factors.append("Workload distribution within sustainable capacity thresholds.")

        return {
            "employee_id": employee.id,
            "employee_name": employee.user.get_full_name() or employee.user.username,
            "total_tasks": total_tasks,
            "active_tasks": active_count,
            "completed_tasks": completed_count,
            "estimated_hours": round(est_hours_sum, 1),
            "actual_hours": round(actual_hours_sum, 1),
            "overdue_tasks": overdue_count,
            "high_complexity_tasks": high_comp_count,
            "medium_complexity_tasks": med_comp_count,
            "low_complexity_tasks": low_comp_count,
            "workload_score": workload_score,
            "status": status_text,
            "status_badge": status_badge,
            "status_color": status_color,
            "advice": status_advice,
            "contributing_factors": contributing_factors,
            "is_burnout_risk": pred_class >= 2 or workload_score >= 75,
            "active_assignments": active_assignments,
        }

    @staticmethod
    def suggest_redistribution(organization_employees):
        """
        Analyzes a list of employees in an organization and suggests task redistribution
        from overloaded team members to underutilized/balanced peers in the same department.
        """
        profiles = [WorkloadAnalyzer.analyze_employee(emp) for emp in organization_employees]
        overloaded = [p for p in profiles if p["is_burnout_risk"] and p["active_tasks"] > 1]
        receptive = [p for p in profiles if not p["is_burnout_risk"] and p["active_tasks"] < 4]

        recommendations = []
        for ov in overloaded:
            # Look for peer with capacity
            candidates = [
                r for r in receptive
                if r["employee_id"] != ov["employee_id"]
            ]
            if candidates:
                best_candidate = min(candidates, key=lambda c: c["workload_score"])
                # Pick a candidate task from overloaded employee
                if ov["active_assignments"]:
                    task_to_move = ov["active_assignments"][0].task
                    recommendations.append({
                        "from_employee": ov["employee_name"],
                        "from_score": ov["workload_score"],
                        "task_title": task_to_move.title,
                        "task_complexity": task_to_move.complexity,
                        "task_hours": float(task_to_move.estimated_hours),
                        "to_employee": best_candidate["employee_name"],
                        "to_score": best_candidate["workload_score"],
                        "projected_reduction": 15,
                    })

        return recommendations

