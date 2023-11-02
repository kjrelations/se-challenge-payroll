from django.db import models

class TimeReport(models.Model):
    report_id = models.CharField(max_length=255)
    date = models.DateField()
    hours_worked = models.FloatField()
    employee_id = models.CharField(max_length=255)
    job_group = models.CharField(max_length=1)
    # Can add uploaded timestamp dateTime field if desired
