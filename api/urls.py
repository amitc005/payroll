from django.urls import path

from api.views import PayrollList
from api.views import TimeRecordAPI

urlpatterns = [
    path("time_reports/", TimeRecordAPI.as_view()),
    path("payroll_report/employee_reports", PayrollList.as_view()),
]
