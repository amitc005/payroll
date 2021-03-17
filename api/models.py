from django.db import models

from api.constants import JobGroup

# Create your models here.
JOB_GROUP_CHOCIES = [
    (JobGroup.JOB_GROUP_A.value, "Job Group A"),
    (JobGroup.JOB_GROUP_B.value, "Job Group B"),
]


class TimeReport(models.Model):
    employee_id = models.IntegerField()
    entry_date = models.DateField()
    job_group = models.CharField(max_length=1, choices=JOB_GROUP_CHOCIES)
    hours = models.DecimalField(default=0, max_digits=5, decimal_places=2)


class Payroll(models.Model):
    class Meta:
        ordering = ["employee_id", "-end_date"]

    start_date = models.DateField()
    end_date = models.DateField()
    amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    employee_id = models.IntegerField()
    total_hours = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    job_group = models.CharField(max_length=1, choices=JOB_GROUP_CHOCIES)


class FileIDRecord(models.Model):
    file_id = models.IntegerField()
    created_date = models.DateField(auto_now_add=True)
