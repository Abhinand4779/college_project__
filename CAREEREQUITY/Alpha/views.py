
from datetime import datetime
from decimal import Decimal, InvalidOperation
from functools import wraps

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.utils import timezone

from .models import (
    AccountProfile,
    EmployeeProfile,
    Department,
    Team,
    JobPosition,
    Skill,
    EmployeeSkill,
    SalaryRecord,
    Task,
    TaskAssignment,
    PositionRequirement,
    AttendanceRecord,
    LeaveRequest,
    PerformanceReview,
    Notification,
)
from .ml_engine.workload_model import WorkloadAnalyzer
from .ml_engine.salary_model import SalaryEquityPredictor
from .ml_engine.career_engine import CareerProgressionAdvisor


# =========================================================
# HELPER FUNCTIONS AND DECORATORS
# =========================================================

def is_hr_user(user):
    return AccountProfile.objects.filter(
        user=user,
        role="HR Manager/Admin"
    ).exists()


def is_department_manager(user):
    return AccountProfile.objects.filter(
        user=user,
        role__in=["Department Manager", "HR Manager/Admin"]
    ).exists()


def is_team_manager(user):
    return AccountProfile.objects.filter(
        user=user,
        role__in=["Team Manager", "Department Manager", "HR Manager/Admin"]
    ).exists()


def team_manager_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not is_team_manager(request.user):
            messages.error(request, "Access restricted to Team Managers and above.")
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper


def department_manager_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not is_department_manager(request.user):
            messages.error(request, "Access restricted to Department Managers and above.")
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper


def employee_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):

        is_employee = AccountProfile.objects.filter(
            user=request.user,
            role="Employee"
        ).exists()

        if not is_employee:
            messages.error(
                request,
                "You are not authorized to access this page."
            )
            return redirect("dashboard")

        if not EmployeeProfile.objects.filter(user=request.user).exists():
            messages.error(
                request,
                "Your employee profile has not been created."
            )
            return redirect("dashboard")

        return view_func(request, *args, **kwargs)

    return wrapper


def get_employee(request):
    return EmployeeProfile.objects.select_related(
        "user", "department", "position", "team", "target_position"
    ).get(user=request.user)


def get_hr_employees(request):
    employees = EmployeeProfile.objects.filter(
        employment_status="Active"
    ).select_related(
        "user", "department", "position", "team"
    )

    account = AccountProfile.objects.filter(
        user=request.user
    ).first()

    if account and account.organization:
        employees = employees.filter(
            user__account_profile__organization=account.organization
        )

    return employees.order_by("department__name", "team__name", "employee_id")


def get_hr_assignments(request):
    assignments = TaskAssignment.objects.select_related(
        "employee__user",
        "employee__department",
        "employee__position",
        "employee__team",
        "task"
    )

    account = AccountProfile.objects.filter(
        user=request.user
    ).first()

    if account and account.organization:
        assignments = assignments.filter(
            employee__user__account_profile__organization=account.organization
        )

    return assignments.order_by("-assigned_date", "-id")


# =========================================================
# CSRF FAILURE HANDLER
# =========================================================

def custom_csrf_failure_view(request, reason=""):
    """
    Gracefully handles CSRF token mismatches (e.g., rapid double-clicks,
    session token rotation on login, or stale cached form tokens).
    """
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        return redirect("dashboard")

    session = getattr(request, "session", None)
    if session and "_auth_user_id" in session:
        return redirect("dashboard")

    try:
        messages.warning(request, "Your security session refreshed. Please sign in again.")
    except Exception:
        pass

    return redirect("login_page")


# =========================================================
# LOGIN
# =========================================================

