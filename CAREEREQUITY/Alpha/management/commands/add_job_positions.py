
from django.core.management.base import BaseCommand
from Alpha.models import Department, JobPosition


class Command(BaseCommand):
    help = "Add job positions to CareerEquity AI"

    def handle(self, *args, **kwargs):

        positions_data = [
            # COMPUTER SCIENCE
            {
                "department": "Computer Science",
                "title": "Software Developer",
                "level": "Junior",
                "minimum_salary": 25000,
                "maximum_salary": 45000,
                "experience": 0,
            },
            {
                "department": "Computer Science",
                "title": "Senior Software Developer",
                "level": "Senior",
                "minimum_salary": 50000,
                "maximum_salary": 90000,
                "experience": 3,
            },
            {
                "department": "Computer Science",
                "title": "Python Developer",
                "level": "Junior",
                "minimum_salary": 25000,
                "maximum_salary": 50000,
                "experience": 0,
            },
            {
                "department": "Computer Science",
                "title": "Full Stack Developer",
                "level": "Intermediate",
                "minimum_salary": 40000,
                "maximum_salary": 70000,
                "experience": 2,
            },
            {
                "department": "Computer Science",
                "title": "Software Tester",
                "level": "Junior",
                "minimum_salary": 20000,
                "maximum_salary": 40000,
                "experience": 0,
            },

            # HUMAN RESOURCES
            {
                "department": "Human Resources",
                "title": "HR Executive",
                "level": "Junior",
                "minimum_salary": 20000,
                "maximum_salary": 35000,
                "experience": 0,
            },
            {
                "department": "Human Resources",
                "title": "HR Manager",
                "level": "Senior",
                "minimum_salary": 50000,
                "maximum_salary": 80000,
                "experience": 4,
            },
            {
                "department": "Human Resources",
                "title": "Recruitment Specialist",
                "level": "Intermediate",
                "minimum_salary": 30000,
                "maximum_salary": 50000,
                "experience": 2,
            },

            # FINANCE
            {
                "department": "Finance",
                "title": "Accountant",
                "level": "Junior",
                "minimum_salary": 20000,
                "maximum_salary": 35000,
                "experience": 0,
            },
            {
                "department": "Finance",
                "title": "Financial Analyst",
                "level": "Intermediate",
                "minimum_salary": 35000,
                "maximum_salary": 60000,
                "experience": 2,
            },
            {
                "department": "Finance",
                "title": "Finance Manager",
                "level": "Senior",
                "minimum_salary": 50000,
                "maximum_salary": 85000,
                "experience": 5,
            },

            # MARKETING
            {
                "department": "Marketing",
                "title": "Marketing Executive",
                "level": "Junior",
                "minimum_salary": 20000,
                "maximum_salary": 35000,
                "experience": 0,
            },
            {
                "department": "Marketing",
                "title": "Digital Marketing Specialist",
                "level": "Intermediate",
                "minimum_salary": 30000,
                "maximum_salary": 50000,
                "experience": 2,
            },
            {
                "department": "Marketing",
                "title": "Marketing Manager",
                "level": "Senior",
                "minimum_salary": 50000,
                "maximum_salary": 80000,
                "experience": 5,
            },

            # INFORMATION TECHNOLOGY
            {
                "department": "Information Technology",
                "title": "IT Support Executive",
                "level": "Junior",
                "minimum_salary": 18000,
                "maximum_salary": 30000,
                "experience": 0,
            },
            {
                "department": "Information Technology",
                "title": "System Administrator",
                "level": "Intermediate",
                "minimum_salary": 30000,
                "maximum_salary": 50000,
                "experience": 2,
            },
            {
                "department": "Information Technology",
                "title": "Network Engineer",
                "level": "Intermediate",
                "minimum_salary": 30000,
                "maximum_salary": 55000,
                "experience": 2,
            },
            {
                "department": "Information Technology",
                "title": "IT Manager",
                "level": "Senior",
                "minimum_salary": 50000,
                "maximum_salary": 85000,
                "experience": 5,
            },
        ]

        added = 0
        existing = 0

        for item in positions_data:

            try:
                department = Department.objects.get(
                    name=item["department"]
                )
            except Department.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"Department not found: {item['department']}. "
                        "Add departments first."
                    )
                )
                continue

            position, created = JobPosition.objects.get_or_create(
                title=item["title"],
                department=department,
                job_level=item["level"],
                defaults={
                    "minimum_salary": item["minimum_salary"],
                    "maximum_salary": item["maximum_salary"],
                    "required_experience": item["experience"],
                }
            )

            if created:
                added += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Added: {position.title} - {department.name}"
                    )
                )
            else:
                existing += 1
                self.stdout.write(
                    f"Already exists: {position.title} - {department.name}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nCompleted! Added: {added}, Already existing: {existing}"
            )
        )


