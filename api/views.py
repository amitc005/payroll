from http import HTTPStatus

from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from api.models import Payroll
from api.serializers import PayrollSerializer
from api.serializers import TimeRecordFileSerializer


class TimeRecordAPI(generics.CreateAPIView):
    parser_classes = (MultiPartParser,)
    serializer_class = TimeRecordFileSerializer

    @swagger_auto_schema()
    def create(self, request):
        upload_serializer = self.get_serializer(data=request.data)
        upload_serializer.is_valid(raise_exception=True)
        upload_serializer.save()
        return Response(status=HTTPStatus.CREATED)


class PayrollList(generics.ListAPIView):
    queryset = Payroll.objects.all()
    serializer_class = PayrollSerializer

    @swagger_auto_schema(
        operation_description="partial_update description override",
        responses={404: "slug not found"},
    )
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response({"payroll_report": {"employee_reports": serializer.data}})