@ensure_csrf_cookie
def login_page(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        role = request.POST.get("role", "").strip()
        login_input = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not login_input or not password or not role:
            messages.error(request, "Please fill in all login fields.")
            return render(request, "Alpha/login.html")

        # 1. Try direct authentication by username
        user = authenticate(
            request,
            username=login_input,
            password=password
        )

        # 2. Try lookup by email
        if user is None:
            user_by_email = User.objects.filter(email__iexact=login_input).first()
            if user_by_email:
                user = authenticate(
                    request,
                    username=user_by_email.username,
                    password=password
                )

        # 3. Try lookup by employee_id (from AccountProfile or EmployeeProfile)
        if user is None:
            account_record = AccountProfile.objects.filter(employee_id__iexact=login_input).first()
            if account_record:
                user = authenticate(
                    request,
                    username=account_record.user.username,
                    password=password
                )
            else:
                emp_record = EmployeeProfile.objects.filter(employee_id__iexact=login_input).first()
                if emp_record:
                    user = authenticate(
                        request,
                        username=emp_record.user.username,
                        password=password
                    )

        if user is not None:

            account = AccountProfile.objects.filter(
                user=user
            ).first()

            if not account:
                messages.error(
                    request,
                    "Account profile not found for this user."
                )
                return render(request, "Alpha/login.html")

            # Successfully authenticate and log in directly
            login(request, user)

            if not request.POST.get("remember_me"):
                request.session.set_expiry(0)

            messages.success(request, f"Welcome back, {account.full_name}!")
            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url and next_url.startswith("/") and not next_url.startswith("//"):
                return redirect(next_url)
            return redirect("dashboard")

        else:
            messages.error(
                request,
                "Invalid login credentials. Please check your username, email, or employee ID and password."
            )

    return render(request, "Alpha/login.html")


# =========================================================
# HR REGISTRATION
# =========================================================

def register_page(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        organization = request.POST.get("organization", "").strip()

        if not all([full_name, email, password, confirm_password]):
            messages.error(request, "Please complete all required fields.")
            return render(request, "Alpha/register.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "Alpha/register.html")

        if len(password) < 8:
            messages.error(
                request,
                "Password must contain at least 8 characters."
            )
            return render(request, "Alpha/register.html")

        if User.objects.filter(username=email).exists():
            messages.error(request, "This email is already registered.")
            return render(request, "Alpha/register.html")

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "This email is already in use.")
            return render(request, "Alpha/register.html")

        try:
            with transaction.atomic():

                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=full_name
                )

                AccountProfile.objects.create(
                    user=user,
                    full_name=full_name,
                    role="HR Manager/Admin",
                    organization=organization
                )

            messages.success(
                request,
                "HR account created successfully. Please log in."
            )
            return redirect("login_page")

        except IntegrityError:
            messages.error(
                request,
                "Unable to create the account. Please try again."
            )

    return render(request, "Alpha/register.html")


# =========================================================
# DASHBOARD
# =========================================================

@login_required
def dashboard(request):

    account = AccountProfile.objects.filter(
        user=request.user
    ).first()

    if not account:
        messages.error(request, "Your account profile is missing.")
        logout(request)
        return redirect("login_page")

    # -------------------------------------------------------------
    # 1. HR ADMIN ROLE
    # -------------------------------------------------------------
    if account.role == "HR Manager/Admin":
        employees = get_hr_employees(request)
        total_employees = employees.count()
        active_employees = employees.filter(employment_status="Active").count()
        departments = Department.objects.all().order_by("name")
        positions = JobPosition.objects.select_related("department").all().order_by("department__name", "title")
        assignments = get_hr_assignments(request)

        # AI Workload Analysis for all employees
        workload_analyses = []
        workload_alerts_count = 0
        dept_scores = {}
        dept_counts = {}

        for emp in employees:
            analysis = WorkloadAnalyzer.analyze_employee(emp)
            workload_analyses.append({
                "employee": emp,
                "analysis": analysis,
            })
            if analysis["is_burnout_risk"]:
                workload_alerts_count += 1

            dept_name = emp.department.name if emp.department else "General"
            dept_scores[dept_name] = dept_scores.get(dept_name, 0) + analysis["workload_score"]
            dept_counts[dept_name] = dept_counts.get(dept_name, 0) + 1

        chart_labels = list(dept_scores.keys()) if dept_scores else ["Engineering", "Design", "QA", "HR", "Finance"]
        chart_data = [
            round(dept_scores[k] / dept_counts[k], 1) if dept_counts[k] > 0 else 50
            for k in chart_labels
        ] if dept_scores else [68, 52, 60, 42, 49]

        # AI Salary Equity Audits
        salary_audits = []
        salary_reviews_count = 0
        for emp in employees:
            sal_profile = SalaryEquityPredictor.predict_salary_profile(emp)
            salary_audits.append({
                "employee": emp,
                "profile": sal_profile,
            })
            if sal_profile["equity_status"] != "Fairly Compensated (Equitable)" and sal_profile["current_salary"]:
                salary_reviews_count += 1

        # AI Workload Imbalance Redistribution Suggestions
        redistributions = WorkloadAnalyzer.suggest_redistribution(employees)

        # Structured Department & Team Breakdown
        all_teams = Team.objects.select_related("department", "team_manager").order_by("department__name", "name")
        department_structure = []
        for dept in departments:
            dept_teams = []
            for t in all_teams.filter(department=dept):
                t_members = [e for e in employees if e.team_id == t.id]
                dept_teams.append({
                    "team": t,
                    "members": t_members,
                    "count": len(t_members)
                })
            d_members = [e for e in employees if e.department_id == dept.id]
            department_structure.append({
                "department": dept,
                "teams": dept_teams,
                "total_members": len(d_members),
                "roles_count": dept.positions.count()
            })

        context = {
            "profile": account,
            "total_employees": total_employees,
            "active_employees": active_employees,
            "departments_count": departments.count(),
            "departments": departments,
            "positions": positions,
            "employees": employees,
            "all_teams": all_teams,
            "department_structure": department_structure,
            "workload_analyses": workload_analyses,
            "workload_alerts_count": workload_alerts_count,
            "salary_audits": salary_audits,
            "salary_reviews_count": salary_reviews_count,
            "redistributions": redistributions,
            "chart_labels": chart_labels,
            "chart_data": chart_data,
            "assignments": assignments,
        }
        return render(
            request,
            "Alpha/hr_dashboard.html",
            context
        )

    # -------------------------------------------------------------
    # 2. DEPARTMENT MANAGER ROLE
    # -------------------------------------------------------------
    if account.role == "Department Manager":
        dept = Department.objects.filter(department_manager=request.user).first()
        if not dept:
            dept = Department.objects.filter(name=account.department).first() or Department.objects.first()

        teams = Team.objects.filter(department=dept).select_related("team_manager")
        dept_employees = EmployeeProfile.objects.filter(department=dept, employment_status="Active").select_related("user", "position", "team")

        # AI Workload analysis across department
        dept_workload = []
        burnout_count = 0
        total_dept_hours = Decimal("0")
        for emp in dept_employees:
            an = WorkloadAnalyzer.analyze_employee(emp)
            dept_workload.append({"employee": emp, "analysis": an})
            total_dept_hours += Decimal(str(an.get("estimated_hours", 0)))
            if an["is_burnout_risk"]:
                burnout_count += 1

        # Salary & Budget
        total_salary_spend = sum(
            emp.salary_records.order_by("-effective_date").first().salary_amount
            for emp in dept_employees if emp.salary_records.exists()
        ) if dept_employees else Decimal("0")

        # Department Leaves & Attendance
        dept_leaves = LeaveRequest.objects.filter(
            employee__department=dept
        ).select_related("employee__user").order_by("-applied_at")

        today = timezone.localdate()
        today_attendance = AttendanceRecord.objects.filter(
            employee__department=dept,
            date=today
        )
        present_count = today_attendance.filter(status="Present").count()

        context = {
            "profile": account,
            "department": dept,
            "teams": teams,
            "teams_count": teams.count(),
            "dept_employees": dept_employees,
            "total_employees": dept_employees.count(),
            "dept_workload": dept_workload,
            "burnout_count": burnout_count,
            "total_dept_hours": total_dept_hours,
            "total_salary_spend": total_salary_spend,
            "budget_remaining": (dept.budget - total_salary_spend) if dept else Decimal("0"),
            "pending_leaves": dept_leaves.filter(status="Pending").count(),
            "present_count": present_count,
            "attendance_rate": round((present_count / max(1, dept_employees.count())) * 100, 1),
            "recent_leaves": dept_leaves[:6],
        }
        return render(request, "Alpha/department_dashboard.html", context)

    # -------------------------------------------------------------
    # 3. TEAM MANAGER ROLE
    # -------------------------------------------------------------
    if account.role == "Team Manager":
        team = Team.objects.filter(team_manager=request.user).first()
        if not team:
            team = Team.objects.filter(department__name=account.department).first() or Team.objects.first()

        team_members = EmployeeProfile.objects.filter(team=team, employment_status="Active").select_related("user", "position", "team") if team else EmployeeProfile.objects.filter(department__name=account.department)[:5]

        # Workload analysis for team
        team_workload = []
        team_burnout_alerts = 0
        for m in team_members:
            an = WorkloadAnalyzer.analyze_employee(m)
            team_workload.append({"employee": m, "analysis": an})
            if an["is_burnout_risk"]:
                team_burnout_alerts += 1

        team_assignments = TaskAssignment.objects.filter(
            employee__in=team_members
        ).select_related("employee__user", "task").order_by("-assigned_date")

        team_leaves = LeaveRequest.objects.filter(
            employee__in=team_members
        ).select_related("employee__user").order_by("-applied_at")
        pending_leaves = team_leaves.filter(status="Pending")

        today = timezone.localdate()
        today_attendance = AttendanceRecord.objects.filter(
            employee__in=team_members,
            date=today
        ).select_related("employee__user")

        recent_reviews = PerformanceReview.objects.filter(
            reviewer=request.user
        ).select_related("employee__user")

        context = {
            "profile": account,
            "team": team,
            "team_members": team_members,
            "total_members": team_members.count(),
            "team_workload": team_workload,
            "team_burnout_alerts": team_burnout_alerts,
            "team_assignments": team_assignments[:10],
            "pending_tasks_count": team_assignments.filter(status__in=["Pending", "In Progress"]).count(),
            "completed_tasks_count": team_assignments.filter(status="Completed").count(),
            "pending_leaves": pending_leaves,
            "pending_leaves_count": pending_leaves.count(),
            "today_attendance": today_attendance,
            "recent_reviews": recent_reviews[:5],
        }
        return render(request, "Alpha/team_manager_dashboard.html", context)

    # -------------------------------------------------------------
    # 4. EMPLOYEE ROLE (9 Comprehensive Modules Overview)
    # -------------------------------------------------------------
    if account.role == "Employee":
        employee = EmployeeProfile.objects.filter(user=request.user).select_related("department", "position", "team", "target_position").first()
        if not employee:
            messages.error(request, "Your employee profile has not been created.")
            return render(request, "Alpha/employee_dashboard.html", {"profile": account})

        workload_analysis = WorkloadAnalyzer.analyze_employee(employee)
        career_readiness = CareerProgressionAdvisor.analyze_readiness(employee)
        salary_profile = SalaryEquityPredictor.predict_salary_profile(employee)

        assignments = employee.assignments.select_related("task").order_by("-assigned_date")
        pending_tasks = assignments.filter(status__in=["Pending", "In Progress"])
        completed_tasks = assignments.filter(status="Completed")

        today = timezone.localdate()
        today_record = AttendanceRecord.objects.filter(employee=employee, date=today).first()

        leaves = employee.leave_requests.all().order_by("-applied_at")
        approved_leave_days = sum(l.days_count for l in leaves if l.status == "Approved")
        pending_leave_reqs = leaves.filter(status="Pending")

        perf_reviews = employee.performance_reviews.select_related("reviewer").order_by("-created_at")
        latest_review = perf_reviews.first()

        notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
        unread_notifications_count = notifications.filter(is_read=False).count()

        context = {
            "profile": account,
            "employee": employee,
            "workload_analysis": workload_analysis,
            "career_readiness": career_readiness,
            "salary_profile": salary_profile,
            "assignments": assignments[:5],
            "total_tasks": assignments.count(),
            "pending_tasks_count": pending_tasks.count(),
            "completed_tasks_count": completed_tasks.count(),
            "total_skills": employee.employee_skills.count(),
            "today_attendance": today_record,
            "is_checked_in": bool(today_record and today_record.check_in),
            "is_checked_out": bool(today_record and today_record.check_out),
            "casual_leaves_left": max(0, 12 - approved_leave_days),
            "pending_leaves_count": pending_leave_reqs.count(),
            "latest_review": latest_review,
            "recent_notifications": notifications[:5],
            "unread_notifications_count": unread_notifications_count,
        }
        return render(
            request,
            "Alpha/employee_dashboard.html",
            context
        )

    messages.error(request, "Invalid account role.")
    logout(request)
    return redirect("login_page")


@login_required
def logout_page(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login_page")


# =========================================================
# HR: CREATE EMPLOYEE
# =========================================================

@login_required
def create_employee(request):

    if not is_hr_user(request.user):
        messages.error(request, "Only HR can create employee accounts.")
        return redirect("dashboard")

    departments = Department.objects.all().order_by("name")
    positions = JobPosition.objects.select_related(
        "department"
    ).order_by("title")

    if request.method == "POST":

        full_name = request.POST.get("full_name", "").strip()
        employee_id = request.POST.get("employee_id", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        department_id = request.POST.get("department")
        position_id = request.POST.get("position")
        experience_input = request.POST.get("experience_years", "0").strip()
        joining_date_input = request.POST.get("joining_date", "").strip()

        if not all([
            full_name,
            employee_id,
            email,
            password,
            department_id,
            position_id
        ]):
            messages.error(request, "Please complete all required fields.")
            return render(request, "Alpha/create_employee.html", {
                "departments": departments,
                "positions": positions
            })

        if len(password) < 8:
            messages.error(
                request,
                "Employee password must contain at least 8 characters."
            )
            return render(request, "Alpha/create_employee.html", {
                "departments": departments,
                "positions": positions
            })

        if User.objects.filter(username=employee_id).exists():
            messages.error(request, "Employee ID already exists.")
            return render(request, "Alpha/create_employee.html", {
                "departments": departments,
                "positions": positions
            })

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, "Alpha/create_employee.html", {
                "departments": departments,
                "positions": positions
            })

        if EmployeeProfile.objects.filter(
            employee_id=employee_id
        ).exists():
            messages.error(request, "Employee ID already exists.")
            return render(request, "Alpha/create_employee.html", {
                "departments": departments,
                "positions": positions
            })

        try:
            experience_years = Decimal(experience_input)

            if experience_years < 0 or experience_years > 60:
                raise InvalidOperation

        except (InvalidOperation, ValueError):
            messages.error(request, "Enter valid experience in years.")
            return render(request, "Alpha/create_employee.html", {
                "departments": departments,
                "positions": positions
            })

        department = Department.objects.filter(
            id=department_id
        ).first()

        position = JobPosition.objects.filter(
            id=position_id
        ).first()

        if not department or not position:
            messages.error(request, "Select a valid department and position.")
            return render(request, "Alpha/create_employee.html", {
                "departments": departments,
                "positions": positions
            })

        if position.department_id != department.id:
            messages.error(
                request,
                "The selected position does not belong to this department."
            )
            return render(request, "Alpha/create_employee.html", {
                "departments": departments,
                "positions": positions
            })

        joining_date = None

        if joining_date_input:
            try:
                joining_date = datetime.strptime(
                    joining_date_input,
                    "%Y-%m-%d"
                ).date()
            except ValueError:
                messages.error(request, "Enter a valid joining date.")
                return render(request, "Alpha/create_employee.html", {
                    "departments": departments,
                    "positions": positions
                })

        hr_account = AccountProfile.objects.filter(
            user=request.user
        ).first()

        organization = (
            hr_account.organization if hr_account else ""
        )

        try:
            with transaction.atomic():

                user = User.objects.create_user(
                    username=employee_id,
                    email=email,
                    password=password,
                    first_name=full_name
                )

                AccountProfile.objects.create(
                    user=user,
                    full_name=full_name,
                    role="Employee",
                    employee_id=employee_id,
                    organization=organization,
                    department=department.name,
                    designation=position.title
                )

                default_team = Team.objects.filter(department=department).first()
                EmployeeProfile.objects.create(
                    user=user,
                    employee_id=employee_id,
                    department=department,
                    team=default_team,
                    position=position,
                    experience_years=experience_years,
                    joining_date=joining_date,
                    employment_status="Active"
                )

            messages.success(
                request,
                "Employee account created successfully."
            )
            return redirect("create_employee")

        except IntegrityError:
            messages.error(
                request,
                "Unable to create employee. Check the employee ID and email."
            )

    return render(request, "Alpha/create_employee.html", {
        "departments": departments,
        "positions": positions
    })


# =========================================================
# EMPLOYEE: PROFILE
# =========================================================

@employee_required
def employee_profile(request):

    employee = get_employee(request)
    skills = employee.employee_skills.select_related("skill").all().order_by("skill__name")
    career_readiness = CareerProgressionAdvisor.analyze_readiness(employee)

    return render(
        request,
        "Alpha/employee_profile.html",
        {
            "employee": employee,
            "profile": employee.user.account_profile,
            "skills": skills,
            "career_readiness": career_readiness,
        }
    )


# =========================================================
# EMPLOYEE: SKILLS MANAGEMENT
# =========================================================

@employee_required
def employee_skills(request):

    employee = get_employee(request)

    if request.method == "POST":

        action = request.POST.get("action", "").strip()

        if action == "add":

            skill_name = request.POST.get("skill_name", "").strip()
            proficiency = request.POST.get("proficiency", "").strip()

            allowed_levels = [
                "Beginner",
                "Intermediate",
                "Advanced",
                "Expert"
            ]

            if not skill_name:
                messages.error(request, "Enter a skill name.")

            elif proficiency not in allowed_levels:
                messages.error(request, "Select a valid proficiency level.")

            else:
                try:
                    with transaction.atomic():

                        skill = Skill.objects.filter(
                            name__iexact=skill_name
                        ).first()

                        if skill is None:
                            skill = Skill.objects.create(name=skill_name)

                        existing = EmployeeSkill.objects.filter(
                            employee=employee,
                            skill=skill
                        ).exists()

                        if existing:
                            messages.warning(
                                request,
                                "This skill has already been added."
                            )
                        else:
                            EmployeeSkill.objects.create(
                                employee=employee,
                                skill=skill,
                                proficiency=proficiency
                            )
                            messages.success(
                                request,
                                "Skill added successfully."
                            )

                except IntegrityError:
                    messages.error(
                        request,
                        "This skill could not be added. Please try again."
                    )

        elif action == "update":

            skill_id = request.POST.get("skill_id")
            proficiency = request.POST.get("proficiency", "").strip()

            allowed_levels = [
                "Beginner",
                "Intermediate",
                "Advanced",
                "Expert"
            ]

            if proficiency not in allowed_levels:
                messages.error(request, "Select a valid proficiency level.")
            else:
                employee_skill = EmployeeSkill.objects.filter(
                    id=skill_id,
                    employee=employee
                ).first()

                if employee_skill:
                    employee_skill.proficiency = proficiency
                    employee_skill.save()
                    messages.success(
                        request,
                        "Skill updated successfully."
                    )
                else:
                    messages.error(request, "Skill record not found.")

        elif action == "delete":

            skill_id = request.POST.get("skill_id")

            employee_skill = EmployeeSkill.objects.filter(
                id=skill_id,
                employee=employee
            ).first()

            if employee_skill:
                employee_skill.delete()
                messages.success(
                    request,
                    "Skill deleted successfully."
                )
            else:
                messages.error(request, "Skill record not found.")

        else:
            messages.error(request, "Invalid action.")

        return redirect("employee_skills")

    skills = EmployeeSkill.objects.filter(
        employee=employee
    ).select_related(
        "skill"
    ).order_by("skill__name")

    return render(
        request,
        "Alpha/employee_skills.html",
        {
            "employee": employee,
            "skills": skills,
            "total_skills": skills.count()
        }
    )


# =========================================================
# EMPLOYEE: WORKLOAD
# =========================================================

@employee_required
def employee_workload(request):

    employee = get_employee(request)

    assignments = TaskAssignment.objects.filter(
        employee=employee
    ).select_related(
        "task"
    ).order_by("-assigned_date", "-id")

    total_tasks = assignments.count()
    completed_tasks = assignments.filter(status="Completed").count()
    pending_tasks = assignments.filter(status="Pending").count()
    in_progress_tasks = assignments.filter(status="In Progress").count()

    # AI Workload Imbalance & Burnout Analysis
    workload_analysis = WorkloadAnalyzer.analyze_employee(employee)

    return render(
        request,
        "Alpha/employee_workload.html",
        {
            "employee": employee,
            "assignments": assignments,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "in_progress_tasks": in_progress_tasks,
            "workload_analysis": workload_analysis,
        }
    )


# =========================================================
# EMPLOYEE: SALARY
# =========================================================

@employee_required
def employee_salary(request):

    employee = get_employee(request)

    salary_records = SalaryRecord.objects.filter(
        employee=employee
    ).order_by("-effective_date", "-id")

    latest_salary = salary_records.first()

    # AI ML Salary Prediction and Same-Level Equity Model
    salary_profile = SalaryEquityPredictor.predict_salary_profile(employee)

    return render(
        request,
        "Alpha/employee_salary.html",
        {
            "employee": employee,
            "salary_records": salary_records,
            "latest_salary": latest_salary,
            "position": employee.position,
            "salary_profile": salary_profile,
        }
    )


# =========================================================
# EMPLOYEE: CAREER
# =========================================================

@employee_required
def employee_career(request):

    employee = get_employee(request)

    if request.method == "POST":
        target_pos_id = request.POST.get("target_position")
        if target_pos_id:
            target_pos = JobPosition.objects.filter(id=target_pos_id).first()
            if target_pos:
                employee.target_position = target_pos
                employee.save(update_fields=["target_position"])
                messages.success(
                    request,
                    f"Target position set to {target_pos.title} ({target_pos.job_level})."
                )

    available_positions = JobPosition.objects.select_related("department").all().order_by("department__name", "title")
    career_readiness = CareerProgressionAdvisor.analyze_readiness(employee)

    return render(
        request,
        "Alpha/employee_career.html",
        {
            "employee": employee,
            "position": employee.position,
            "department": employee.department,
            "target_position": employee.target_position,
            "available_positions": available_positions,
            "career_readiness": career_readiness,
        }
    )


# =========================================================
# EMPLOYEE: PROGRESS
# =========================================================

@employee_required
def employee_progress(request):

    employee = get_employee(request)

    assignments = TaskAssignment.objects.filter(
        employee=employee
    ).select_related("task").order_by("-assigned_date", "-id")

    completed_tasks = assignments.filter(
        status="Completed"
    ).count()

    total_tasks = assignments.count()

    total_actual_hours = sum(
        (assignment.actual_hours for assignment in assignments),
        Decimal("0")
    )
    total_est_hours = sum(
        (assignment.task.estimated_hours for assignment in assignments),
        Decimal("0")
    )

    completion_percentage = (
        round((completed_tasks / total_tasks) * 100, 1)
        if total_tasks else 0
    )

    career_readiness = CareerProgressionAdvisor.analyze_readiness(employee)
    workload_analysis = WorkloadAnalyzer.analyze_employee(employee)

    return render(
        request,
        "Alpha/employee_progress.html",
        {
            "employee": employee,
            "assignments": assignments,
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "total_actual_hours": total_actual_hours,
            "total_est_hours": total_est_hours,
            "completion_percentage": completion_percentage,
            "career_readiness": career_readiness,
            "workload_analysis": workload_analysis,
        }
    )


# =========================================================
# HR: TASK ASSIGNMENT
# =========================================================

@login_required
def hr_task_assignment(request):

    if not is_hr_user(request.user):
        messages.error(
            request,
            "Only HR can access task assignment."
        )
        return redirect("dashboard")

    teams = Team.objects.all().select_related("department", "team_manager").order_by("name")
    employees = get_hr_employees(request)

    if request.method == "POST":

        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        team_id = request.POST.get("team") or request.POST.get("team_id")
        employee_id = request.POST.get("employee")
        complexity = request.POST.get("complexity", "").strip()
        estimated_hours_input = request.POST.get(
            "estimated_hours", ""
        ).strip()
        deadline_input = request.POST.get("deadline", "").strip()

        allowed_complexities = ["Low", "Medium", "High"]

        if not all([
            title,
            (team_id or employee_id),
            complexity,
            estimated_hours_input
        ]):
            messages.error(
                request,
                "Please complete all required task fields."
            )
            return redirect("hr_task_assignment")

        if complexity not in allowed_complexities:
            messages.error(request, "Select a valid task complexity.")
            return redirect("hr_task_assignment")

        try:
            estimated_hours = Decimal(estimated_hours_input)

            if (
                not estimated_hours.is_finite()
                or estimated_hours <= 0
                or estimated_hours > 1000
            ):
                raise InvalidOperation

        except (InvalidOperation, ValueError):
            messages.error(
                request,
                "Estimated hours must be greater than 0 and no more than 1000."
            )
            return redirect("hr_task_assignment")

        target_team = None
        assigned_emp = None

        if team_id:
            target_team = teams.filter(id=team_id).first()
            if not target_team:
                messages.error(request, "Select a valid team.")
                return redirect("hr_task_assignment")

            # Intelligently assign to the member of this team with lowest current active workload
            team_members = target_team.team_members.filter(employment_status="Active")
            if not team_members.exists():
                team_members = target_team.team_members.all()

            if team_members.exists():
                best_member = None
                min_active_hours = float("inf")
                for member in team_members:
                    active_h = sum(
                        float(a.task.estimated_hours)
                        for a in member.assignments.filter(status__in=["Pending", "In Progress"]).select_related("task")
                    )
                    if active_h < min_active_hours:
                        min_active_hours = active_h
                        best_member = member
                assigned_emp = best_member or team_members.first()
            else:
                assigned_emp = employees.first()

        elif employee_id:
            assigned_emp = employees.filter(id=employee_id).first()
            if not assigned_emp:
                messages.error(request, "Select a valid active employee.")
                return redirect("hr_task_assignment")
            target_team = assigned_emp.team

        if not assigned_emp:
            messages.error(request, "Could not determine an employee or team to assign.")
            return redirect("hr_task_assignment")

        deadline = None

        if deadline_input:
            try:
                deadline = datetime.strptime(
                    deadline_input,
                    "%Y-%m-%d"
                ).date()
            except ValueError:
                messages.error(request, "Enter a valid deadline.")
                return redirect("hr_task_assignment")

            if deadline < timezone.localdate():
                messages.error(
                    request,
                    "The deadline cannot be in the past."
                )
                return redirect("hr_task_assignment")

        try:
            with transaction.atomic():

                task = Task.objects.create(
                    title=title,
                    description=description,
                    complexity=complexity,
                    estimated_hours=estimated_hours,
                    deadline=deadline
                )

                TaskAssignment.objects.create(
                    employee=assigned_emp,
                    task=task,
                    status="Pending"
                )

                team_display_name = target_team.name if target_team else (assigned_emp.team.name if assigned_emp.team else assigned_emp.department.name)
                Notification.objects.create(
                    user=assigned_emp.user,
                    title=f"New Task Assigned: {title}",
                    message=f"A new task '{title}' has been assigned to team {team_display_name} ({complexity} complexity, {estimated_hours}h).",
                    category="Task"
                )

                if target_team and target_team.team_manager and target_team.team_manager != assigned_emp.user:
                    Notification.objects.create(
                        user=target_team.team_manager,
                        title=f"New Task for Team: {title}",
                        message=f"HR has assigned task '{title}' to your team {target_team.name}.",
                        category="Task"
                    )

            if target_team:
                messages.success(
                    request,
                    f"Task successfully assigned to team {target_team.name}."
                )
            else:
                messages.success(
                    request,
                    f"Task successfully assigned to {assigned_emp.user.first_name or assigned_emp.user.username}."
                )

        except IntegrityError:
            messages.error(
                request,
                "Unable to assign the task. Please try again."
            )

        return redirect("hr_task_assignment")

    assignments = get_hr_assignments(request)

    return render(
        request,
        "Alpha/hr_task_assignment.html",
        {
            "teams": teams,
            "employees": employees,
            "assignments": assignments,
            "total_assignments": assignments.count()
        }
    )


# =========================================================
# DEPARTMENT MANAGER VIEWS
# =========================================================

@department_manager_required
def department_dashboard_view(request):
    return dashboard(request)


@department_manager_required
def department_teams(request):
    account = AccountProfile.objects.filter(user=request.user).first()
    dept = Department.objects.filter(department_manager=request.user).first()
    if not dept:
        dept = Department.objects.filter(name=account.department).first() or Department.objects.first()

    teams = Team.objects.filter(department=dept).select_related("team_manager")
    team_data = []
    for t in teams:
        members = EmployeeProfile.objects.filter(team=t, employment_status="Active").select_related("user", "position")
        team_data.append({
            "team": t,
            "members": members,
            "members_count": members.count(),
        })

    return render(
        request,
        "Alpha/department_teams.html",
        {
            "profile": account,
            "department": dept,
            "team_data": team_data,
            "total_teams": teams.count(),
        }
    )


@department_manager_required
def department_reports(request):
    account = AccountProfile.objects.filter(user=request.user).first()
    dept = Department.objects.filter(department_manager=request.user).first()
    if not dept:
        dept = Department.objects.filter(name=account.department).first() or Department.objects.first()

    dept_employees = EmployeeProfile.objects.filter(department=dept, employment_status="Active").select_related("user", "position")
    
    # Workload distribution
    analyses = []
    overloaded = 0
    balanced = 0
    underutilized = 0
    for emp in dept_employees:
        an = WorkloadAnalyzer.analyze_employee(emp)
        analyses.append({"employee": emp, "analysis": an})
        if an["workload_level"] == "Overloaded":
            overloaded += 1
        elif an["workload_level"] == "Balanced":
            balanced += 1
        else:
            underutilized += 1

    # Attendance rate
    today = timezone.localdate()
    month_start = today.replace(day=1)
    attendance_records = AttendanceRecord.objects.filter(
        employee__department=dept,
        date__gte=month_start
    )
    present_total = attendance_records.filter(status="Present").count()
    attendance_total = attendance_records.count()
    dept_att_rate = round((present_total / max(1, attendance_total)) * 100, 1)

    return render(
        request,
        "Alpha/department_reports.html",
        {
            "profile": account,
            "department": dept,
            "total_employees": dept_employees.count(),
            "analyses": analyses,
            "overloaded_count": overloaded,
            "balanced_count": balanced,
            "underutilized_count": underutilized,
            "dept_att_rate": dept_att_rate,
            "total_budget": dept.budget if dept else Decimal("0"),
        }
    )


# =========================================================
# TEAM MANAGER VIEWS
# =========================================================

@team_manager_required
def team_manager_dashboard_view(request):
    return dashboard(request)


@team_manager_required
def team_manager_assign_task(request):
    account = AccountProfile.objects.filter(user=request.user).first()
    team = Team.objects.filter(team_manager=request.user).first()
    if not team:
        team = Team.objects.filter(department__name=account.department).first() or Team.objects.first()

    team_members = EmployeeProfile.objects.filter(team=team, employment_status="Active").select_related("user", "position") if team else EmployeeProfile.objects.filter(department__name=account.department)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        complexity = request.POST.get("complexity", "Medium").strip()
        estimated_hours = request.POST.get("estimated_hours", "10").strip()
        deadline_input = request.POST.get("deadline", "").strip()
        employee_id = request.POST.get("employee_id")

        if not all([title, complexity, estimated_hours, employee_id]):
            messages.error(request, "Please fill in all required task fields.")
            return redirect("team_manager_assign_task")

        assigned_emp = EmployeeProfile.objects.filter(id=employee_id).first()
        if not assigned_emp:
            messages.error(request, "Selected employee not found.")
            return redirect("team_manager_assign_task")

        deadline = None
        if deadline_input:
            try:
                deadline = datetime.strptime(deadline_input, "%Y-%m-%d").date()
            except ValueError:
                pass

        task = Task.objects.create(
            title=title,
            description=description,
            complexity=complexity,
            estimated_hours=Decimal(estimated_hours),
            deadline=deadline
        )
        TaskAssignment.objects.create(
            employee=assigned_emp,
            task=task,
            status="Pending"
        )

        Notification.objects.create(
            user=assigned_emp.user,
            title=f"New Task: {title}",
            message=f"You have been assigned a new task '{title}' by {account.full_name} ({complexity} Priority, Est. {estimated_hours}h).",
            category="Task"
        )

        messages.success(request, f"Task successfully assigned to {assigned_emp.user.get_full_name() or assigned_emp.user.username}!")
        return redirect("team_manager_dashboard")

    return render(
        request,
        "Alpha/team_manager_assign.html",
        {
            "profile": account,
            "team": team,
            "team_members": team_members,
        }
    )


@team_manager_required
def team_manager_leaves(request):
    account = AccountProfile.objects.filter(user=request.user).first()
    team = Team.objects.filter(team_manager=request.user).first()
    if not team:
        team = Team.objects.filter(department__name=account.department).first() or Team.objects.first()

    team_members = EmployeeProfile.objects.filter(team=team, employment_status="Active") if team else EmployeeProfile.objects.filter(department__name=account.department)

    leaves = LeaveRequest.objects.filter(
        employee__in=team_members
    ).select_related("employee__user", "employee__position").order_by("-applied_at")

    return render(
        request,
        "Alpha/team_manager_leaves.html",
        {
            "profile": account,
            "team": team,
            "leaves": leaves,
            "pending_count": leaves.filter(status="Pending").count(),
        }
    )


@team_manager_required
def team_manager_attendance(request):
    account = AccountProfile.objects.filter(user=request.user).first()
    team = Team.objects.filter(team_manager=request.user).first()
    if not team:
        team = Team.objects.filter(department__name=account.department).first() or Team.objects.first()

    team_members = EmployeeProfile.objects.filter(team=team, employment_status="Active").select_related("user", "position") if team else EmployeeProfile.objects.filter(department__name=account.department)

    today = timezone.localdate()
    today_records = AttendanceRecord.objects.filter(
        employee__in=team_members,
        date=today
    ).select_related("employee__user")

    recent_logs = AttendanceRecord.objects.filter(
        employee__in=team_members
    ).select_related("employee__user").order_by("-date")[:30]

    return render(
        request,
        "Alpha/team_manager_attendance.html",
        {
            "profile": account,
            "team": team,
            "team_members": team_members,
            "today_records": today_records,
            "recent_logs": recent_logs,
            "today": today,
        }
    )


@team_manager_required
def team_manager_feedback(request):
    account = AccountProfile.objects.filter(user=request.user).first()
    team = Team.objects.filter(team_manager=request.user).first()
    if not team:
        team = Team.objects.filter(department__name=account.department).first() or Team.objects.first()

    team_members = EmployeeProfile.objects.filter(team=team, employment_status="Active").select_related("user", "position") if team else EmployeeProfile.objects.filter(department__name=account.department)

    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        rating = request.POST.get("rating", "4.0").strip()
        period = request.POST.get("review_period", "Q4 2026").strip()
        feedback = request.POST.get("feedback", "").strip()

        assigned_emp = EmployeeProfile.objects.filter(id=employee_id).first()
        if not assigned_emp or not feedback:
            messages.error(request, "Please select an employee and provide feedback comments.")
            return redirect("team_manager_feedback")

        PerformanceReview.objects.create(
            employee=assigned_emp,
            reviewer=request.user,
            rating=Decimal(rating),
            review_period=period,
            feedback=feedback
        )

        Notification.objects.create(
            user=assigned_emp.user,
            title=f"Performance Review ({period})",
            message=f"{account.full_name} submitted your {period} performance review with a rating of {rating}/5.0★.",
            category="Performance"
        )

        messages.success(request, f"Performance evaluation successfully submitted for {assigned_emp.user.get_full_name() or assigned_emp.user.username}!")
        return redirect("team_manager_dashboard")

    recent_reviews = PerformanceReview.objects.filter(
        reviewer=request.user
    ).select_related("employee__user").order_by("-created_at")[:10]

    return render(
        request,
        "Alpha/team_manager_feedback.html",
        {
            "profile": account,
            "team": team,
            "team_members": team_members,
            "recent_reviews": recent_reviews,
        }
    )


# =========================================================
# EMPLOYEE 9 MODULES VIEWS
# =========================================================

@employee_required
def employee_tasks(request):
    employee = get_employee(request)
    assignments = employee.assignments.select_related("task").order_by("-assigned_date")

    pending_tasks = assignments.filter(status="Pending")
    in_progress_tasks = assignments.filter(status="In Progress")
    completed_tasks = assignments.filter(status="Completed")

    return render(
        request,
        "Alpha/employee_tasks.html",
        {
            "profile": employee.user.account_profile,
            "employee": employee,
            "assignments": assignments,
            "pending_tasks": pending_tasks,
            "in_progress_tasks": in_progress_tasks,
            "completed_tasks": completed_tasks,
            "total_tasks": assignments.count(),
        }
    )


@employee_required
def employee_task_updates(request):
    employee = get_employee(request)
    assignments = employee.assignments.select_related("task").order_by("-assigned_date")

    active_assignments = assignments.filter(status__in=["Pending", "In Progress"])
    recent_submissions = assignments.filter(submitted_at__isnull=False).order_by("-submitted_at")

    return render(
        request,
        "Alpha/employee_task_updates.html",
        {
            "profile": employee.user.account_profile,
            "employee": employee,
            "active_assignments": active_assignments,
            "recent_submissions": recent_submissions,
        }
    )


@employee_required
def employee_attendance(request):
    employee = get_employee(request)
    today = timezone.localdate()

    today_record = AttendanceRecord.objects.filter(employee=employee, date=today).first()
    attendance_qs = AttendanceRecord.objects.filter(employee=employee)

    # Quick stats
    present_count = attendance_qs.filter(status="Present").count()
    late_count = attendance_qs.filter(status="Late").count()
    total_records = attendance_qs.count()
    attendance_rate = round((present_count / max(1, total_records)) * 100, 1)

    attendance_history = attendance_qs.order_by("-date")[:30]

    return render(
        request,
        "Alpha/employee_attendance.html",
        {
            "profile": employee.user.account_profile,
            "employee": employee,
            "today_record": today_record,
            "attendance_history": attendance_history,
            "present_count": present_count,
            "late_count": late_count,
            "attendance_rate": attendance_rate,
            "today": today,
            "now_time": timezone.localtime().strftime("%I:%M %p"),
        }
    )


@employee_required
def employee_leaves(request):
    employee = get_employee(request)
    leaves = LeaveRequest.objects.filter(employee=employee).order_by("-applied_at")

    # Leave balance calculation (Standard 12 Casual, 7 Sick, 15 Earned)
    used_casual = sum(l.days_count for l in leaves if l.leave_type == "Casual Leave" and l.status == "Approved")
    used_sick = sum(l.days_count for l in leaves if l.leave_type == "Sick Leave" and l.status == "Approved")
    used_earned = sum(l.days_count for l in leaves if l.leave_type == "Earned Leave" and l.status == "Approved")

    casual_left = max(0, 12 - used_casual)
    sick_left = max(0, 7 - used_sick)
    earned_left = max(0, 15 - used_earned)

    return render(
        request,
        "Alpha/employee_leaves.html",
        {
            "profile": employee.user.account_profile,
            "employee": employee,
            "leaves": leaves,
            "casual_left": casual_left,
            "sick_left": sick_left,
            "earned_left": earned_left,
            "pending_count": leaves.filter(status="Pending").count(),
        }
    )


@employee_required
def employee_performance(request):
    employee = get_employee(request)
    reviews = employee.performance_reviews.select_related("reviewer").order_by("-created_at")

    # Integrated AI Promotion Readiness
    career_readiness = CareerProgressionAdvisor.analyze_readiness(employee)

    # Average rating
    if reviews.exists():
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1)
    else:
        avg_rating = 4.5

    return render(
        request,
        "Alpha/employee_performance.html",
        {
            "profile": employee.user.account_profile,
            "employee": employee,
            "reviews": reviews,
            "avg_rating": avg_rating,
            "career_readiness": career_readiness,
        }
    )


@employee_required
def employee_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")

    return render(
        request,
        "Alpha/employee_notifications.html",
        {
            "profile": request.user.account_profile,
            "notifications": notifications,
            "unread_count": notifications.filter(is_read=False).count(),
        }
    )


@employee_required
def employee_payslip(request):
    employee = get_employee(request)
    salary_record = employee.salary_records.order_by("-effective_date").first()
    annual_ctc = salary_record.salary_amount if salary_record else Decimal("900000")

    monthly_gross = round(annual_ctc / Decimal("12"), 2)
    basic_pay = round(monthly_gross * Decimal("0.50"), 2)
    hra = round(monthly_gross * Decimal("0.20"), 2)
    special_allowance = round(monthly_gross * Decimal("0.30"), 2)

    # Deductions
    provident_fund = round(basic_pay * Decimal("0.12"), 2)
    professional_tax = Decimal("200.00")
    income_tax_tds = round(monthly_gross * Decimal("0.05"), 2)
    total_deductions = provident_fund + professional_tax + income_tax_tds

    net_pay = monthly_gross - total_deductions

    # AI Salary profile
    salary_profile = SalaryEquityPredictor.predict_salary_profile(employee)

    current_month_str = timezone.localdate().strftime("%B %Y")

    return render(
        request,
        "Alpha/employee_payslip.html",
        {
            "profile": employee.user.account_profile,
            "employee": employee,
            "annual_ctc": annual_ctc,
            "monthly_gross": monthly_gross,
            "basic_pay": basic_pay,
            "hra": hra,
            "special_allowance": special_allowance,
            "provident_fund": provident_fund,
            "professional_tax": professional_tax,
            "income_tax_tds": income_tax_tds,
            "total_deductions": total_deductions,
            "net_pay": net_pay,
            "month_year": current_month_str,
            "salary_profile": salary_profile,
        }
    )


# =========================================================
# INTERACTIVE ACTION APIS
# =========================================================

@login_required
def api_check_in(request):
    if request.method == "POST":
        employee = EmployeeProfile.objects.filter(user=request.user).first()
        if not employee:
            messages.error(request, "Employee profile not found.")
            return redirect("dashboard")

        today = timezone.localdate()
        rec, _ = AttendanceRecord.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={"status": "Present"}
        )
        if not rec.check_in:
            now_local = timezone.localtime()
            rec.check_in = now_local.time()
            rec.status = "Present"
            rec.save()

            time_str = now_local.strftime('%I:%M %p')
            Notification.objects.create(
                user=request.user,
                title="Attendance Check-In Confirmed",
                message=f"Checked in successfully at {time_str} IST.",
                category="Attendance"
            )
            messages.success(request, f"Checked in successfully at {time_str} IST!")
        else:
            messages.info(request, f"You are already checked in at {rec.check_in.strftime('%I:%M %p')} IST.")

    return redirect(request.META.get("HTTP_REFERER", "employee_attendance"))


