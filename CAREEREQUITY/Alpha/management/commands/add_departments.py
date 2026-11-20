
from django.core.management.base import BaseCommand
from Alpha.models import Department, JobPosition


class Command(BaseCommand):
    help = "Add sample departments and job positions"

    def handle(self, *args, **kwargs):

        departments_data = {
            "Computer Science": {
                "description": "Software development and computer science operations.",
                "positions": [
                    ("Software Developer", "Junior", 25000, 45000, 0),
                    ("Senior Software Developer", "Senior", 50000, 90000, 3),
                    ("Python Developer", "Junior", 25000, 50000, 0),
                    ("Full Stack Developer", "Intermediate", 40000, 70000, 2),
                    ("Software Tester", "Junior", 20000, 40000, 0),
                ],
            },

            "Human Resources": {
                "description": "Employee recruitment and workforce management.",
                "positions": [
                    ("HR Executive", "Junior", 20000, 35000, 0),
                    ("HR Manager", "Senior", 50000, 80000, 4),
                    ("Recruitment Specialist", "Intermediate", 30000, 50000, 2),
                ],
            },

            "Finance": {
                "description": "Financial planning, accounting and budgeting.",
                "positions": [
                    ("Accountant", "Junior", 20000, 35000, 0),
                    ("Financial Analyst", "Intermediate", 35000, 60000, 2),
                    ("Finance Manager", "Senior", 50000, 85000, 5),
                ],
            },

            "Marketing": {
                "description": "Marketing strategy and brand promotion.",
                "positions": [
                    ("Marketing Executive", "Junior", 20000, 35000, 0),
                    ("Digital Marketing Specialist", "Intermediate", 30000, 50000, 2),
                    ("Marketing Manager", "Senior", 50000, 80000, 5),
                ],
            },

            "Information Technology": {
                "description": "IT infrastructure and technical support.",
                "positions": [
                    ("IT Support Executive", "Junior", 18000, 30000, 0),
                    ("System Administrator", "Intermediate", 30000, 50000, 2),
                    ("Network Engineer", "Intermediate", 30000, 55000, 2),
                    ("IT Manager", "Senior", 50000, 85000, 5),
                ],
            },
        }

        for department_name, details in departments_data.items():

            department, created = Department.objects.get_or_create(
                name=department_name,
                defaults={
                    "description": details["description"]
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Department added: {department_name}"
                    )
                )
            else:
                self.stdout.write(
                    f"Department already exists: {department_name}"
                )

            for position_data in details["positions"]:

                title, level, min_salary, max_salary, experience = position_data

                position, position_created = JobPosition.objects.get_or_create(
                    title=title,
                    department=department,
                    job_level=level,
                    defaults={
                        "minimum_salary": min_salary,
                        "maximum_salary": max_salary,
                        "required_experience": experience,
                    }
                )

                if position_created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Position added: {title} - {department_name}"
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                "\nAll departments and job positions processed successfully!"
            )
        )

