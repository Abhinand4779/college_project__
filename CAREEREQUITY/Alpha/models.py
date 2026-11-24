
from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


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
    assigned_date = models.DateField(auto_now_add=True)

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


class AccountProfile(models.Model):
    ROLE_CHOICES = [
        ("HR Manager/Admin", "HR Manager/Admin"),
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