@login_required
def api_check_out(request):
    if request.method == "POST":
        employee = EmployeeProfile.objects.filter(user=request.user).first()
        if not employee:
            messages.error(request, "Employee profile not found.")
            return redirect("dashboard")

        today = timezone.localdate()
        rec = AttendanceRecord.objects.filter(employee=employee, date=today).first()
        if rec and rec.check_in:
            now_local = timezone.localtime()
            rec.check_out = now_local.time()

            # Calculate hours
            checkin_dt = datetime.combine(today, rec.check_in)
            checkout_dt = datetime.combine(today, rec.check_out)
            duration = (checkout_dt - checkin_dt).total_seconds() / 3600.0
            rec.working_hours = Decimal(f"{max(0.0, duration):.2f}")
            rec.save()

            time_str = now_local.strftime('%I:%M %p')
            Notification.objects.create(
                user=request.user,
                title="Attendance Check-Out Recorded",
                message=f"Checked out at {time_str} IST. Total shift hours: {rec.working_hours} hrs.",
                category="Attendance"
            )
            messages.success(request, f"Checked out successfully at {time_str} IST ({rec.working_hours} hours logged)!")
        else:
            messages.error(request, "Please check in first before checking out.")

    return redirect(request.META.get("HTTP_REFERER", "employee_attendance"))


