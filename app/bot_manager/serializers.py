from rest_framework import serializers
from .models import (
    Setting,
    Interest,
    ReportReason,
    DocumentType,
    Story,
    Like,
    Comment,
    Room
)  # Make sure to import the models
from .models import Post, PostContent, Chatuser


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


class ChatuserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chatuser
        fields = '__all__'


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostContent
        fields = ['id', 'post_id', 'content_type', 'content', 'thumbnail', 'created_at', 'updated_at']


class FeedSerializer(serializers.ModelSerializer):
    content = ContentSerializer(many=True, read_only=True)
    user = ChatuserSerializer(read_only=True)
    is_like = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'user_id', 'desc', 'comments_count', 'likes_count', 'created_at', 'updated_at', 'is_like', 'content', 'user']

    def __init__(self, *args, **kwargs):
        self.my_user_id = kwargs.pop('my_user_id', None)
        super().__init__(*args, **kwargs)

    def get_is_like(self, obj):
        return 1 if Like.objects.filter(user_id=self.my_user_id, post_id=obj.id).exists() else 0


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    user = ChatuserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user_id', 'post_id', 'desc', 'created_at', 'updated_at', 'user']


class CommonResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    message = serializers.CharField(max_length=255)


class RoomSerializer(serializers.ModelSerializer):
    admin = ChatuserSerializer(read_only=True)
    interests = InterestSerializer(many=True, read_only=True)
    roomUsers = ChatuserSerializer(many=True, read_only=True)
    userRoomStatus = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = [
            "id",
            "admin_id",
            "photo",
            "title",
            "desc",
            "interest_ids",
            "is_private",
            "is_join_request_enable",
            "total_member",
            "created_at",
            "updated_at",
            "userRoomStatus",
            "is_mute",
            "interests",
            "admin",
            "roomUsers",
        ]

    def get_userRoomStatus(self, obj):
        # Logic để trả về giá trị của userRoomStatus
        return obj.user_room_status if hasattr(obj, 'user_room_status') else 0
