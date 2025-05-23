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
    schedulings = serializers.SerializerMethodField()
    total_minutes = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = '__all__'  # sẽ trả về tất cả trường của Employee + schedulings + total_minutes

    def get_schedulings(self, obj):
        # Hàm này sẽ không dùng nữa khi dùng join ngoài view
        return []

    def get_total_minutes(self, obj):
        # Hàm này sẽ không dùng nữa khi dùng join ngoài view
        return 0