@login_required
def api_apply_leave(request):
    if request.method == "POST":
        employee = EmployeeProfile.objects.filter(user=request.user).first()
        if not employee:
            messages.error(request, "Employee profile not found.")
            return redirect("dashboard")

        leave_type = request.POST.get("leave_type", "Casual Leave").strip()
        start_date_str = request.POST.get("start_date", "").strip()
        end_date_str = request.POST.get("end_date", "").strip()
        reason = request.POST.get("reason", "").strip()

        if not all([start_date_str, end_date_str, reason]):
            messages.error(request, "Please provide leave type, dates, and a valid reason.")
            return redirect("employee_leaves")

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect("employee_leaves")

        if end_date < start_date:
            messages.error(request, "End date cannot be earlier than start date.")
            return redirect("employee_leaves")

        days_count = (end_date - start_date).days + 1

        LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            days_count=days_count,
            reason=reason,
            status="Pending"
        )

        # Notify Team Manager if assigned
        if employee.team and employee.team.team_manager:
            Notification.objects.create(
                user=employee.team.team_manager,
                title=f"Leave Request from {employee.user.get_full_name() or employee.user.username}",
                message=f"{employee.user.get_full_name() or employee.user.username} applied for {days_count} days {leave_type} ({start_date_str} to {end_date_str}).",
                category="Leave"
            )

        messages.success(request, f"Leave application for {days_count} days submitted successfully! Awaiting manager approval.")
        return redirect("employee_leaves")

    return redirect("employee_leaves")


