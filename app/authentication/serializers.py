from rest_framework import serializers


class EmployeeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    job_id = serializers.JSONField()
    department_id = serializers.JSONField()
    # code = serializers.CharField(max_length=255)
