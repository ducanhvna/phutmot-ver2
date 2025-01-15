from rest_framework import serializers
from .models import (
    Setting,
    Interest,
    ReportReason,
    DocumentType,
)  # Make sure to import the models


class InterestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Interest
        fields = "__all__"


class ReportReasonSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReportReason
        fields = "__all__"


class DocumentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentType
        fields = "__all__"


class SettingSerializer(serializers.ModelSerializer):
    interests = InterestSerializer(many=True, read_only=True)
    report_reasons = ReportReasonSerializer(many=True, read_only=True)
    document_type = DocumentTypeSerializer(many=True, read_only=True)

    class Meta:
        model = Setting
        fields = "__all__"
