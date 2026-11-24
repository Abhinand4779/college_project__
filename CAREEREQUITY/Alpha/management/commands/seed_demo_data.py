"""
CareerEquity AI - Comprehensive Demo Data Seeder
Populates realistic departments, positions, position requirements, skills,
employees, tasks, and salary records to provide a full viva-ready showcase.
"""

from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

from Alpha.models import (
    AccountProfile,
    Department,
    JobPosition,
    PositionRequirement,
    Skill,
    EmployeeProfile,
    EmployeeSkill,
    Task,
    TaskAssignment,
    SalaryRecord,
)


class Command(BaseCommand):
    help = "Seeds comprehensive realistic demo data for CareerEquity AI showcase"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Seeding CareerEquity AI demo dataset..."))

        with transaction.atomic():
            # 1. HR Manager User
            hr_user, _ = User.objects.get_or_create(
                username="hr_admin",
                defaults={
                    "first_name": "Eleanor",
                    "last_name": "Vance",
                    "email": "hr@careerequity.ai",
                    "is_staff": True,
                }
            )
            hr_user.set_password("password123")
            hr_user.save()

            AccountProfile.objects.update_or_create(
                user=hr_user,
                defaults={
                    "full_name": "Eleanor Vance",
                    "role": "HR Manager/Admin",
                    "employee_id": "HR001",
                    "organization": "CareerEquity Tech Labs",
                    "department": "Human Resources",
                    "designation": "Head of People & Culture",
                }
            )

            # 2. Departments
            depts_data = [
                ("Engineering", "Software development, architecture, infrastructure and cloud platforms."),
                ("Data Science & AI", "Predictive modeling, machine learning, data engineering and analytics."),
                ("Product & Design", "User experience research, UI architecture, product design and workflows."),
                ("Quality Assurance", "Automated testing, continuous integration, performance and QA."),
                ("Human Resources", "Talent acquisition, compensation management, and people analytics."),
                ("Finance & Operations", "Financial planning, operations strategy and business management."),
            ]

            dept_map = {}
            for name, desc in depts_data:
                d, _ = Department.objects.get_or_create(name=name, defaults={"description": desc})
                dept_map[name] = d

            # 3. Job Positions & Salary Bands
            positions_data = [
                ("Junior Software Engineer", "Engineering", "Junior", 450000, 750000, 1.0),
                ("Senior Software Engineer", "Engineering", "Senior", 1000000, 1700000, 4.0),
                ("Lead Systems Architect", "Engineering", "Lead", 1900000, 3000000, 7.0),
                ("Junior Data Analyst", "Data Science & AI", "Junior", 400000, 700000, 1.0),
                ("Senior Data Scientist", "Data Science & AI", "Senior", 1100000, 1850000, 4.5),
                ("Lead AI Researcher", "Data Science & AI", "Lead", 2000000, 3200000, 7.0),
                ("Associate UI/UX Designer", "Product & Design", "Junior", 420000, 720000, 1.0),
                ("Senior Product Designer", "Product & Design", "Senior", 950000, 1600000, 4.0),
                ("QA Automation Engineer", "Quality Assurance", "Mid-Level", 600000, 1050000, 2.5),
                ("Senior QA Architect", "Quality Assurance", "Senior", 1000000, 1650000, 5.0),
            ]

            pos_map = {}
            for title, dept_name, level, min_sal, max_sal, req_exp in positions_data:
                pos, _ = JobPosition.objects.get_or_create(
                    title=title,
                    department=dept_map[dept_name],
                    defaults={
                        "job_level": level,
                        "minimum_salary": Decimal(str(min_sal)),
                        "maximum_salary": Decimal(str(max_sal)),
                        "required_experience": Decimal(str(req_exp)),
                        "description": f"{title} within the {dept_name} organization.",
                    }
                )
                pos_map[title] = pos

            # 4. Skills
            skills_list = [
                "Python", "Django", "JavaScript", "React", "SQL & Database Design",
                "Machine Learning", "Scikit-Learn", "Docker & Kubernetes", "PyTest & Automated Testing",
                "Figma & UI Prototyping", "Data Analysis & Pandas", "Cloud Architecture (AWS/GCP)",
                "System Design", "Agile Leadership", "Git & CI/CD"
            ]

            skill_map = {}
            for sname in skills_list:
                sk, _ = Skill.objects.get_or_create(name=sname)
                skill_map[sname] = sk

            # 5. Position Requirements (Competency mappings)
            req_data = [
                ("Senior Software Engineer", [
                    ("Python", "Advanced"),
                    ("Django", "Advanced"),
                    ("SQL & Database Design", "Advanced"),
                    ("Docker & Kubernetes", "Intermediate"),
                    ("System Design", "Intermediate"),
                ]),
                ("Senior Data Scientist", [
                    ("Python", "Expert"),
                    ("Machine Learning", "Advanced"),
                    ("Scikit-Learn", "Advanced"),
                    ("Data Analysis & Pandas", "Expert"),
                    ("SQL & Database Design", "Advanced"),
                ]),
                ("Senior Product Designer", [
                    ("Figma & UI Prototyping", "Expert"),
                    ("JavaScript", "Intermediate"),
                    ("Agile Leadership", "Intermediate"),
                ]),
                ("QA Automation Engineer", [
                    ("Python", "Intermediate"),
                    ("PyTest & Automated Testing", "Advanced"),
                    ("Git & CI/CD", "Intermediate"),
                ]),
            ]

            for pos_title, reqs in req_data:
                pos_obj = pos_map[pos_title]
                for sk_name, prof in reqs:
                    PositionRequirement.objects.get_or_create(
                        position=pos_obj,
                        skill=skill_map[sk_name],
                        defaults={"required_proficiency": prof}
                    )

            # 6. Employees Showcase
            today = date.today()
            employees_data = [
                {
                    "username": "alex_dev",
                    "name": "Alex Mercer",
                    "email": "alex@careerequity.ai",
                    "emp_id": "EMP101",
                    "dept": "Engineering",
                    "pos": "Junior Software Engineer",
                    "target_pos": "Senior Software Engineer",
                    "exp": 2.2,
                    "salary": 620000,
                    "skills": [("Python", "Advanced"), ("Django", "Intermediate"), ("SQL & Database Design", "Intermediate"), ("Git & CI/CD", "Intermediate")],
                    "tasks": [
                        ("Develop Authentication Microservice", "High", 28, 24, today + timedelta(days=5), "In Progress"),
                        ("Database Index Tuning", "Medium", 14, 12, today + timedelta(days=9), "In Progress"),
                        ("Unit Testing User APIs", "Low", 8, 8, today - timedelta(days=4), "Completed"),
                    ]
                },
                {
                    "username": "priya_lead",
                    "name": "Priya Sharma",
                    "email": "priya@careerequity.ai",
                    "emp_id": "EMP102",
                    "dept": "Engineering",
                    "pos": "Senior Software Engineer",
                    "target_pos": "Lead Systems Architect",
                    "exp": 5.5,
                    "salary": 1450000,
                    "skills": [("Python", "Expert"), ("Django", "Expert"), ("SQL & Database Design", "Advanced"), ("Docker & Kubernetes", "Advanced"), ("System Design", "Advanced"), ("Git & CI/CD", "Advanced")],
                    # Overloaded / Burnout profile: multiple High complexity tasks + overdue
                    "tasks": [
                        ("High-Throughput Payment Engine Migration", "High", 48, 55, today - timedelta(days=2), "In Progress"),
                        ("Core Microservices Infrastructure Redesign", "High", 36, 40, today + timedelta(days=3), "In Progress"),
                        ("Security Vulnerability Penetration Patching", "High", 26, 20, today + timedelta(days=4), "Pending"),
                        ("Legacy Database Sharding Phase 2", "High", 32, 10, today + timedelta(days=8), "Pending"),
                    ]
                },
                {
                    "username": "rahul_qa",
                    "name": "Rahul Verma",
                    "email": "rahul@careerequity.ai",
                    "emp_id": "EMP103",
                    "dept": "Quality Assurance",
                    "pos": "QA Automation Engineer",
                    "target_pos": "Senior QA Architect",
                    "exp": 2.8,
                    "salary": 780000,
                    "skills": [("Python", "Intermediate"), ("PyTest & Automated Testing", "Advanced"), ("Git & CI/CD", "Intermediate")],
                    # Underutilized: Low task load, capacity available for rebalancing
                    "tasks": [
                        ("Smoke Test Suite Regression Run", "Low", 10, 8, today + timedelta(days=7), "In Progress"),
                    ]
                },
                {
                    "username": "sneha_data",
                    "name": "Sneha Nair",
                    "email": "sneha@careerequity.ai",
                    "emp_id": "EMP104",
                    "dept": "Data Science & AI",
                    "pos": "Junior Data Analyst",
                    "target_pos": "Senior Data Scientist",
                    "exp": 2.0,
                    # Underpaid disparity case: only ₹4,20,000 despite high skills
                    "salary": 420000,
                    "skills": [("Python", "Advanced"), ("Data Analysis & Pandas", "Advanced"), ("Machine Learning", "Intermediate"), ("SQL & Database Design", "Advanced")],
                    "tasks": [
                        ("Customer Retention ML Feature Engineering", "Medium", 20, 18, today + timedelta(days=6), "In Progress"),
                        ("Weekly Churn Analytics Dashboard", "Low", 12, 12, today - timedelta(days=2), "Completed"),
                    ]
                },
                {
                    "username": "karan_des",
                    "name": "Karan Patel",
                    "email": "karan@careerequity.ai",
                    "emp_id": "EMP105",
                    "dept": "Product & Design",
                    "pos": "Associate UI/UX Designer",
                    "target_pos": "Senior Product Designer",
                    "exp": 1.8,
                    "salary": 580000,
                    "skills": [("Figma & UI Prototyping", "Advanced"), ("JavaScript", "Beginner")],
                    "tasks": [
                        ("Mobile Onboarding User Experience Flow", "Medium", 18, 15, today + timedelta(days=5), "In Progress"),
                        ("Design System Color & Typography Tokens", "Low", 10, 10, today - timedelta(days=3), "Completed"),
                    ]
                },
            ]

            for ed in employees_data:
                user, _ = User.objects.get_or_create(
                    username=ed["username"],
                    defaults={
                        "first_name": ed["name"].split()[0],
                        "last_name": ed["name"].split()[1] if len(ed["name"].split()) > 1 else "",
                        "email": ed["email"],
                    }
                )
                user.set_password("password123")
                user.save()

                AccountProfile.objects.update_or_create(
                    user=user,
                    defaults={
                        "full_name": ed["name"],
                        "role": "Employee",
                        "employee_id": ed["emp_id"],
                        "organization": "CareerEquity Tech Labs",
                        "department": ed["dept"],
                        "designation": ed["pos"],
                    }
                )

                emp, _ = EmployeeProfile.objects.update_or_create(
                    user=user,
                    defaults={
                        "employee_id": ed["emp_id"],
                        "department": dept_map[ed["dept"]],
                        "position": pos_map[ed["pos"]],
                        "target_position": pos_map.get(ed["target_pos"]),
                        "experience_years": Decimal(str(ed["exp"])),
                        "joining_date": today - timedelta(days=int(ed["exp"] * 365)),
                        "employment_status": "Active",
                    }
                )

                # Skills
                for sk_name, prof in ed["skills"]:
                    EmployeeSkill.objects.update_or_create(
                        employee=emp,
                        skill=skill_map[sk_name],
                        defaults={"proficiency": prof}
                    )

                # Tasks
                for title, comp, est_h, act_h, dline, stat in ed["tasks"]:
                    task = Task.objects.create(
                        title=title,
                        description=f"{comp} priority deliverable for {ed['dept']}.",
                        complexity=comp,
                        estimated_hours=Decimal(str(est_h)),
                        deadline=dline
                    )
                    TaskAssignment.objects.create(
                        employee=emp,
                        task=task,
                        actual_hours=Decimal(str(act_h)),
                        status=stat
                    )

                # Salary Record
                SalaryRecord.objects.get_or_create(
                    employee=emp,
                    salary_amount=Decimal(str(ed["salary"])),
                    effective_date=today - timedelta(days=120)
                )

        self.stdout.write(self.style.SUCCESS("[OK] CareerEquity AI demo database populated successfully!"))
        self.stdout.write(self.style.SUCCESS("HR Admin: hr_admin / password123"))
        self.stdout.write(self.style.SUCCESS("Sample Employees (password123 for all):"))
        self.stdout.write("  - alex_dev (Balanced, aiming for promotion)")
        self.stdout.write("  - priya_lead (Overloaded / Burnout risk alert)")
        self.stdout.write("  - rahul_qa (Underutilized / capacity available)")
        self.stdout.write("  - sneha_data (Pay disparity review case)")
        self.stdout.write("  - karan_des (Product Designer)")

