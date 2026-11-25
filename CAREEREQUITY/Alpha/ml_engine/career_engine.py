"""
CareerEquity AI - Module 3D, 3E, 3F: Career Progression & Promotion Readiness
Skill Gap Analyzer, Readiness Scoring & Dynamic Milestone Roadmap Generator
"""

from decimal import Decimal
import numpy as np

PROFICIENCY_SCORES = {
    "Beginner": 1,
    "Intermediate": 2,
    "Advanced": 3,
    "Expert": 4,
}


class CareerProgressionAdvisor:

    @staticmethod
    def analyze_readiness(employee, target_position=None):
        """
        Compares employee's competencies against a target position
        and calculates promotion readiness, skill gaps, and milestone roadmap.
        """
        # If no target position provided, check employee's profile or default to next level in department
        target = target_position or employee.target_position
        if not target and employee.department:
            # Pick a higher level position in the same department
            target = employee.department.positions.exclude(id=employee.position.id).first()

        current_position = employee.position

        # If still no target, return a minimal guidance object
        if not target:
            return {
                "has_target": False,
                "target_position": None,
                "readiness_score": 0,
                "skill_match_percentage": 0,
                "exp_match_percentage": 0,
                "matched_skills": [],
                "developing_skills": [],
                "missing_skills": [],
                "roadmap": [],
            }

        # 1. Experience Alignment
        current_exp = float(employee.experience_years)
        req_exp = float(target.required_experience) if target.required_experience else 2.0
        exp_gap = max(0.0, round(req_exp - current_exp, 1))
        exp_match_pct = min(100, int(round((current_exp / req_exp) * 100))) if req_exp > 0 else 100

        # 2. Skill Gap Comparison
        emp_skills_dict = {
            es.skill.name.lower(): (es.skill.name, es.proficiency, PROFICIENCY_SCORES.get(es.proficiency, 1))
            for es in employee.employee_skills.select_related("skill").all()
        }

        # Get position requirements
        requirements = list(target.requirements.select_related("skill").all())

        matched_skills = []
        developing_skills = []
        missing_skills = []

        total_req_points = 0
        earned_points = 0

        if requirements:
            for req in requirements:
                req_name = req.skill.name
                req_prof = req.required_proficiency
                req_score = PROFICIENCY_SCORES.get(req_prof, 2)
                total_req_points += req_score

                skill_key = req_name.lower()
                if skill_key in emp_skills_dict:
                    actual_name, actual_prof, actual_score = emp_skills_dict[skill_key]
                    if actual_score >= req_score:
                        earned_points += req_score
                        matched_skills.append({
                            "name": actual_name,
                            "current_prof": actual_prof,
                            "required_prof": req_prof,
                            "status": "Matched",
                            "badge": "success",
                        })
                    else:
                        earned_points += actual_score
                        developing_skills.append({
                            "name": actual_name,
                            "current_prof": actual_prof,
                            "required_prof": req_prof,
                            "status": "Proficiency Gap",
                            "badge": "warning",
                            "action": f"Upgrade proficiency from {actual_prof} to {req_prof}",
                        })
                else:
                    missing_skills.append({
                        "name": req_name,
                        "current_prof": "Not Acquired",
                        "required_prof": req_prof,
                        "status": "Missing Competency",
                        "badge": "danger",
                        "action": f"Acquire fundamental knowledge and reach {req_prof} level",
                    })

            skill_match_pct = int(round((earned_points / total_req_points) * 100)) if total_req_points > 0 else 50
        else:
            # Fallback when position has no explicit requirements linked yet
            skill_match_pct = 70
            matched_skills = [
                {"name": s.skill.name, "current_prof": s.proficiency, "required_prof": "Intermediate", "status": "Matched", "badge": "success"}
                for s in employee.employee_skills.all()[:4]
            ]

        # 3. Task Delivery Track Record
        assignments = employee.assignments.all()
        completed = assignments.filter(status="Completed").count()
        total_tasks = assignments.count()
        task_success_rate = (completed / total_tasks * 100) if total_tasks > 0 else 80

        # 4. Overall Readiness Index (0 - 100%)
        # Weighted: 55% Skills, 30% Experience, 15% Execution Track Record
        readiness_score = int(round(
            (skill_match_pct * 0.55) +
            (exp_match_pct * 0.30) +
            (min(100, task_success_rate) * 0.15)
        ))
        readiness_score = max(5, min(100, readiness_score))

        # Readiness classification
        if readiness_score >= 85:
            readiness_label = "Ready for Promotion Consideration"
            readiness_badge = "success"
        elif readiness_score >= 65:
            readiness_label = "Strong Progress (Near Readiness)"
            readiness_badge = "info"
        elif readiness_score >= 40:
            readiness_label = "Actively Developing"
            readiness_badge = "warning"
        else:
            readiness_label = "Early Development Stage"
            readiness_badge = "secondary"

        # 5. Generate Personalized Step-by-Step Development Roadmap
        roadmap = CareerProgressionAdvisor._build_roadmap(
            target, missing_skills, developing_skills, exp_gap, readiness_score
        )

        return {
            "has_target": True,
            "target_position": target,
            "current_position": current_position,
            "readiness_score": readiness_score,
            "readiness_percentage": readiness_score,
            "current_stage_number": 3 if readiness_score >= 75 else (2 if readiness_score >= 45 else 1),
            "matched_skills_count": len(matched_skills),
            "developing_skills_count": len(developing_skills),
            "missing_skills_count": len(missing_skills),
            "readiness_label": readiness_label,
            "readiness_badge": readiness_badge,
            "skill_match_percentage": skill_match_pct,
            "exp_match_percentage": exp_match_pct,
            "current_experience": current_exp,
            "required_experience": req_exp,
            "experience_gap": exp_gap,
            "matched_skills": matched_skills,
            "developing_skills": developing_skills,
            "missing_skills": missing_skills,
            "roadmap": roadmap,
        }

    @staticmethod
    def _build_roadmap(target_pos, missing_skills, developing_skills, exp_gap, score):
        """Constructs an actionable milestone roadmap."""
        milestones = []

        # Step 1: Missing Skills Foundation
        if missing_skills:
            skill_names = ", ".join([s["name"] for s in missing_skills[:3]])
            milestones.append({
                "step": 1,
                "title": f"Competency Acquisition: {skill_names}",
                "timeline": "Months 1 – 2",
                "tag": "Technical Learning",
                "color": "#6366f1",
                "description": f"Complete targeted learning modules, coursework, and initial coding exercises in {skill_names} to establish required baseline knowledge.",
                "action_items": [
                    f"Enroll in recommended training for {s['name']}" for s in missing_skills[:2]
                ] + ["Complete 2 mini-project assessments"],
                "status": "In Progress" if score < 60 else "Completed",
            })

        # Step 2: Proficiency Level-Up
        if developing_skills:
            up_names = ", ".join([s["name"] for s in developing_skills[:3]])
            milestones.append({
                "step": len(milestones) + 1,
                "title": f"Proficiency Elevation: {up_names}",
                "timeline": "Months 3 – 4",
                "tag": "Applied Practice",
                "color": "#3b82f6",
                "description": f"Deepen operational proficiency in {up_names} by taking on real-world assignments and intermediate system responsibilities.",
                "action_items": [
                    f"Pair with a Senior Mentor on tasks involving {s['name']}" for s in developing_skills[:2]
                ] + ["Contribute to peer code reviews and architectural discussions"],
                "status": "Pending",
            })

        # Step 3: High-Complexity Execution & Leadership
        milestones.append({
            "step": len(milestones) + 1,
            "title": f"High-Impact Ownership & Role Simulation",
            "timeline": "Months 5 – 6",
            "tag": "Leadership & Delivery",
            "color": "#10b981",
            "description": f"Lead at least 2 High-complexity tasks aligned with the {target_pos.title} scope, demonstrating independent problem-solving and cross-team communication.",
            "action_items": [
                f"Request assignment to a High-complexity deliverable in {target_pos.department.name}",
                "Document technical delivery architecture and post-mortem metrics",
            ],
            "status": "Pending",
        })

        # Step 4: Promotion Appraisal & Portfolio Review
        milestones.append({
            "step": len(milestones) + 1,
            "title": f"Formal HR Review & Transition to {target_pos.title}",
            "timeline": "Month 6+",
            "tag": "Career Level-Up",
            "color": "#8b5cf6",
            "description": f"Present completed roadmap milestones and verified skill upgrades to HR and department leads for formal promotion consideration to {target_pos.title} ({target_pos.job_level}).",
            "action_items": [
                "Schedule Career Review Discussion with HR Admin",
                "Submit updated competency portfolio and milestone sign-offs",
            ],
            "status": "Target",
        })

        return milestones

