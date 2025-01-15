from rest_framework import serializers
from .models import (
    Setting,
    Interest,
    ReportReason,
    DocumentType,
)  # Make sure to import the models
from .models import User


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
    interests = serializers.SerializerMethodField()
    report_reasons = serializers.SerializerMethodField()
    document_type = serializers.SerializerMethodField()

    def get_interests(self, obj):
        interests = Interest.objects.all()
        return InterestSerializer(interests, many=True).data

    def get_report_reasons(self, obj):
        report_reasons = ReportReason.objects.all()
        return ReportReasonSerializer(report_reasons, many=True).data

    def get_document_type(self, obj):
        document_type = DocumentType.objects.all()
        return DocumentTypeSerializer(document_type, many=True).data

    class Meta:
        model = Setting
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
