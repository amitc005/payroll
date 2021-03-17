from drf_yasg import openapi
from rest_framework import serializers

from api.constants import JobGroup
from api.models import FileIDRecord
from api.models import Payroll
from api.models import TimeReport
from api.utils import get_time_record_from_file
from api.utils import get_timerecord_file_id
from api.utils import update_payroll_record
from api.utils import validate_time_report_file


class TimeRecordFileSerializer(serializers.Serializer):
    file = serializers.FileField()

    class Meta:
        swagger_schema_fields = {"type": openapi.TYPE_OBJECT, "properties": {}}

    def validate_file(self, file):
        valid, error_msg = validate_time_report_file(file)
        if not valid:
            raise serializers.ValidationError(error_msg)
        return file

    def save(self):
        for data in get_time_record_from_file(self.validated_data["file"]):
            serializer = TimeRecordSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            time_record = serializer.save()
            update_payroll_record(time_record)

        file_id = get_timerecord_file_id(self.validated_data["file"].name)
        FileIDRecord.objects.create(file_id=file_id)


class TimeRecordSerializer(serializers.ModelSerializer):
    entry_date = serializers.DateField(input_formats=["%d/%m/%Y"])

    class Meta:
        model = TimeReport
        fields = "__all__"


class PayrollSerializer(serializers.ModelSerializer):
    pay_period = serializers.SerializerMethodField()
    amount_paid = serializers.SerializerMethodField()

    class Meta:
        model = Payroll
        fields = [
            "employee_id",
            "amount_paid",
            "amount",
            "pay_period",
            "start_date",
            "end_date",
            "total_hours",
            "job_group",
        ]
        extra_kwargs = {
            "start_date": {"write_only": True},
            "end_date": {"write_only": True},
            "amount": {"read_only": True},
        }
        swagger_schema_fields = {
            "type": openapi.TYPE_OBJECT,
            "title": "payroll_report",
            "properties": {
                "employee_reports": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "employee_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "amount_paid": openapi.Schema(type=openapi.TYPE_STRING),
                            "pay_period": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "start_date": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format=openapi.FORMAT_DATE,
                                    ),
                                    "end_date": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format=openapi.FORMAT_DATE,
                                    ),
                                },
                            ),
                        },
                    ),
                )
            },
            "required": [],
        }

    def create(self, validated_data):
        validated_data["amount"] = (
            validated_data["total_hours"]
            * JobGroup.HOURLY_PAY.value[validated_data["job_group"]]
        )
        if validated_data["total_hours"] > 60:
            over_time = validated_data["total_hours"] - 60
            validated_data["amount"] += (
                over_time * JobGroup.OVERTIME_PAY.value[validated_data["job_group"]]
            )

        return Payroll.objects.create(**validated_data)

    def update(self, instance, validated_data):
        current_hours = validated_data["total_hours"] - instance.total_hours
        validated_data["amount"] = instance.amount
        validated_data["amount"] += (
            current_hours * JobGroup.HOURLY_PAY.value[instance.job_group]
        )

        if instance.total_hours > 60:
            validated_data["amount"] += (
                current_hours * JobGroup.OVERTIME_PAY.value[instance.job_group]
            )

        elif validated_data["total_hours"] > 60:
            over_time_hours = (validated_data["total_hours"]) - 60
            validated_data["amount"] += (
                over_time_hours * JobGroup.OVERTIME_PAY.value[instance.job_group]
            )

        instance.total_hours = validated_data["total_hours"]
        instance.amount = validated_data["amount"]
        instance.save()
        return instance

    def get_pay_period(self, obj):
        return {"start_date": obj.start_date, "end_date": obj.end_date}

    def get_amount_paid(self, obj):
        return "${:,.2f}".format(obj.amount)
