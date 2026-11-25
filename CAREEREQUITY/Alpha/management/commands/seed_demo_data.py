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
            # 1. DEPARTMENTS
            # =========================================================
            dept_specs = [
                ("Engineering", "Software development, platform engineering, and IT architecture.", 7500000),
                ("Data Science & AI", "Machine learning engineering, business intelligence, and AI research.", 6000000),
                ("Product & Design", "Product management, UX research, and UI system design.", 4500000),
                ("Quality Assurance", "Automated regression testing, load testing, and release quality.", 3500000),
                ("Human Resources", "Talent acquisition, equity auditing, and organizational development.", 3000000),
                ("Finance & Operations", "Corporate payroll, compliance, and enterprise budgeting.", 4000000),
            ]
            dept_map = {}
            for name, desc, bud in dept_specs:
                d, _ = Department.objects.update_or_create(
                    name=name,
                    defaults={"description": desc, "budget": Decimal(str(bud))}
                )
                dept_map[name] = d

            # =========================================================
            # 2. JOB POSITIONS
            # =========================================================
            positions_data = [
                ("Junior Software Engineer", "Engineering", "Entry-Level", 450000, 750000, 1.0),
                ("Software Engineer", "Engineering", "Mid-Level", 750000, 1300000, 2.5),
                ("Senior Software Engineer", "Engineering", "Senior-Level", 1300000, 2200000, 5.0),
                ("Lead Systems Architect", "Engineering", "Principal / Lead", 2200000, 3500000, 8.0),
                ("Associate Data Scientist", "Data Science & AI", "Entry-Level", 550000, 850000, 1.0),
                ("Data Scientist", "Data Science & AI", "Mid-Level", 850000, 1500000, 3.0),
                ("Senior AI Engineer", "Data Science & AI", "Senior-Level", 1500000, 2600000, 6.0),
                ("Associate UI/UX Designer", "Product & Design", "Entry-Level", 400000, 700000, 1.0),
                ("Product Designer", "Product & Design", "Mid-Level", 700000, 1300000, 3.0),
                ("Lead Product Designer", "Product & Design", "Senior-Level", 1300000, 2200000, 6.0),
                ("QA Engineer", "Quality Assurance", "Mid-Level", 500000, 950000, 2.0),
                ("Senior QA Automation Engineer", "Quality Assurance", "Senior-Level", 950000, 1600000, 5.0),
                ("HR Specialist", "Human Resources", "Mid-Level", 500000, 900000, 2.0),
                ("Senior HR Manager", "Human Resources", "Senior-Level", 900000, 1800000, 6.0),
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
                "Figma", "UI Prototyping", "Design Systems",
                "Selenium", "Cypress", "API Testing", "CI/CD",
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
                ("QA Engineer", [("Selenium", "Intermediate"), ("API Testing", "Intermediate"), ("Python", "Beginner")]),
                ("Product Designer", [("Figma", "Advanced"), ("UI Prototyping", "Advanced"), ("Design Systems", "Intermediate")]),
                ("Senior AI Engineer", [("Machine Learning", "Expert"), ("PyTorch", "Advanced"), ("Python", "Expert")]),
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
                    "employee_id": "HR-001",
                    "organization": "CareerEquity Tech Labs",
                    "department": "Human Resources",
                    "designation": "Director of People & Equity",
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
            # 7. TEAMS UNDER DEPARTMENTS
            # =========================================================
            team_core, _ = Team.objects.update_or_create(
                name="Core Platform Engineering",
                department=dept_map["Engineering"],
                defaults={
                    "team_manager": team_mgr_user,
                    "description": "Full-stack application delivery, microservices, and backend APIs."
                }
            )
            team_qa, _ = Team.objects.update_or_create(
                name="QA & Automation",
                department=dept_map["Quality Assurance"],
                defaults={
                    "description": "Automated end-to-end testing, integration tests, and performance benchmarks."
                }
            )
            team_ai, _ = Team.objects.update_or_create(
                name="AI & Analytics",
                department=dept_map["Data Science & AI"],
                defaults={
                    "description": "Predictive modeling, machine learning pipelines, and equity analytics."
                }
            )
            team_design, _ = Team.objects.update_or_create(
                name="Product Experience & UI",
                department=dept_map["Product & Design"],
                defaults={
                    "description": "Enterprise UI architecture, accessibility, and interactive design systems."
                }
            )

            # =========================================================
            # 8. ROLE 4: EMPLOYEES & ASSOCIATED DATA
            # =========================================================
            employees_spec = [
                {
                    "username": "alex_dev",
                    "fname": "Alex", "lname": "Mercer",
                    "email": "alex.mercer@careerequity.ai",
                    "emp_id": "EMP-101",
                    "dept": "Engineering",
                    "team": team_core,
                    "pos": "Software Engineer",
                    "target_pos": "Senior Software Engineer",
                    "exp": 3.8,
                    "salary": 1150000,
                    "phone": "+91 98450 12345",
                    "skills": [("Python", "Advanced"), ("Django", "Advanced"), ("PostgreSQL", "Intermediate"), ("Docker", "Beginner")],
                    "tasks": [
                        ("Build JWT Token Refresh Service", "High", 28.0, 24.0, date.today() + timedelta(days=5), "In Progress", "Implemented redis token blacklist and refresh rotation."),
                        ("Optimize Database Connection Pooling", "Medium", 14.0, 14.0, date.today() - timedelta(days=2), "Completed", "Applied pgbouncer configuration, query latency reduced by 34%."),
                        ("Migrate Auth Middleware to Async", "High", 22.0, 10.0, date.today() + timedelta(days=9), "Pending", ""),
                    ]
                },
                {
                    "username": "priya_lead",
                    "fname": "Priya", "lname": "Sharma",
                    "email": "priya.sharma@careerequity.ai",
                    "emp_id": "EMP-102",
                    "dept": "Engineering",
                    "team": team_core,
                    "pos": "Senior Software Engineer",
                    "target_pos": "Lead Systems Architect",
                    "exp": 6.5,
                    "salary": 1850000,
                    "phone": "+91 98450 67890",
                    "skills": [("Python", "Expert"), ("Django", "Advanced"), ("Docker", "Advanced"), ("System Architecture", "Advanced"), ("CI/CD", "Intermediate")],
                    "tasks": [
                        ("Enterprise SSO SAML Integration", "High", 36.0, 32.0, date.today() + timedelta(days=2), "In Progress", "Connected Okta IdP endpoints."),
                        ("Design Microservices Event Bus", "High", 40.0, 38.0, date.today() - timedelta(days=1), "In Progress", "Drafted Kafka topic schema registry."),
                        ("Multi-region Database Replication", "High", 32.0, 20.0, date.today() + timedelta(days=6), "In Progress", ""),
                        ("Audit Production Security Vulnerabilities", "Medium", 18.0, 18.0, date.today() - timedelta(days=4), "Completed", "Remediated 4 high severity npm advisories."),
                    ]
                },
                {
                    "username": "rahul_qa",
                    "fname": "Rahul", "lname": "Verma",
                    "email": "rahul.verma@careerequity.ai",
                    "emp_id": "EMP-103",
                    "dept": "Quality Assurance",
                    "team": team_qa,
                    "pos": "QA Engineer",
                    "target_pos": "Senior QA Automation Engineer",
                    "exp": 2.2,
                    "salary": 680000,
                    "phone": "+91 98450 33445",
                    "skills": [("Selenium", "Intermediate"), ("API Testing", "Intermediate"), ("Python", "Beginner")],
                    "tasks": [
                        ("Run End-to-End Regression Suite", "Medium", 16.0, 16.0, date.today() - timedelta(days=3), "Completed", "All 182 test scenarios executed cleanly."),
                        ("Automate Role Access Perm Testing", "Low", 10.0, 6.0, date.today() + timedelta(days=8), "Pending", ""),
                    ]
                },
                {
                    "username": "sneha_data",
                    "fname": "Sneha", "lname": "Nair",
                    "email": "sneha.nair@careerequity.ai",
                    "emp_id": "EMP-104",
                    "dept": "Data Science & AI",
                    "team": team_ai,
                    "pos": "Senior AI Engineer",
                    "target_pos": None,
                    "exp": 6.8,
                    "salary": 1650000,
                    "phone": "+91 98450 55667",
                    "skills": [("Python", "Expert"), ("Machine Learning", "Expert"), ("PyTorch", "Advanced"), ("Data Analysis", "Advanced")],
                    "tasks": [
                        ("Train Workload Random Forest Classifier", "High", 30.0, 28.0, date.today() + timedelta(days=4), "In Progress", "Trained on 10,000 historical task allocations with 94.2% accuracy."),
                        ("Build Explainable AI Attribution Engine", "High", 26.0, 26.0, date.today() - timedelta(days=2), "Completed", "Integrated SHAP-style rupee attribution weights."),
                    ]
                },
                {
                    "username": "karan_des",
                    "fname": "Karan", "lname": "Patel",
                    "email": "karan.patel@careerequity.ai",
                    "emp_id": "EMP-105",
                    "dept": "Product & Design",
                    "team": team_design,
                    "pos": "Product Designer",
                    "target_pos": "Lead Product Designer",
                    "exp": 3.4,
                    "salary": 980000,
                    "phone": "+91 98450 77889",
                    "skills": [("Figma", "Advanced"), ("UI Prototyping", "Advanced"), ("Design Systems", "Intermediate")],
                    "tasks": [
                        ("Design 4-Level Management System UI", "High", 28.0, 26.0, date.today() + timedelta(days=3), "In Progress", "High-fidelity mockups for HR, DM, TM, and Employee portals completed."),
                        ("Accessibility Audit for Contrast Standards", "Medium", 14.0, 14.0, date.today() - timedelta(days=5), "Completed", "Complied with WCAG 2.1 AA specifications."),
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

                # =====================================================
                # 9. ATTENDANCE RECORDS (Past 10 days)
                # =====================================================
                for day_offset in range(10, -1, -1):
                    rec_date = today - timedelta(days=day_offset)
                    # Skip weekends
                    if rec_date.weekday() in (5, 6):
                        continue

                    # If today
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

                # =====================================================
                # 10. PERFORMANCE REVIEWS & FEEDBACK
                # =====================================================
                if ed["username"] == "alex_dev":
                    PerformanceReview.objects.update_or_create(
                        employee=emp,
                        reviewer=team_mgr_user,
                        review_period="Q3 2026",
                        defaults={
                            "rating": Decimal("4.7"),
                            "feedback": "Alex displays tremendous ownership in backend engineering. Highly collaborative, writes robust test-driven code, and proactively refactored database pooling with zero downtime."
                        }
                    )
                elif ed["username"] == "priya_lead":
                    PerformanceReview.objects.update_or_create(
                        employee=emp,
                        reviewer=team_mgr_user,
                        review_period="Q3 2026",
                        defaults={
                            "rating": Decimal("4.9"),
                            "feedback": "Priya is an exceptional senior technical lead. Manages complex architectural deliverables and mentors junior teammates effectively. Keep an eye on workload to prevent fatigue."
                        }
                    )
                elif ed["username"] == "rahul_qa":
                    PerformanceReview.objects.update_or_create(
                        employee=emp,
                        reviewer=dept_mgr_user,
                        review_period="Q3 2026",
                        defaults={
                            "rating": Decimal("4.3"),
                            "feedback": "Consistent accuracy in regression testing. Ready to take on advanced automation framework development."
                        }
                    )

                # =====================================================
                # 11. LEAVE REQUESTS
                # =====================================================
                # Historical approved leave
                LeaveRequest.objects.get_or_create(
                    employee=emp,
                    leave_type="Casual Leave",
                    start_date=today - timedelta(days=25),
                    end_date=today - timedelta(days=24),
                    defaults={
                        "days_count": 2,
                        "reason": "Family function and travel.",
                        "status": "Approved",
                        "reviewed_by": team_mgr_user,
                        "review_comments": "Approved. Team coverage confirmed.",
                        "reviewed_at": timezone.now() - timedelta(days=26)
                    }
                )

                # Live pending leave for Alex Mercer (so Team Manager can demonstrate live approval!)
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

                # =====================================================
                # 12. NOTIFICATIONS
                # =====================================================
                Notification.objects.get_or_create(
                    user=user,
                    title="Sprint Task Assigned",
                    defaults={
                        "message": "You have been assigned a new high-priority deliverable by Ananya Roy (Team Manager).",
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

        self.stdout.write(self.style.SUCCESS("[OK] CareerEquity AI 4-level enterprise database seeded successfully!"))
        self.stdout.write(self.style.SUCCESS("=== READY-TO-DEMO CREDENTIALS (password: password123) ==="))
        self.stdout.write("  [1] HR Admin:           hr_admin")
        self.stdout.write("  [2] Department Manager: dept_manager  (Engineering)")
        self.stdout.write("  [3] Team Manager:       team_manager  (Engineering Team Lead)")
        self.stdout.write("  [4] Employee:           alex_dev      (Full-Stack Developer, 9 Modules Active)")
