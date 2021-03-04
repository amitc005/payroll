import io
from calendar import monthrange
from datetime import datetime

import pytest

from api.messages import FILE_ID_ALREADY_PROCCED
from api.messages import INVALID_FILE_NAME
from api.models import FileIDRecord
from api.models import Payroll
from api.serializers import TimeRecordSerializer
from api.utils import get_payroll_period
from api.utils import get_timerecord_file_id
from api.utils import update_payroll_record
from api.utils import validate_time_report_file


@pytest.mark.django_db
class TestUtil:
    def test_get_timerecord_file_id(self):
        for file_id in range(100):
            file_name = f"time-report-{file_id}.csv"
            assert get_timerecord_file_id(file_name) == file_id

    @pytest.mark.parametrize(
        "file_id", ["time-report-{file_id}.csv", "----", "invalid_file_name"]
    )
    def test_get_timerecord_file_id_with_invalid_name(self, file_id):
        assert get_timerecord_file_id(f"time-report-{file_id}.csv") is None

    def test_validate_time_report_file(self):
        with io.BytesIO(b"Test File") as file:
            file.name = "time-report-1.csv"
            valid, error_msg = validate_time_report_file(file)
            assert valid

    def test_validate_time_report_file_where_file_id_already_in_record(self):
        FileIDRecord.objects.create(file_id=1)
        with io.BytesIO(b"Test File") as file:
            file.name = "time-report-1.csv"
            valid, error_msg = validate_time_report_file(file)
            assert valid is None
            assert error_msg == FILE_ID_ALREADY_PROCCED

    def test_validate_time_report_file_where_file_id_invalid_file(self):
        FileIDRecord.objects.create(file_id=1)
        with io.BytesIO(b"Test File") as file:
            file.name = "invalid-file-name"
            valid, error_msg = validate_time_report_file(file)
            assert valid is None
            assert error_msg == INVALID_FILE_NAME

    @pytest.mark.parametrize(
        "time_entry_date,expected_start,expected_end",
        [
            ("2021-02-23", "2021-02-16", "2021-02-28"),  # Feb which has 28th
            ("2020-02-23", "2020-02-16", "2020-02-29"),  # Feb which has 29th
            ("2021-02-01", "2021-02-01", "2021-02-15"),
            ("2021-02-15", "2021-02-01", "2021-02-15"),
            ("2021-02-16", "2021-02-16", "2021-02-28"),
            ("2021-02-28", "2021-02-16", "2021-02-28"),
        ],
    )
    def test_get_amount(self, time_entry_date, expected_start, expected_end):
        start, end = get_payroll_period(datetime.strptime(time_entry_date, "%Y-%m-%d"))
        assert start == datetime.strptime(expected_start, "%Y-%m-%d").date()
        assert end == datetime.strptime(expected_end, "%Y-%m-%d").date()

    @pytest.mark.parametrize(
        "time_report_data",
        [
            ("22/11/2016", "5", "1", "A"),
            ("23/11/2016", "5", "4", "B"),
            ("24/11/2016", "5", "4", "B"),
            ("25/11/2016", "5", "4", "B"),
            ("14/12/2016", "7.5", "1", "A"),
            ("23/02/2021", "4", "2", "B"),
            ("23/02/2020", "4", "2", "B"),
        ],
    )
    def test_update_payroll_record(self, time_report_data):
        serializer = TimeRecordSerializer(
            data={
                "entry_date": time_report_data[0],
                "hours": time_report_data[1],
                "employee_id": time_report_data[2],
                "job_group": time_report_data[3],
            }
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        update_payroll_record(instance)

        payroll_set = Payroll.objects.all()
        assert len(payroll_set) == 1
        payroll_set[0].employee_id = instance.employee_id
        payroll_set[0].amount = instance.get_paid_amount()
        time_report_date = datetime.strptime(time_report_data[0], "%d/%m/%Y")

        _, last_date = monthrange(time_report_date.year, time_report_date.month)
        if time_report_date.day > 15:
            payroll_set[0].start_date.day == 16
            payroll_set[0].start_date.day == last_date
        else:
            payroll_set[0].start_date.day == 1
            payroll_set[0].start_date.day == 15
