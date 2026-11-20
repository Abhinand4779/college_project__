
from datetime import datetime
from decimal import Decimal, InvalidOperation
from functools import wraps

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.utils import timezone

from .models import (
    AccountProfile,
    EmployeeProfile,
    Department,
    JobPosition,
    Skill,
    EmployeeSkill,
    SalaryRecord,
    Task,
    TaskAssignment,
)


# =========================================================
# HELPER FUNCTIONS AND DECORATORS
# =========================================================

def is_hr_user(user):
    return AccountProfile.objects.filter(
        user=user,
        role="HR Manager/Admin"
    ).exists()


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
        "user", "department", "position"
    ).get(user=request.user)


def get_hr_employees(request):
    employees = EmployeeProfile.objects.filter(
        employment_status="Active"
    ).select_related(
        "user", "department", "position"
    )

    account = AccountProfile.objects.filter(
        user=request.user
    ).first()

    if account and account.organization:
        employees = employees.filter(
            user__account_profile__organization=account.organization
        )

    return employees.order_by("user__first_name", "employee_id")


def get_hr_assignments(request):
    assignments = TaskAssignment.objects.select_related(
        "employee__user",
        "employee__department",
        "employee__position",
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
# LOGIN
# =========================================================

def login_page(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        role = request.POST.get("role", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if role == "HR Manager/Admin":
            username = username.lower()

        if not username or not password or not role:
            messages.error(request, "Please fill in all login fields.")
            return render(request, "Alpha/login.html")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            account = AccountProfile.objects.filter(
                user=user
            ).first()

            if account and account.role == role:

                login(request, user)

                if not request.POST.get("remember_me"):
                    request.session.set_expiry(0)

                messages.success(request, "Login successful!")
                return redirect("dashboard")

            messages.error(
                request,
                "The selected role does not match this account."
            )

        else:
            messages.error(
                request,
                "Invalid username or password."
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

    if account.role == "HR Manager/Admin":
        return render(
            request,
            "Alpha/hr_dashboard.html",
            {"profile": account}
        )

    if account.role == "Employee":
        return render(
            request,
            "Alpha/employee_dashboard.html",
            {"profile": account}
        )

    messages.error(request, "Invalid account role.")
    logout(request)
    return redirect("login_page")


# =========================================================
# LOGOUT
# =========================================================

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

                EmployeeProfile.objects.create(
                    user=user,
                    employee_id=employee_id,
                    department=department,
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

    return render(
        request,
        "Alpha/employee_profile.html",
        {
            "employee": employee,
            "profile": employee.user.account_profile
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

    return render(
        request,
        "Alpha/employee_workload.html",
        {
            "employee": employee,
            "assignments": assignments,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "in_progress_tasks": in_progress_tasks
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

    return render(
        request,
        "Alpha/employee_salary.html",
        {
            "employee": employee,
            "salary_records": salary_records,
            "latest_salary": latest_salary,
            "position": employee.position
        }
    )


# =========================================================
# EMPLOYEE: CAREER
# =========================================================

@employee_required
def employee_career(request):

    employee = get_employee(request)

    skills = EmployeeSkill.objects.filter(
        employee=employee
    ).select_related("skill").order_by("skill__name")

    return render(
        request,
        "Alpha/employee_career.html",
        {
            "employee": employee,
            "skills": skills,
            "position": employee.position,
            "department": employee.department
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

    completion_percentage = (
        round((completed_tasks / total_tasks) * 100, 1)
        if total_tasks else 0
    )

    return render(
        request,
        "Alpha/employee_progress.html",
        {
            "employee": employee,
            "assignments": assignments,
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "total_actual_hours": total_actual_hours,
            "completion_percentage": completion_percentage
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

    employees = get_hr_employees(request)

    if request.method == "POST":

        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        employee_id = request.POST.get("employee")
        complexity = request.POST.get("complexity", "").strip()
        estimated_hours_input = request.POST.get(
            "estimated_hours", ""
        ).strip()
        deadline_input = request.POST.get("deadline", "").strip()

        allowed_complexities = ["Low", "Medium", "High"]

        if not all([
            title,
            employee_id,
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

        employee = employees.filter(
            id=employee_id
        ).first()

        if not employee:
            messages.error(
                request,
                "Select a valid active employee."
            )
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
                    employee=employee,
                    task=task
                )

            messages.success(
                request,
                f"Task successfully assigned to {employee.user.first_name or employee.user.username}."
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
            "employees": employees,
            "assignments": assignments,
            "total_assignments": assignments.count()
        }
    )
