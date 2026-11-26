"""
CareerEquity AI - Comprehensive Demo Data Seeder
Populates realistic departments, teams, 4-level role users, positions,
position requirements, skills, employees, tasks, attendance records,
leave requests, performance reviews, and notifications for a full viva-ready showcase.
"""

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from Alpha.models import (
    AccountProfile,
    Department,
    Team,
    JobPosition,
    PositionRequirement,
    Skill,
    EmployeeProfile,
    EmployeeSkill,
    Task,
    TaskAssignment,
    SalaryRecord,
    AttendanceRecord,
    LeaveRequest,
    PerformanceReview,
    Notification,
)


class Command(BaseCommand):
    help = "Seeds comprehensive realistic demo data for CareerEquity AI 4-Level Showcase"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Seeding CareerEquity AI 4-level enterprise dataset..."))

        with transaction.atomic():
            # =========================================================
            # 1. DEPARTMENTS (8 Comprehensive Enterprise Departments)
            # =========================================================
            dept_specs = [
                ("Engineering", "Software development, platform engineering, and IT architecture.", 8500000),
                ("Data Science & AI", "Machine learning engineering, business intelligence, and AI research.", 7000000),
                ("Product & Design", "Product management, UX research, and UI system design.", 5000000),
                ("Quality Assurance", "Automated regression testing, load testing, and release quality.", 4000000),
                ("Cloud Infrastructure & DevOps", "Cloud architecture, Kubernetes orchestration, SRE, and CI/CD pipelines.", 6500000),
                ("Cybersecurity & IT Compliance", "Information security, threat defense, network security, and compliance.", 5500000),
                ("Human Resources", "Talent acquisition, equity auditing, people operations, and employee growth.", 3500000),
                ("Finance & Operations", "Corporate finance, payroll governance, budget forecasting, and enterprise ops.", 4500000),
            ]
            dept_map = {}
            for name, desc, bud in dept_specs:
                d, _ = Department.objects.update_or_create(
                    name=name,
                    defaults={"description": desc, "budget": Decimal(str(bud))}
                )
                dept_map[name] = d

            # =========================================================
            # 2. JOB POSITIONS (Multi-Tier Positions per Department)
            # =========================================================
            positions_data = [
                # Engineering
                ("Junior Software Engineer", "Engineering", "Entry-Level", 450000, 750000, 1.0),
                ("Software Engineer", "Engineering", "Mid-Level", 750000, 1300000, 2.5),
                ("Senior Software Engineer", "Engineering", "Senior-Level", 1300000, 2200000, 5.0),
                ("Lead Systems Architect", "Engineering", "Principal / Lead", 2200000, 3500000, 8.0),
                ("Frontend Engineer", "Engineering", "Mid-Level", 700000, 1250000, 2.5),
                # Data Science & AI
                ("Associate Data Scientist", "Data Science & AI", "Entry-Level", 550000, 850000, 1.0),
                ("Data Scientist", "Data Science & AI", "Mid-Level", 850000, 1500000, 3.0),
                ("Senior AI Engineer", "Data Science & AI", "Senior-Level", 1500000, 2600000, 6.0),
                ("Machine Learning Specialist", "Data Science & AI", "Senior-Level", 1600000, 2700000, 5.5),
                # Product & Design
                ("Associate UI/UX Designer", "Product & Design", "Entry-Level", 400000, 700000, 1.0),
                ("Product Designer", "Product & Design", "Mid-Level", 700000, 1300000, 3.0),
                ("Lead Product Designer", "Product & Design", "Senior-Level", 1300000, 2200000, 6.0),
                ("UX Researcher", "Product & Design", "Mid-Level", 650000, 1200000, 2.5),
                # Quality Assurance
                ("QA Engineer", "Quality Assurance", "Mid-Level", 500000, 950000, 2.0),
                ("Senior QA Automation Engineer", "Quality Assurance", "Senior-Level", 950000, 1600000, 5.0),
                ("Performance Test Engineer", "Quality Assurance", "Mid-Level", 600000, 1100000, 3.0),
                # Cloud Infrastructure & DevOps
                ("Cloud DevOps Engineer", "Cloud Infrastructure & DevOps", "Mid-Level", 800000, 1450000, 3.0),
                ("Senior Site Reliability Engineer", "Cloud Infrastructure & DevOps", "Senior-Level", 1450000, 2400000, 5.5),
                # Cybersecurity & IT Compliance
                ("Security Analyst", "Cybersecurity & IT Compliance", "Mid-Level", 750000, 1350000, 2.5),
                ("Senior Cybersecurity Engineer", "Cybersecurity & IT Compliance", "Senior-Level", 1400000, 2500000, 6.0),
                # Human Resources
                ("HR Generalist", "Human Resources", "Mid-Level", 500000, 900000, 2.0),
                ("Senior Talent Acquisition Lead", "Human Resources", "Senior-Level", 900000, 1650000, 5.0),
                # Finance & Operations
                ("Financial Analyst", "Finance & Operations", "Mid-Level", 600000, 1150000, 2.5),
                ("Operations & Payroll Lead", "Finance & Operations", "Senior-Level", 1000000, 1850000, 5.5),
            ]
            pos_map = {}
            for title, dname, lvl, min_s, max_s, req_exp in positions_data:
                p, _ = JobPosition.objects.update_or_create(
                    title=title,
                    department=dept_map[dname],
                    defaults={
                        "job_level": lvl,
                        "minimum_salary": Decimal(str(min_s)),
                        "maximum_salary": Decimal(str(max_s)),
                        "required_experience": Decimal(str(req_exp)),
                        "description": f"{lvl} position in {dname}."
                    }
                )
                pos_map[title] = p

            # =========================================================
            # 3. SKILLS & POSITION REQUIREMENTS
            # =========================================================
            skills_list = [
                "Python", "Django", "React.js", "Docker", "PostgreSQL",
                "Machine Learning", "PyTorch", "Data Analysis",
                "Figma", "UI Prototyping", "Design Systems", "User Research",
                "Selenium", "Cypress", "API Testing", "CI/CD",
                "Kubernetes", "AWS Cloud", "Terraform",
                "Network Security", "Penetration Testing", "SOC 2 Compliance",
                "Talent Acquisition", "People Analytics", "Performance Management",
                "Financial Modeling", "Corporate Budgeting", "Payroll Auditing",
                "Agile Project Management", "System Architecture",
            ]
            skill_map = {}
            for sname in skills_list:
                s, _ = Skill.objects.get_or_create(name=sname)
                skill_map[sname] = s

            reqs = [
                ("Junior Software Engineer", [("Python", "Intermediate"), ("Django", "Beginner"), ("PostgreSQL", "Beginner")]),
                ("Software Engineer", [("Python", "Advanced"), ("Django", "Intermediate"), ("PostgreSQL", "Intermediate"), ("React.js", "Beginner")]),
                ("Senior Software Engineer", [("Python", "Expert"), ("Django", "Advanced"), ("Docker", "Advanced"), ("System Architecture", "Advanced")]),
                ("Lead Systems Architect", [("System Architecture", "Expert"), ("Docker", "Expert"), ("CI/CD", "Advanced")]),
                ("Frontend Engineer", [("React.js", "Advanced"), ("UI Prototyping", "Intermediate"), ("Figma", "Intermediate")]),
                ("QA Engineer", [("Selenium", "Intermediate"), ("API Testing", "Intermediate"), ("Python", "Beginner")]),
                ("Senior QA Automation Engineer", [("Selenium", "Expert"), ("Cypress", "Advanced"), ("CI/CD", "Intermediate")]),
                ("Product Designer", [("Figma", "Advanced"), ("UI Prototyping", "Advanced"), ("Design Systems", "Intermediate")]),
                ("UX Researcher", [("User Research", "Advanced"), ("UI Prototyping", "Intermediate"), ("Data Analysis", "Intermediate")]),
                ("Associate UI/UX Designer", [("Figma", "Intermediate"), ("UI Prototyping", "Beginner")]),
                ("Senior AI Engineer", [("Machine Learning", "Expert"), ("PyTorch", "Advanced"), ("Python", "Expert")]),
                ("Data Scientist", [("Data Analysis", "Advanced"), ("Machine Learning", "Intermediate"), ("Python", "Advanced")]),
                ("Machine Learning Specialist", [("Machine Learning", "Expert"), ("PyTorch", "Expert"), ("Data Analysis", "Advanced")]),
                ("Cloud DevOps Engineer", [("AWS Cloud", "Advanced"), ("Docker", "Advanced"), ("CI/CD", "Advanced"), ("Kubernetes", "Intermediate")]),
                ("Senior Site Reliability Engineer", [("Kubernetes", "Expert"), ("AWS Cloud", "Expert"), ("Terraform", "Advanced"), ("System Architecture", "Advanced")]),
                ("Security Analyst", [("Network Security", "Advanced"), ("SOC 2 Compliance", "Intermediate"), ("API Testing", "Intermediate")]),
                ("Senior Cybersecurity Engineer", [("Network Security", "Expert"), ("Penetration Testing", "Expert"), ("SOC 2 Compliance", "Advanced")]),
                ("HR Generalist", [("Talent Acquisition", "Advanced"), ("Performance Management", "Intermediate"), ("People Analytics", "Beginner")]),
                ("Senior Talent Acquisition Lead", [("Talent Acquisition", "Expert"), ("People Analytics", "Advanced"), ("Performance Management", "Advanced")]),
                ("Financial Analyst", [("Financial Modeling", "Advanced"), ("Data Analysis", "Intermediate"), ("Corporate Budgeting", "Intermediate")]),
                ("Operations & Payroll Lead", [("Corporate Budgeting", "Expert"), ("Payroll Auditing", "Expert"), ("Financial Modeling", "Advanced")]),
            ]
            for ptitle, sk_reqs in reqs:
                if ptitle in pos_map:
                    pos = pos_map[ptitle]
                    for sk_name, prof in sk_reqs:
                        if sk_name in skill_map:
                            PositionRequirement.objects.update_or_create(
                                position=pos,
                                skill=skill_map[sk_name],
                                defaults={"required_proficiency": prof}
                            )

            # =========================================================
            # 4. ROLE 1: HR ADMIN USER
            # =========================================================
            hr_user, _ = User.objects.get_or_create(
                username="hr_admin",
                defaults={
                    "first_name": "Eleanor",
                    "last_name": "Vance",
                    "email": "hr.admin@careerequity.ai",
                    "is_staff": True,
                    "is_superuser": True,
                }
            )
            hr_user.set_password("password123")
            hr_user.save()

            AccountProfile.objects.update_or_create(
                user=hr_user,
                defaults={
                    "full_name": "Eleanor Vance",
                    "role": "HR Manager/Admin",
                    "employee_id": "HR-ADM-001",
                    "organization": "CareerEquity Tech Labs",
                    "department": "Human Resources",
                    "designation": "Chief People Officer & Equity Director",
                }
            )

            # =========================================================
            # 5. ROLE 2: DEPARTMENT MANAGER USER (Head of Engineering)
            # =========================================================
            dept_mgr_user, _ = User.objects.get_or_create(
                username="dept_manager",
                defaults={
                    "first_name": "Vikram",
                    "last_name": "Malhotra",
                    "email": "vikram.dept@careerequity.ai",
                    "is_staff": True,
                }
            )
            dept_mgr_user.set_password("password123")
            dept_mgr_user.save()

            AccountProfile.objects.update_or_create(
                user=dept_mgr_user,
                defaults={
                    "full_name": "Dr. Vikram Malhotra",
                    "role": "Department Manager",
                    "employee_id": "DM-ENG-01",
                    "organization": "CareerEquity Tech Labs",
                    "department": "Engineering",
                    "designation": "Head of Engineering",
                }
            )
            dept_map["Engineering"].department_manager = dept_mgr_user
            dept_map["Engineering"].save()

            # =========================================================
            # 6. ROLE 3: TEAM MANAGER USER (Engineering Team Lead)
            # =========================================================
            team_mgr_user, _ = User.objects.get_or_create(
                username="team_manager",
                defaults={
                    "first_name": "Ananya",
                    "last_name": "Roy",
                    "email": "ananya.team@careerequity.ai",
                    "is_staff": False,
                }
            )
            team_mgr_user.set_password("password123")
            team_mgr_user.save()

            AccountProfile.objects.update_or_create(
                user=team_mgr_user,
                defaults={
                    "full_name": "Ananya Roy",
                    "role": "Team Manager",
                    "employee_id": "TM-ENG-02",
                    "organization": "CareerEquity Tech Labs",
                    "department": "Engineering",
                    "designation": "Engineering Team Lead",
                }
            )

            # =========================================================
            # 7. TEAMS UNDER DEPARTMENTS (16 Teams: 2 per department)
            # =========================================================
            teams_data = [
                ("Core Platform Engineering", "Engineering", team_mgr_user, "Full-stack application delivery, microservices, and backend APIs."),
                ("Frontend & Mobile Systems", "Engineering", None, "NextGen React frontends, component libraries, and mobile architectures."),
                ("AI & Analytics", "Data Science & AI", None, "Predictive modeling, machine learning pipelines, and equity analytics."),
                ("NLP & Generative Models", "Data Science & AI", None, "Natural language processing, explainable AI, and semantic search."),
                ("Product Experience & UI", "Product & Design", None, "Enterprise UI architecture, accessibility, and interactive design systems."),
                ("UX Research & Strategy", "Product & Design", None, "User behavior analytics, wireframing, and persona studies."),
                ("QA & Automation", "Quality Assurance", None, "Automated regression testing, integration tests, and performance benchmarks."),
                ("Performance & Security QA", "Quality Assurance", None, "Stress testing, penetration QA, and release certification."),
                ("Cloud Platform & SRE", "Cloud Infrastructure & DevOps", None, "Kubernetes cluster operations, cloud scalability, and 99.99% uptime."),
                ("CI/CD Automation & Release", "Cloud Infrastructure & DevOps", None, "Automated delivery pipelines, infrastructure as code, and deployment."),
                ("Information Security & Defense", "Cybersecurity & IT Compliance", None, "Intrusion prevention, vulnerability mitigation, and perimeter security."),
                ("IT Governance & Audit", "Cybersecurity & IT Compliance", None, "SOC 2, ISO 27001 regulatory compliance, and security policy auditing."),
                ("Talent Acquisition & People Ops", "Human Resources", None, "Strategic technical recruiting, onboarding, and employee lifecycle operations."),
                ("Culture & Equity Auditing", "Human Resources", None, "Workplace compensation parity, DEI compliance, and retention monitoring."),
                ("Corporate Finance & Payroll", "Finance & Operations", None, "Monthly payroll disbursement, tax compliance, and ledger audits."),
                ("Enterprise Strategy & Ops", "Finance & Operations", None, "Resource planning, corporate budgets, and operational efficiency."),
            ]

            team_map = {}
            for tname, dname, mgr, desc in teams_data:
                t, _ = Team.objects.update_or_create(
                    name=tname,
                    department=dept_map[dname],
                    defaults={
                        "team_manager": mgr,
                        "description": desc
                    }
                )
                team_map[tname] = t

            # =========================================================
            # 8. ROLE 4: 19 REALISTIC EMPLOYEES SPLIT ACROSS 8 DEPARTMENTS
            # =========================================================
            employees_spec = [
                # --- DEPARTMENT 1: ENGINEERING ---
                {
                    "username": "alex_dev",
                    "fname": "Alex", "lname": "Mercer",
                    "email": "alex.mercer@careerequity.ai",
                    "emp_id": "EMP-101",
                    "dept": "Engineering",
                    "team": team_map["Core Platform Engineering"],
                    "pos": "Software Engineer",
                    "target_pos": "Senior Software Engineer",
                    "exp": 3.8,
                    "salary": 1150000,
                    "phone": "+91 98450 12345",
                    "skills": [("Python", "Advanced"), ("Django", "Advanced"), ("PostgreSQL", "Intermediate"), ("Docker", "Beginner")],
                    "tasks": [
                        ("Build JWT Token Refresh Service", "High", 28.0, 24.0, date.today() + timedelta(days=5), "In Progress", "Implemented refresh rotation token logic with Redis caching."),
                        ("Optimize Database Queries for Employee Directory", "Medium", 14.0, 14.0, date.today() - timedelta(days=1), "Completed", "Added select_related on position & department relations, reducing queries by 68%."),
                        ("Implement RESTful Attendance Punch API", "Medium", 12.0, 12.0, date.today() - timedelta(days=7), "Completed", "Integrated timestamp validation and geofencing verification."),
                    ]
                },
                {
                    "username": "priya_lead",
                    "fname": "Priya", "lname": "Sharma",
                    "email": "priya.sharma@careerequity.ai",
                    "emp_id": "EMP-102",
                    "dept": "Engineering",
                    "team": team_map["Core Platform Engineering"],
                    "pos": "Senior Software Engineer",
                    "target_pos": "Lead Systems Architect",
                    "exp": 6.2,
                    "salary": 1950000,
                    "phone": "+91 98450 23456",
                    "skills": [("Python", "Expert"), ("Django", "Expert"), ("Docker", "Advanced"), ("System Architecture", "Advanced"), ("CI/CD", "Intermediate")],
                    "tasks": [
                        ("Core Microservices Infrastructure Migration", "High", 45.0, 40.0, date.today() + timedelta(days=8), "In Progress", "Docker containerization completed. Preparing Helm charts."),
                        ("Security Vulnerability Penetration Patching", "High", 22.0, 22.0, date.today() - timedelta(days=3), "Completed", "Patched CVE dependencies and updated Django security headers."),
                    ]
                },
                {
                    "username": "rohan_fe",
                    "fname": "Rohan", "lname": "Das",
                    "email": "rohan.das@careerequity.ai",
                    "emp_id": "EMP-106",
                    "dept": "Engineering",
                    "team": team_map["Frontend & Mobile Systems"],
                    "pos": "Frontend Engineer",
                    "target_pos": "Senior Software Engineer",
                    "exp": 3.2,
                    "salary": 1050000,
                    "phone": "+91 98450 34567",
                    "skills": [("React.js", "Advanced"), ("UI Prototyping", "Intermediate"), ("Figma", "Intermediate"), ("Docker", "Beginner")],
                    "tasks": [
                        ("Responsive Mobile Navigation Framework", "Medium", 18.0, 16.0, date.today() + timedelta(days=6), "In Progress", "Built touch-friendly hamburger sidebar and sticky headers."),
                        ("Dark Mode Theme Engine Integration", "Low", 10.0, 10.0, date.today() - timedelta(days=4), "Completed", "CSS custom property switching based on user system preference."),
                    ]
                },

                # --- DEPARTMENT 2: DATA SCIENCE & AI ---
                {
                    "username": "sneha_data",
                    "fname": "Sneha", "lname": "Nair",
                    "email": "sneha.nair@careerequity.ai",
                    "emp_id": "EMP-104",
                    "dept": "Data Science & AI",
                    "team": team_map["AI & Analytics"],
                    "pos": "Senior AI Engineer",
                    "target_pos": "Machine Learning Specialist",
                    "exp": 6.5,
                    "salary": 2100000,
                    "phone": "+91 98450 45678",
                    "skills": [("Machine Learning", "Expert"), ("PyTorch", "Expert"), ("Python", "Expert"), ("Data Analysis", "Advanced")],
                    "tasks": [
                        ("Train Workload Random Forest Classifier", "High", 30.0, 28.0, date.today() + timedelta(days=4), "In Progress", "Trained on 10,000 historical task allocations with 94.2% accuracy."),
                        ("Build Explainable AI Attribution Engine", "High", 26.0, 26.0, date.today() - timedelta(days=2), "Completed", "Integrated SHAP-style rupee attribution weights."),
                    ]
                },
                {
                    "username": "aryan_ai",
                    "fname": "Aryan", "lname": "Gupta",
                    "email": "aryan.gupta@careerequity.ai",
                    "emp_id": "EMP-107",
                    "dept": "Data Science & AI",
                    "team": team_map["AI & Analytics"],
                    "pos": "Data Scientist",
                    "target_pos": "Senior AI Engineer",
                    "exp": 3.5,
                    "salary": 1250000,
                    "phone": "+91 98450 56789",
                    "skills": [("Data Analysis", "Advanced"), ("Python", "Advanced"), ("Machine Learning", "Intermediate"), ("PostgreSQL", "Intermediate")],
                    "tasks": [
                        ("Departmental Salary Disparity Statistical Audit", "Medium", 20.0, 18.0, date.today() + timedelta(days=7), "In Progress", "Generating distribution curves and Gini coefficient calculations."),
                        ("Workload Burnout Correlation Pipeline", "Medium", 15.0, 15.0, date.today() - timedelta(days=6), "Completed", "Correlated overtime hours with sprint ticket backlogs."),
                    ]
                },
                {
                    "username": "meera_nlp",
                    "fname": "Meera", "lname": "Iyer",
                    "email": "meera.iyer@careerequity.ai",
                    "emp_id": "EMP-108",
                    "dept": "Data Science & AI",
                    "team": team_map["NLP & Generative Models"],
                    "pos": "Machine Learning Specialist",
                    "target_pos": "Lead Systems Architect",
                    "exp": 5.8,
                    "salary": 1850000,
                    "phone": "+91 98450 67890",
                    "skills": [("Machine Learning", "Expert"), ("PyTorch", "Expert"), ("Python", "Expert"), ("Data Analysis", "Advanced")],
                    "tasks": [
                        ("Fine-tune Sentiment Classifier for Employee Feedback", "High", 25.0, 22.0, date.today() + timedelta(days=5), "In Progress", "Achieved 91% F1-score on anonymous pulse survey comments."),
                        ("Semantic Skill Match Vector Index", "Medium", 16.0, 16.0, date.today() - timedelta(days=8), "Completed", "Indexed 200+ technology skills using cosine similarity embeddings."),
                    ]
                },

                # --- DEPARTMENT 3: PRODUCT & DESIGN ---
                {
                    "username": "karan_des",
                    "fname": "Karan", "lname": "Patel",
                    "email": "karan.patel@careerequity.ai",
                    "emp_id": "EMP-105",
                    "dept": "Product & Design",
                    "team": team_map["Product Experience & UI"],
                    "pos": "Product Designer",
                    "target_pos": "Lead Product Designer",
                    "exp": 3.4,
                    "salary": 980000,
                    "phone": "+91 98450 78901",
                    "skills": [("Figma", "Advanced"), ("UI Prototyping", "Advanced"), ("Design Systems", "Intermediate")],
                    "tasks": [
                        ("Design 4-Level Management System UI", "High", 28.0, 26.0, date.today() + timedelta(days=3), "In Progress", "High-fidelity mockups for HR, DM, TM, and Employee portals completed."),
                        ("Accessibility Audit for Contrast Standards", "Medium", 14.0, 14.0, date.today() - timedelta(days=5), "Completed", "Complied with WCAG 2.1 AA specifications."),
                    ]
                },
                {
                    "username": "tanya_ux",
                    "fname": "Tanya", "lname": "Sen",
                    "email": "tanya.sen@careerequity.ai",
                    "emp_id": "EMP-109",
                    "dept": "Product & Design",
                    "team": team_map["UX Research & Strategy"],
                    "pos": "UX Researcher",
                    "target_pos": "Lead Product Designer",
                    "exp": 3.0,
                    "salary": 920000,
                    "phone": "+91 98450 89012",
                    "skills": [("User Research", "Advanced"), ("UI Prototyping", "Intermediate"), ("Data Analysis", "Intermediate")],
                    "tasks": [
                        ("Employee Dashboard Usability Heatmap Study", "Medium", 16.0, 14.0, date.today() + timedelta(days=9), "In Progress", "Interviewed 12 team leads on task completion friction."),
                        ("Departmental Onboarding Journey Wireframes", "Low", 12.0, 12.0, date.today() - timedelta(days=4), "Completed", "Drafted standard 3-step profile completion workflow."),
                    ]
                },
                {
                    "username": "david_ui",
                    "fname": "David", "lname": "Chen",
                    "email": "david.chen@careerequity.ai",
                    "emp_id": "EMP-110",
                    "dept": "Product & Design",
                    "team": team_map["Product Experience & UI"],
                    "pos": "Associate UI/UX Designer",
                    "target_pos": "Product Designer",
                    "exp": 1.5,
                    "salary": 620000,
                    "phone": "+91 98450 90123",
                    "skills": [("Figma", "Intermediate"), ("UI Prototyping", "Intermediate"), ("Design Systems", "Beginner")],
                    "tasks": [
                        ("Icon Library Standardization & SVG Optimization", "Low", 12.0, 10.0, date.today() + timedelta(days=4), "In Progress", "Refactored 120 custom SVG icons with unified 24px grid alignment."),
                        ("Button Component State Variations in Figma", "Low", 8.0, 8.0, date.today() - timedelta(days=3), "Completed", "Generated primary, secondary, outline, and ghost variants."),
                    ]
                },

                # --- DEPARTMENT 4: QUALITY ASSURANCE ---
                {
                    "username": "rahul_qa",
                    "fname": "Rahul", "lname": "Verma",
                    "email": "rahul.verma@careerequity.ai",
                    "emp_id": "EMP-103",
                    "dept": "Quality Assurance",
                    "team": team_map["QA & Automation"],
                    "pos": "QA Engineer",
                    "target_pos": "Senior QA Automation Engineer",
                    "exp": 2.8,
                    "salary": 750000,
                    "phone": "+91 98450 01234",
                    "skills": [("Selenium", "Intermediate"), ("API Testing", "Intermediate"), ("Python", "Beginner"), ("CI/CD", "Beginner")],
                    "tasks": [
                        ("Smoke Test Suite Regression Run", "Medium", 16.0, 16.0, date.today() - timedelta(days=1), "Completed", "All 84 core portal test cases passed with zero critical blockers."),
                        ("Automate End-to-End Leave Approval Flow", "Medium", 20.0, 18.0, date.today() + timedelta(days=4), "In Progress", "Cypress automation for leave application and manager decision."),
                    ]
                },
                {
                    "username": "nisha_test",
                    "fname": "Nisha", "lname": "Reddy",
                    "email": "nisha.reddy@careerequity.ai",
                    "emp_id": "EMP-111",
                    "dept": "Quality Assurance",
                    "team": team_map["Performance & Security QA"],
                    "pos": "Senior QA Automation Engineer",
                    "target_pos": "Lead Systems Architect",
                    "exp": 5.2,
                    "salary": 1350000,
                    "phone": "+91 98450 11223",
                    "skills": [("Selenium", "Expert"), ("Cypress", "Advanced"), ("API Testing", "Advanced"), ("CI/CD", "Intermediate")],
                    "tasks": [
                        ("Load & Stress Testing on Salary Prediction Endpoint", "High", 24.0, 20.0, date.today() + timedelta(days=5), "In Progress", "Simulated 1,500 concurrent HR salary queries with under 120ms latency."),
                        ("Automate Cross-Browser Matrix on Safari & Chrome", "Medium", 14.0, 14.0, date.today() - timedelta(days=5), "Completed", "Resolved WebKit flexbox rendering variance."),
                    ]
                },

                # --- DEPARTMENT 5: CLOUD INFRASTRUCTURE & DEVOPS ---
                {
                    "username": "vikram_devops",
                    "fname": "Vikram", "lname": "Joshi",
                    "email": "vikram.joshi@careerequity.ai",
                    "emp_id": "EMP-112",
                    "dept": "Cloud Infrastructure & DevOps",
                    "team": team_map["CI/CD Automation & Release"],
                    "pos": "Cloud DevOps Engineer",
                    "target_pos": "Senior Site Reliability Engineer",
                    "exp": 3.6,
                    "salary": 1200000,
                    "phone": "+91 98450 22334",
                    "skills": [("AWS Cloud", "Advanced"), ("Docker", "Advanced"), ("CI/CD", "Advanced"), ("Kubernetes", "Intermediate")],
                    "tasks": [
                        ("Automate GitHub Actions Blue-Green Deployments", "High", 26.0, 24.0, date.today() + timedelta(days=6), "In Progress", "Configured zero-downtime rolling update deployment step."),
                        ("Docker Multi-Stage Build Optimization", "Medium", 12.0, 12.0, date.today() - timedelta(days=3), "Completed", "Reduced production web container image from 1.2GB down to 180MB."),
                    ]
                },
                {
                    "username": "sarah_sre",
                    "fname": "Sarah", "lname": "Jenkins",
                    "email": "sarah.jenkins@careerequity.ai",
                    "emp_id": "EMP-113",
                    "dept": "Cloud Infrastructure & DevOps",
                    "team": team_map["Cloud Platform & SRE"],
                    "pos": "Senior Site Reliability Engineer",
                    "target_pos": "Lead Systems Architect",
                    "exp": 6.0,
                    "salary": 1900000,
                    "phone": "+91 98450 33445",
                    "skills": [("Kubernetes", "Expert"), ("AWS Cloud", "Expert"), ("Terraform", "Advanced"), ("System Architecture", "Advanced")],
                    "tasks": [
                        ("Kubernetes Cluster Auto-Scaling & Spot Instance Provisioning", "High", 32.0, 30.0, date.today() + timedelta(days=7), "In Progress", "Configured horizontal pod autoscalers and node pooling."),
                        ("Prometheus & Grafana Enterprise Telemetry Setup", "Medium", 18.0, 18.0, date.today() - timedelta(days=4), "Completed", "Configured latency, CPU, and database connection pool gauges."),
                    ]
                },

                # --- DEPARTMENT 6: CYBERSECURITY & IT COMPLIANCE ---
                {
                    "username": "kabir_sec",
                    "fname": "Kabir", "lname": "Mehta",
                    "email": "kabir.mehta@careerequity.ai",
                    "emp_id": "EMP-114",
                    "dept": "Cybersecurity & IT Compliance",
                    "team": team_map["Information Security & Defense"],
                    "pos": "Senior Cybersecurity Engineer",
                    "target_pos": "Lead Systems Architect",
                    "exp": 6.2,
                    "salary": 1950000,
                    "phone": "+91 98450 44556",
                    "skills": [("Network Security", "Expert"), ("Penetration Testing", "Expert"), ("SOC 2 Compliance", "Advanced"), ("Docker", "Intermediate")],
                    "tasks": [
                        ("Vulnerability Assessment & OWASP Top 10 Audit", "High", 28.0, 25.0, date.today() + timedelta(days=5), "In Progress", "Verified CSRF tokens, strict CSP headers, and SQL injection sanitization."),
                        ("Enterprise SSL/TLS Certificate Auto-Renewal Script", "Medium", 10.0, 10.0, date.today() - timedelta(days=7), "Completed", "Automated Let's Encrypt bot integration with alerting."),
                    ]
                },
                {
                    "username": "ananya_gov",
                    "fname": "Ananya", "lname": "Sengupta",
                    "email": "ananya.sengupta@careerequity.ai",
                    "emp_id": "EMP-115",
                    "dept": "Cybersecurity & IT Compliance",
                    "team": team_map["IT Governance & Audit"],
                    "pos": "Security Analyst",
                    "target_pos": "Senior Cybersecurity Engineer",
                    "exp": 2.9,
                    "salary": 950000,
                    "phone": "+91 98450 55667",
                    "skills": [("SOC 2 Compliance", "Advanced"), ("Network Security", "Intermediate"), ("API Testing", "Intermediate")],
                    "tasks": [
                        ("SOC 2 Type II Evidence Documentation Repository", "Medium", 20.0, 16.0, date.today() + timedelta(days=8), "In Progress", "Collected access log reviews and RBAC permission matrices."),
                        ("Internal Phishing Simulation & Security Awareness Training", "Low", 14.0, 14.0, date.today() - timedelta(days=4), "Completed", "Trained 85 internal staff with 98% pass rate."),
                    ]
                },

                # --- DEPARTMENT 7: HUMAN RESOURCES ---
                {
                    "username": "pooja_hr",
                    "fname": "Pooja", "lname": "Kulkarni",
                    "email": "pooja.kulkarni@careerequity.ai",
                    "emp_id": "EMP-116",
                    "dept": "Human Resources",
                    "team": team_map["Talent Acquisition & People Ops"],
                    "pos": "HR Generalist",
                    "target_pos": "Senior Talent Acquisition Lead",
                    "exp": 3.1,
                    "salary": 780000,
                    "phone": "+91 98450 66778",
                    "skills": [("Talent Acquisition", "Advanced"), ("Performance Management", "Intermediate"), ("People Analytics", "Intermediate")],
                    "tasks": [
                        ("Campus Recruitment Drive Coordination - Tier 1 Tech Institutes", "Medium", 22.0, 18.0, date.today() + timedelta(days=10), "In Progress", "Screened 140 graduate engineering candidate applications."),
                        ("Annual Leave Policy & Health Benefits Documentation", "Low", 12.0, 12.0, date.today() - timedelta(days=6), "Completed", "Published updated 2026 handbook for employee self-service."),
                    ]
                },
                {
                    "username": "arjun_people",
                    "fname": "Arjun", "lname": "Singhania",
                    "email": "arjun.singhania@careerequity.ai",
                    "emp_id": "EMP-117",
                    "dept": "Human Resources",
                    "team": team_map["Culture & Equity Auditing"],
                    "pos": "Senior Talent Acquisition Lead",
                    "target_pos": "HR Generalist",
                    "exp": 5.5,
                    "salary": 1350000,
                    "phone": "+91 98450 77889",
                    "skills": [("Talent Acquisition", "Expert"), ("People Analytics", "Advanced"), ("Performance Management", "Advanced")],
                    "tasks": [
                        ("Quarterly Pay Parity & Promotion Transparency Audit", "High", 25.0, 22.0, date.today() + timedelta(days=4), "In Progress", "Benchmarked compensation against national tech market deciles."),
                        ("Senior Engineering Hiring Pipeline Strategy", "Medium", 15.0, 15.0, date.today() - timedelta(days=3), "Completed", "Filled 4 critical senior backend architect vacancies."),
                    ]
                },

                # --- DEPARTMENT 8: FINANCE & OPERATIONS ---
                {
                    "username": "neha_fin",
                    "fname": "Neha", "lname": "Chawla",
                    "email": "neha.chawla@careerequity.ai",
                    "emp_id": "EMP-118",
                    "dept": "Finance & Operations",
                    "team": team_map["Corporate Finance & Payroll"],
                    "pos": "Financial Analyst",
                    "target_pos": "Operations & Payroll Lead",
                    "exp": 3.0,
                    "salary": 880000,
                    "phone": "+91 98450 88990",
                    "skills": [("Financial Modeling", "Advanced"), ("Corporate Budgeting", "Intermediate"), ("Data Analysis", "Intermediate")],
                    "tasks": [
                        ("Q4 Operating Expenditure Variance Modeling", "Medium", 20.0, 18.0, date.today() + timedelta(days=6), "In Progress", "Audited server hosting vs headcount expense growth."),
                        ("Corporate Travel Reimbursement Reconciliation", "Low", 12.0, 12.0, date.today() - timedelta(days=5), "Completed", "Processed and closed 48 expense claims within 48hr SLA."),
                    ]
                },
                {
                    "username": "sid_ops",
                    "fname": "Siddharth", "lname": "Rao",
                    "email": "siddharth.rao@careerequity.ai",
                    "emp_id": "EMP-119",
                    "dept": "Finance & Operations",
                    "team": team_map["Enterprise Strategy & Ops"],
                    "pos": "Operations & Payroll Lead",
                    "target_pos": "Financial Analyst",
                    "exp": 5.7,
                    "salary": 1480000,
                    "phone": "+91 98450 99001",
                    "skills": [("Corporate Budgeting", "Expert"), ("Payroll Auditing", "Expert"), ("Financial Modeling", "Advanced")],
                    "tasks": [
                        ("Enterprise Fiscal Year 2027 Budget Allocation Framework", "High", 30.0, 26.0, date.today() + timedelta(days=7), "In Progress", "Balanced ₹42M capital expenditures across all 8 functional departments."),
                        ("Automated Monthly Salary Disbursement Run", "High", 18.0, 18.0, date.today() - timedelta(days=2), "Completed", "Verified gross-to-net calculations, tax withholdings, and EPF filings."),
                    ]
                },
            ]

            today = date.today()

            for ed in employees_spec:
                user, _ = User.objects.get_or_create(
                    username=ed["username"],
                    defaults={
                        "first_name": ed["fname"],
                        "last_name": ed["lname"],
                        "email": ed["email"],
                    }
                )
                user.set_password("password123")
                user.save()

                AccountProfile.objects.update_or_create(
                    user=user,
                    defaults={
                        "full_name": f"{ed['fname']} {ed['lname']}",
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
                        "team": ed["team"],
                        "position": pos_map[ed["pos"]],
                        "target_position": pos_map.get(ed["target_pos"]),
                        "experience_years": Decimal(str(ed["exp"])),
                        "joining_date": today - timedelta(days=int(ed["exp"] * 365)),
                        "phone": ed["phone"],
                        "employment_status": "Active",
                    }
                )

                # Skills
                for sk_name, prof in ed["skills"]:
                    if sk_name in skill_map:
                        EmployeeSkill.objects.update_or_create(
                            employee=emp,
                            skill=skill_map[sk_name],
                            defaults={"proficiency": prof}
                        )

                # Tasks & Assignments
                for title, comp, est_h, act_h, dline, stat, notes in ed["tasks"]:
                    task, _ = Task.objects.update_or_create(
                        title=title,
                        defaults={
                            "description": f"{comp} priority deliverable for {ed['dept']}.",
                            "complexity": comp,
                            "estimated_hours": Decimal(str(est_h)),
                            "deadline": dline
                        }
                    )
                    TaskAssignment.objects.update_or_create(
                        employee=emp,
                        task=task,
                        defaults={
                            "actual_hours": Decimal(str(act_h)),
                            "status": stat,
                            "completion_notes": notes,
                            "submitted_at": timezone.now() if stat == "Completed" else None
                        }
                    )

                # Salary Record
                SalaryRecord.objects.get_or_create(
                    employee=emp,
                    salary_amount=Decimal(str(ed["salary"])),
                    effective_date=today - timedelta(days=120)
                )

                # Attendance Records (Past 10 days)
                for day_offset in range(10, -1, -1):
                    rec_date = today - timedelta(days=day_offset)
                    # Skip weekends
                    if rec_date.weekday() in (5, 6):
                        continue

                    if day_offset == 0:
                        AttendanceRecord.objects.update_or_create(
                            employee=emp,
                            date=rec_date,
                            defaults={
                                "check_in": time(9, 15),
                                "check_out": time(18, 0) if ed["username"] != "alex_dev" else None,
                                "status": "Present",
                                "working_hours": Decimal("8.75") if ed["username"] != "alex_dev" else Decimal("0.0"),
                                "notes": "On-time biometric punch."
                            }
                        )
                    else:
                        AttendanceRecord.objects.update_or_create(
                            employee=emp,
                            date=rec_date,
                            defaults={
                                "check_in": time(9, 10),
                                "check_out": time(18, 15),
                                "status": "Present",
                                "working_hours": Decimal("9.08"),
                                "notes": "Regular working shift logged."
                            }
                        )

                # Performance Review
                rating_val = Decimal("4.7") if ed["exp"] > 5 else Decimal("4.4")
                PerformanceReview.objects.update_or_create(
                    employee=emp,
                    reviewer=team_mgr_user if ed["dept"] == "Engineering" else dept_mgr_user,
                    review_period="Q3 2026",
                    defaults={
                        "rating": rating_val,
                        "feedback": f"{ed['fname']} shows consistent commitment and high standard of execution in {ed['dept']}. Great team player with strong technical ownership."
                    }
                )

                # Historical Approved Leave
                LeaveRequest.objects.get_or_create(
                    employee=emp,
                    leave_type="Casual Leave",
                    start_date=today - timedelta(days=25),
                    end_date=today - timedelta(days=24),
                    defaults={
                        "days_count": 2,
                        "reason": "Personal work and family function.",
                        "status": "Approved",
                        "reviewed_by": team_mgr_user,
                        "review_comments": "Approved. Team coverage confirmed.",
                        "reviewed_at": timezone.now() - timedelta(days=26)
                    }
                )

                # Live pending leave for Alex Mercer (for live demo approval)
                if ed["username"] == "alex_dev":
                    LeaveRequest.objects.get_or_create(
                        employee=emp,
                        leave_type="Earned Leave",
                        start_date=today + timedelta(days=4),
                        end_date=today + timedelta(days=5),
                        defaults={
                            "days_count": 2,
                            "reason": "Personal vacation and recharge after Sprint release.",
                            "status": "Pending",
                            "review_comments": ""
                        }
                    )

                # In-App Notifications
                Notification.objects.get_or_create(
                    user=user,
                    title="Sprint Task Assigned",
                    defaults={
                        "message": f"You have been assigned a new high-priority deliverable for {ed['dept']}.",
                        "category": "Task",
                        "is_read": False
                    }
                )
                Notification.objects.get_or_create(
                    user=user,
                    title="Company All-Hands Meeting",
                    defaults={
                        "message": "Quarterly Townhall & Innovation Awards are scheduled for Friday at 4:30 PM.",
                        "category": "Announcement",
                        "is_read": True
                    }
                )
                Notification.objects.get_or_create(
                    user=user,
                    title="Q3 Performance Review Published",
                    defaults={
                        "message": "Your manager has submitted your Q3 2026 performance evaluation and feedback.",
                        "category": "Performance",
                        "is_read": False
                    }
                )

            # Notifications for Team Manager
            Notification.objects.get_or_create(
                user=team_mgr_user,
                title="Pending Leave Request from Alex Mercer",
                defaults={
                    "message": "Alex Mercer has submitted an Earned Leave request (2 days) awaiting your review.",
                    "category": "Leave",
                    "is_read": False
                }
            )

        self.stdout.write(self.style.SUCCESS("[OK] CareerEquity AI enterprise database seeded successfully!"))
        self.stdout.write(self.style.SUCCESS(f"Seeded 8 Departments, 16 Teams, and {len(employees_spec)} Employees across all departments."))
        self.stdout.write(self.style.SUCCESS("All users password: password123"))
