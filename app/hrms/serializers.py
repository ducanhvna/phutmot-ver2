# myapp/serializers.py

from rest_framework import serializers
from .models import Employee, Scheduling


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class SchedulingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheduling
        fields = '__all__'


class EmployeeWithSchedulingSerializer(serializers.ModelSerializer):
    scheduling = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = '__all__'  # sẽ trả về tất cả trường của Employee + scheduling

    def get_scheduling(self, obj):
        schedulings = Scheduling.objects.filter(
            employee_code=obj.employee_code,
            start_date=obj.start_date,
            end_date=obj.end_date
        )
        return SchedulingSerializer(schedulings, many=True).data
