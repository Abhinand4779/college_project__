
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path("", views.login_page, name="login_page"),
    path("register/", views.register_page, name="register_page"),
    path("logout/", views.logout_page, name="logout_page"),

    # Main dashboard
    path("dashboard/", views.dashboard, name="dashboard"),

    # HR pages
    path(
        "hr/create-employee/",
        views.create_employee,
        name="create_employee"
    ),
    path(
        "hr/task-assignment/",
        views.hr_task_assignment,
        name="hr_task_assignment"
    ),

    # Employee pages
    path(
        "employee/profile/",
        views.employee_profile,
        name="employee_profile"
    ),
    path(
        "employee/skills/",
        views.employee_skills,
        name="employee_skills"
    ),
    path(
        "employee/workload/",
        views.employee_workload,
        name="employee_workload"
    ),
    path(
        "employee/salary/",
        views.employee_salary,
        name="employee_salary"
    ),
    path(
        "employee/career/",
        views.employee_career,
        name="employee_career"
    ),
    path(
        "employee/progress/",
        views.employee_progress,
        name="employee_progress"
    ),
]
