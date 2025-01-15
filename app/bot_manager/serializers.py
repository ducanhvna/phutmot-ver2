from rest_framework import serializers
from .models import (
    Setting,
    Interest,
    ReportReason,
    DocumentType,
)  # Make sure to import the models
from .models import Post, PostContent, Room, User


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
        fields = [
            "id",
            "app_name",
            "setRoomUsersLimit",
            "minute_limit_in_creating_story",
            "minute_limit_in_choosing_video_for_story",
            "minute_limit_in_choosing_video_for_post",
            "max_images_can_be_uploaded_in_one_post",
            "ad_banner_android",
            "ad_interstitial_android",
            "ad_banner_iOS",
            "ad_interstitial_iOS",
            "is_admob_on",
            "created_at",
            "updated_at",
            "interests",
            "report_reasons",
            "document_type",
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostContent
        fields = ['id', 'post_id', 'content_type', 'content', 'thumbnail', 'created_at', 'updated_at']


class FeedSerializer(serializers.ModelSerializer):
    content = ContentSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user_id', 'desc', 'comments_count', 'likes_count', 'created_at', 'updated_at', 'is_like', 'content', 'user']


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'title', 'desc']
