import csv
import io
import re
from calendar import monthrange
from datetime import datetime
from decimal import Decimal

from api.messages import FILE_ID_ALREADY_PROCCED
from api.messages import INVALID_FILE_NAME
from api.models import FileIDRecord
from api.models import Payroll


def validate_time_report_file(file):
    file_id = get_timerecord_file_id(file.name)
    if not file_id:
        return None, INVALID_FILE_NAME

    if FileIDRecord.objects.filter(file_id=file_id).exists():
        return None, FILE_ID_ALREADY_PROCCED

    return True, ""


def get_timerecord_file_id(filename):
    result = re.compile(r"time-report-(\d+).csv").match(filename)
    if result is None:
        return None

    file_id = result.group(1)
    return int(file_id)


def get_time_record_from_file(file):
    wrapper = io.TextIOWrapper(file, encoding="utf-8")
    for record in csv.DictReader(wrapper):
        yield {
            "employee_id": int(record["employee id"]),
            "entry_date": record["date"],
            "job_group": record["job group"],
            "hours": Decimal(record["hours worked"]),
        }


def get_payroll_period(entry_date):

    if entry_date.day <= 15:
        return (
            datetime(day=1, month=entry_date.month, year=entry_date.year).date(),
            datetime(day=15, month=entry_date.month, year=entry_date.year).date(),
        )
    _, last_date = monthrange(entry_date.year, entry_date.month)
    return (
        datetime(day=16, month=entry_date.month, year=entry_date.year).date(),
        datetime(day=last_date, month=entry_date.month, year=entry_date.year).date(),
    )


def update_payroll_record(time_report):
    start_date, end_date = get_payroll_period(time_report.entry_date)
    data = {
        "start_date": start_date,
        "end_date": end_date,
        "employee_id": time_report.employee_id,
    }
    payroll_row = Payroll.objects.filter(**data).first()

    from api.serializers import PayrollSerializer

    if payroll_row:
        data["total_hours"] = payroll_row.total_hours + time_report.hours
        payroll_serialized = PayrollSerializer(payroll_row, data=data, partial=True)
        payroll_serialized.is_valid(raise_exception=True)
        payroll_serialized.save()
    else:

        data["total_hours"] = time_report.hours
        data["job_group"] = time_report.job_group
        payroll_serialized = PayrollSerializer(data=data)
        payroll_serialized.is_valid(raise_exception=True)
        payroll_serialized.save()
