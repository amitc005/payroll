from django.db import models

# Create your models here.


class TimeReport(models.Model):
    JOB_GROUP_A = "A"
    JOB_GROUP_B = "B"

    HOURLY_PAY = {JOB_GROUP_A: 20, JOB_GROUP_B: 30}

    JOB_GROUP_CHOCIES = [(JOB_GROUP_A, "Job Group A"), (JOB_GROUP_B, "Job Group B")]
    employee_id = models.IntegerField()
    entry_date = models.DateField()
    job_group = models.CharField(max_length=1, choices=JOB_GROUP_CHOCIES)
    hours = models.DecimalField(default=0, max_digits=5, decimal_places=2)

    def get_paid_amount(self):
        return self.hours * self.HOURLY_PAY[self.job_group]


class Payroll(models.Model):
    class Meta:
        ordering = ["employee_id", "-end_date"]

    start_date = models.DateField()
    end_date = models.DateField()
    amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    employee_id = models.IntegerField()


class FileIDRecord(models.Model):
    file_id = models.IntegerField()
    created_date = models.DateField(auto_now_add=True)