@login_required
def api_approve_leave(request, leave_id):
    if not is_team_manager(request.user):
        messages.error(request, "Permission denied.")
        return redirect("dashboard")

    leave = LeaveRequest.objects.filter(id=leave_id).select_related("employee__user").first()
    if not leave:
        messages.error(request, "Leave request not found.")
        return redirect("team_manager_leaves")

    comments = request.POST.get("review_comments", "Approved by Manager.").strip()
    leave.status = "Approved"
    leave.reviewed_by = request.user
    leave.review_comments = comments
    leave.reviewed_at = timezone.now()
    leave.save()

    Notification.objects.create(
        user=leave.employee.user,
        title="Leave Request Approved! ✓",
        message=f"Your {leave.leave_type} ({leave.start_date} to {leave.end_date}) was Approved. Comments: {comments}",
        category="Leave"
    )

    messages.success(request, f"Leave request for {leave.employee.user.get_full_name() or leave.employee.user.username} approved successfully!")
    return redirect("team_manager_leaves")


@login_required
def api_reject_leave(request, leave_id):
    if not is_team_manager(request.user):
        messages.error(request, "Permission denied.")
        return redirect("dashboard")

    leave = LeaveRequest.objects.filter(id=leave_id).select_related("employee__user").first()
    if not leave:
        messages.error(request, "Leave request not found.")
        return redirect("team_manager_leaves")

    comments = request.POST.get("review_comments", "Rejected by Manager.").strip()
    leave.status = "Rejected"
    leave.reviewed_by = request.user
    leave.review_comments = comments
    leave.reviewed_at = timezone.now()
    leave.save()

    Notification.objects.create(
        user=leave.employee.user,
        title="Leave Request Status Update",
        message=f"Your {leave.leave_type} ({leave.start_date} to {leave.end_date}) was Rejected. Comments: {comments}",
        category="Leave"
    )

    messages.info(request, f"Leave request for {leave.employee.user.get_full_name() or leave.employee.user.username} rejected.")
    return redirect("team_manager_leaves")


