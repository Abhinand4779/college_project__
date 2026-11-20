
from django.contrib import admin
from .models import (
    Department,
    JobPosition,
    EmployeeProfile,
    Skill,
    EmployeeSkill,
    Task,
    TaskAssignment,
    SalaryRecord
)

admin.site.register(Department)
admin.site.register(JobPosition)
admin.site.register(EmployeeProfile)
admin.site.register(Skill)
admin.site.register(EmployeeSkill)
admin.site.register(Task)
admin.site.register(TaskAssignment)
admin.site.register(SalaryRecord)
