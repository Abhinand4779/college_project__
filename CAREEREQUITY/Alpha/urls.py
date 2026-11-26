from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path("", views.login_page, name="login_page"),
    path("accounts/login/", views.login_page, name="accounts_login"),
    path("register/", views.register_page, name="register_page"),
    path("logout/", views.logout_page, name="logout_page"),
    path("password-reset/", views.password_reset_request, name="password_reset_request"),
    path("password-reset/confirm/<str:token>/", views.password_reset_confirm, name="password_reset_confirm"),

    # Main dashboard (Auto-routed by role: HR Admin, Department Manager, Team Manager, Employee)
    path("dashboard/", views.dashboard, name="dashboard"),

    # HR Admin pages
    path("hr/create-employee/", views.create_employee, name="create_employee"),
    path("hr/task-assignment/", views.hr_task_assignment, name="hr_task_assignment"),

    # Department Manager pages
    path("dept/dashboard/", views.department_dashboard_view, name="department_dashboard"),
    path("dept/teams/", views.department_teams, name="department_teams"),
    path("dept/reports/", views.department_reports, name="department_reports"),

    # Team Manager pages
    path("manager/team/", views.team_manager_dashboard_view, name="team_manager_dashboard"),
    path("manager/assign-task/", views.team_manager_assign_task, name="team_manager_assign_task"),
    path("manager/leaves/", views.team_manager_leaves, name="team_manager_leaves"),
    path("manager/attendance/", views.team_manager_attendance, name="team_manager_attendance"),
    path("manager/feedback/", views.team_manager_feedback, name="team_manager_feedback"),

    # Employee 9 Modules
    path("employee/dashboard/", views.dashboard, name="employee_dashboard"),
    path("employee/profile/", views.employee_profile, name="employee_profile"),
    path("employee/tasks/", views.employee_tasks, name="employee_tasks"),
    path("employee/task-updates/", views.employee_task_updates, name="employee_task_updates"),
    path("employee/attendance/", views.employee_attendance, name="employee_attendance"),
    path("employee/leaves/", views.employee_leaves, name="employee_leaves"),
    path("employee/performance/", views.employee_performance, name="employee_performance"),
    path("employee/notifications/", views.employee_notifications, name="employee_notifications"),
    path("employee/salary/", views.employee_salary, name="employee_salary"),
    path("employee/payslip/", views.employee_payslip, name="employee_payslip"),

    # Existing employee sub-pages (backward compatibility)
    path("employee/skills/", views.employee_skills, name="employee_skills"),
    path("employee/workload/", views.employee_workload, name="employee_workload"),
    path("employee/career/", views.employee_career, name="employee_career"),
    path("employee/progress/", views.employee_progress, name="employee_progress"),

    # Interactive Actions / APIs
    path("actions/attendance/check-in/", views.api_check_in, name="api_check_in"),
    path("actions/attendance/check-out/", views.api_check_out, name="api_check_out"),
    path("actions/leaves/apply/", views.api_apply_leave, name="api_apply_leave"),
    path("actions/leaves/<int:leave_id>/approve/", views.api_approve_leave, name="api_approve_leave"),
    path("actions/leaves/<int:leave_id>/reject/", views.api_reject_leave, name="api_reject_leave"),
    path("actions/tasks/<int:assignment_id>/update/", views.api_update_task, name="api_update_task"),
    path("actions/notifications/<int:notif_id>/read/", views.api_mark_notification_read, name="api_mark_notification_read"),
    path("actions/notifications/read-all/", views.api_mark_all_notifications_read, name="api_mark_all_notifications_read"),
]
