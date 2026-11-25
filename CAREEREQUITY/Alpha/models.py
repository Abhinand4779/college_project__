from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    department_manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_departments"
    )
    budget = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=5000000.00
    )

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="teams"
    )
    team_manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_teams"
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.department.name})"


class JobPosition(models.Model):
    title = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="positions"
    )
    job_level = models.CharField(max_length=50)
    minimum_salary = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True
    )
    maximum_salary = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True
    )
    required_experience = models.DecimalField(
        max_digits=4, decimal_places=1,
        default=0
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} - {self.job_level}"


class EmployeeProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="employee_profile"
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_members"
    )
    position = models.ForeignKey(
        JobPosition,
        on_delete=models.PROTECT
    )
    experience_years = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0
    )
    joining_date = models.DateField(
        null=True,
        blank=True
    )
    phone = models.CharField(
        max_length=20,
        blank=True
    )
    employment_status = models.CharField(
        max_length=20,
        choices=[
            ("Active", "Active"),
            ("Inactive", "Inactive"),
        ],
        default="Active"
    )
    target_position = models.ForeignKey(
        JobPosition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="aspiring_employees"
    )

    def __str__(self):
        return f"{self.employee_id} - {self.user.username}"


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class EmployeeSkill(models.Model):
    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name="employee_skills"
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE
    )
    proficiency = models.CharField(
        max_length=20,
        choices=[
            ("Beginner", "Beginner"),
            ("Intermediate", "Intermediate"),
            ("Advanced", "Advanced"),
            ("Expert", "Expert"),
        ],
        default="Beginner"
    )

    class Meta:
        unique_together = ("employee", "skill")

    def __str__(self):
        return f"{self.employee} - {self.skill}"


class PositionRequirement(models.Model):
    position = models.ForeignKey(
        JobPosition,
        on_delete=models.CASCADE,
        related_name="requirements"
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE
    )
    required_proficiency = models.CharField(
        max_length=20,
        choices=[
            ("Beginner", "Beginner"),
            ("Intermediate", "Intermediate"),
            ("Advanced", "Advanced"),
            ("Expert", "Expert"),
        ],
        default="Intermediate"
    )

    class Meta:
        unique_together = ("position", "skill")

    def __str__(self):
        return f"{self.position.title} ({self.position.job_level}) requires {self.skill.name} ({self.required_proficiency})"


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    complexity = models.CharField(
        max_length=20,
        choices=[
            ("Low", "Low"),
            ("Medium", "Medium"),
            ("High", "High"),
        ]
    )
    estimated_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )
    deadline = models.DateField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title


class TaskAssignment(models.Model):
    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name="assignments"
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="assignments"
    )
    actual_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("In Progress", "In Progress"),
            ("Completed", "Completed"),
        ],
        default="Pending"
    )
    completion_notes = models.TextField(blank=True)
    assigned_date = models.DateField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee} - {self.task}"


class SalaryRecord(models.Model):
    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name="salary_records"
    )
    salary_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    effective_date = models.DateField()

    def __str__(self):
        return f"{self.employee} - {self.salary_amount}"


class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ("Present", "Present"),
        ("Late", "Late"),
        ("Half Day", "Half Day"),
        ("Absent", "Absent"),
        ("On Leave", "On Leave"),
    ]

    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )
    date = models.DateField(default=timezone.now)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Present"
    )
    working_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.0
    )
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ("employee", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.employee.employee_id} - {self.date} ({self.status})"


class LeaveRequest(models.Model):
    LEAVE_CHOICES = [
        ("Casual Leave", "Casual Leave"),
        ("Sick Leave", "Sick Leave"),
        ("Earned Leave", "Earned Leave"),
        ("Emergency", "Emergency"),
    ]
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name="leave_requests"
    )
    leave_type = models.CharField(
        max_length=30,
        choices=LEAVE_CHOICES
    )
    start_date = models.DateField()
    end_date = models.DateField()
    days_count = models.IntegerField(default=1)
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_leaves"
    )
    review_comments = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-applied_at"]

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.status})"


class PerformanceReview(models.Model):
    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name="performance_reviews"
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="submitted_reviews"
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=4.0
    )
    feedback = models.TextField()
    review_period = models.CharField(
        max_length=50,
        default="Q4 2026"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.employee} - {self.rating}★ ({self.review_period})"


class Notification(models.Model):
    CATEGORY_CHOICES = [
        ("Task", "Task"),
        ("Leave", "Leave"),
        ("Attendance", "Attendance"),
        ("Performance", "Performance"),
        ("Announcement", "Announcement"),
        ("Salary", "Salary"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="Announcement"
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class AccountProfile(models.Model):
    ROLE_CHOICES = [
        ("HR Manager/Admin", "HR Manager/Admin"),
        ("Department Manager", "Department Manager"),
        ("Team Manager", "Team Manager"),
        ("Employee", "Employee"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="account_profile"
    )
    full_name = models.CharField(max_length=150)
    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES
    )
    employee_id = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )
    organization = models.CharField(
        max_length=150,
        blank=True
    )
    department = models.CharField(
        max_length=100,
        blank=True
    )
    designation = models.CharField(
        max_length=100,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.role}"
