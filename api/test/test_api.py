import io
from decimal import Decimal
from http import HTTPStatus

import pytest
from rest_framework.test import APIClient

from api.messages import FILE_ID_ALREADY_PROCCED
from api.messages import INVALID_FILE_NAME
from api.models import FileIDRecord
from api.models import TimeReport


@pytest.mark.django_db
class TestTimeRecordAPI:
    @pytest.fixture(autouse=True)
    def set_up(self):
        self.client = APIClient()
        self.file_name = "time-report-%d.csv"

    def test_upload_time_record_api_with_invalid_file(self):
        file_str = """
        date,hours worked,employee id,job group
        14/11/2016,7.5,1,A
        9/11/2016,4,2,B
        """
        file_name = "invalid_name"
        with io.BytesIO(file_str.encode()) as upload_file:
            response = self.client.post(
                "/time_reports/", data={"file": (upload_file, file_name)}
            )
            assert response.status_code == HTTPStatus.BAD_REQUEST
            res_data = response.json()
            assert "file" in res_data
            assert isinstance(res_data["file"], list)
            assert INVALID_FILE_NAME in res_data["file"]

    def test_upload_time_record_api_with_existed_file_id(self):
        file_id = 1
        FileIDRecord.objects.create(file_id=file_id)

        file_str = """
        date,hours worked,employee id,job group
        14/11/2016,7.5,1,A
        9/11/2016,4,2,B
        """
        file_name = self.file_name % file_id
        with io.BytesIO(file_str.encode()) as upload_file:
            upload_file.name = file_name
            response = self.client.post("/time_reports/", data={"file": upload_file})
            assert response.status_code == HTTPStatus.BAD_REQUEST
            res_data = response.json()
            assert "file" in res_data
            assert isinstance(res_data["file"], list)
            assert FILE_ID_ALREADY_PROCCED in res_data["file"]

    def test_upload_time_record_api(self):
        file_id = 1
        file_str = "date,hours worked,employee id,job group"
        file_str += "\n4/11/2016,7.5,1,A"
        file_str += "\n9/11/2016,4,2,B"
        file_name = self.file_name % file_id
        with io.BytesIO(file_str.encode()) as upload_file:
            upload_file.name = file_name
            response = self.client.post("/time_reports/", data={"file": upload_file})
            assert response.status_code == HTTPStatus.CREATED

        time_record_set = TimeReport.objects.all()
        assert len(time_record_set) == 2

    def test_payroll_report_get_api(self):
        file_id = 1
        file_str = "date,hours worked,employee id,job group"
        file_str += "\n4/11/2016,7.5,1,A"
        file_str += "\n9/11/2016,4,2,B"
        file_name = self.file_name % file_id
        with io.BytesIO(file_str.encode()) as upload_file:
            upload_file.name = file_name
            response = self.client.post("/time_reports/", data={"file": upload_file})
            assert response.status_code == HTTPStatus.CREATED

        time_record_set = TimeReport.objects.all()
        assert len(time_record_set) == 2

        response = self.client.get("/payroll_report/employee_reports", format="json")
        assert response.status_code == HTTPStatus.OK
        res_data = response.json()
        assert "payroll_report" in res_data
        assert "employee_reports" in res_data["payroll_report"]
        assert isinstance(res_data["payroll_report"]["employee_reports"], list)
        assert len(res_data["payroll_report"]["employee_reports"]) == 2

    def test_time_record_api_with_multiple_records_and_check_employee_paid_amount(self):
        file_id = 1
        file_str = "date,hours worked,employee id,job group"

        file_str += "\n4/11/2016,7.5,1,A"
        file_str += "\n5/11/2016,7.5,1,A"
        file_str += "\n14/11/2016,5.5,1,A"
        total_emp_a = 410

        file_str += "\n9/11/2016,4,2,B"
        file_str += "\n8/11/2016,4,2,B"
        file_str += "\n16/11/2016,4,2,B"
        total_emp_b = 360

        file_name = self.file_name % file_id
        with io.BytesIO(file_str.encode()) as upload_file:
            upload_file.name = file_name
            response = self.client.post("/time_reports/", data={"file": upload_file})
            assert response.status_code == HTTPStatus.CREATED

        time_record_set = TimeReport.objects.all()
        assert len(time_record_set) == 6

        response = self.client.get("/payroll_report/employee_reports", format="json")
        assert response.status_code == HTTPStatus.OK
        res_data = response.json()
        assert "payroll_report" in res_data
        assert "employee_reports" in res_data["payroll_report"]
        assert isinstance(res_data["payroll_report"]["employee_reports"], list)
        assert len(res_data["payroll_report"]["employee_reports"]) == 3

        total_pay = {1: 0, 2: 0}
        for report in res_data["payroll_report"]["employee_reports"]:
            total_pay[report["employee_id"]] += Decimal(report["amount_paid"][1:])

        assert total_pay[1] == total_emp_a
        assert total_pay[2] == total_emp_b

    def test_add_time_report_with_over_time_hours(self):
        file_id = 1
        file_str = "date,hours worked,employee id,job group"

        file_str += "\n1/11/2016,7.5,1,A"
        file_str += "\n2/11/2016,7.5,1,A"
        file_str += "\n3/11/2016,7.5,1,A"
        file_str += "\n4/11/2016,7.5,1,A"
        file_str += "\n5/11/2016,7.5,1,A"
        file_str += "\n6/11/2016,7.5,1,A"
        file_str += "\n7/11/2016,7.5,1,A"
        file_str += "\n8/11/2016,7.5,1,A"
        file_str += "\n9/11/2016,7.5,1,A"
        file_str += "\n10/11/2016,7.5,1,A"
        file_str += "\n11/11/2016,7.5,1,A"
        file_str += "\n12/11/2016,7.5,1,A"
        file_str += "\n13/11/2016,7.5,1,A"
        file_str += "\n14/11/2016,7.5,1,A"
        file_str += "\n15/11/2016,7.5,1,A"

        file_name = self.file_name % file_id
        with io.BytesIO(file_str.encode()) as upload_file:
            upload_file.name = file_name
            response = self.client.post("/time_reports/", data={"file": upload_file})
            assert response.status_code == HTTPStatus.CREATED

        time_record_set = TimeReport.objects.all()
        assert len(time_record_set) == 6

        response = self.client.get("/payroll_report/employee_reports", format="json")
        assert response.status_code == HTTPStatus.OK