@login_required
def api_update_task(request, assignment_id):
    if request.method == "POST":
        employee = EmployeeProfile.objects.filter(user=request.user).first()
        if not employee:
            messages.error(request, "Employee profile not found.")
            return redirect("dashboard")

        assignment = TaskAssignment.objects.filter(id=assignment_id, employee=employee).select_related("task").first()
        if not assignment:
            messages.error(request, "Assigned task not found.")
            return redirect("employee_task_updates")

        status = request.POST.get("status", assignment.status).strip()
        additional_hours = request.POST.get("additional_hours", "0").strip()
        notes = request.POST.get("completion_notes", "").strip()

        assignment.status = status
        if additional_hours:
            try:
                assignment.actual_hours += Decimal(additional_hours)
            except (InvalidOperation, ValueError):
                pass

        if notes:
            assignment.completion_notes = notes

        if status == "Completed" and not assignment.submitted_at:
            assignment.submitted_at = timezone.now()

        assignment.save()

        # Notify team manager if completed
        if status == "Completed" and employee.team and employee.team.team_manager:
            Notification.objects.create(
                user=employee.team.team_manager,
                title=f"Task Completed: {assignment.task.title}",
                message=f"{employee.user.get_full_name() or employee.user.username} has completed task '{assignment.task.title}'. Total hours logged: {assignment.actual_hours}h.",
                category="Task"
            )

        messages.success(request, f"Progress updated for '{assignment.task.title}'!")
        return redirect("employee_task_updates")

    return redirect("employee_task_updates")


@login_required
def api_mark_notification_read(request, notif_id):
    Notification.objects.filter(id=notif_id, user=request.user).update(is_read=True)
    return redirect(request.META.get("HTTP_REFERER", "employee_notifications"))


@login_required
def api_mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect(request.META.get("HTTP_REFERER", "employee_notifications"))
