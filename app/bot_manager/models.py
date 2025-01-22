from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=100)
    telegram_user_id = models.CharField(max_length=100, unique=True)


class Message(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Admin(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_name = models.CharField(max_length=255)
    user_password = models.CharField(max_length=255)
    user_type = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AdminNotification(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.IntegerField()
    post_id = models.IntegerField()
    desc = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class DocumentType(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FAQ(models.Model):
    id = models.AutoField(primary_key=True)
    faqs_type_id = models.IntegerField()
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FAQType(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=55)
    is_deleted = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FollowingList(models.Model):
    id = models.BigAutoField(primary_key=True)
    my_user_id = models.IntegerField()
    user_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Interest(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Like(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.IntegerField()
    post_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Post(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.IntegerField()
    desc = models.TextField(null=True, blank=True)
    tags = models.CharField(max_length=255, null=True, blank=True)
    comments_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PostContent(models.Model):
    id = models.BigAutoField(primary_key=True)
    post_id = models.IntegerField()
    content_type = models.IntegerField()
    content = models.CharField(max_length=255)
    thumbnail = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProfileVerification(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.IntegerField()
    selfie = models.CharField(max_length=255)
    document = models.CharField(max_length=255)
    document_type = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Report(models.Model):
    id = models.BigAutoField(primary_key=True)
    type = models.IntegerField(null=True, blank=True)
    room_id = models.IntegerField(null=True, blank=True)
    user_id = models.IntegerField(null=True, blank=True)
    post_id = models.IntegerField(null=True, blank=True)
    reason = models.CharField(max_length=255)
    desc = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ReportReason(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Room(models.Model):
    id = models.BigAutoField(primary_key=True)
    admin_id = models.IntegerField()
    photo = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255)
    desc = models.CharField(max_length=255)
    interest_ids = models.CharField(max_length=255)
    is_private = models.IntegerField()
    is_join_request_enable = models.IntegerField()
    total_member = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class RoomUser(models.Model):
    id = models.AutoField(primary_key=True)
    room_id = models.IntegerField()
    user_id = models.IntegerField()
    invited_by = models.IntegerField(null=True, blank=True)
    type = models.IntegerField()
    is_mute = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SavedNotification(models.Model):
    id = models.AutoField(primary_key=True)
    my_user_id = models.IntegerField(null=True, blank=True)
    user_id = models.IntegerField(null=True, blank=True)
    post_id = models.IntegerField(null=True, blank=True)
    room_id = models.IntegerField(null=True, blank=True)
    type = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Setting(models.Model):
    id = models.BigAutoField(primary_key=True)
    app_name = models.CharField(max_length=255)
    setRoomUsersLimit = models.IntegerField()
    minute_limit_in_creating_story = models.IntegerField(null=True, blank=True)
    minute_limit_in_choosing_video_for_story = models.IntegerField(null=True, blank=True)
    minute_limit_in_choosing_video_for_post = models.IntegerField(null=True, blank=True)
    max_images_can_be_uploaded_in_one_post = models.IntegerField(null=True, blank=True)
    ad_banner_android = models.CharField(max_length=255)
    ad_interstitial_android = models.CharField(max_length=255)
    ad_banner_iOS = models.CharField(max_length=255)
    ad_interstitial_iOS = models.CharField(max_length=255)
    is_admob_on = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Story(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    type = models.IntegerField(default=0)
    duration = models.FloatField(default=0)
    content = models.CharField(max_length=255)
    view_by_user_ids = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Page(models.Model):
    id = models.AutoField(primary_key=True)
    privacy = models.TextField(null=True, blank=True)
    termsofuse = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Chatuser(models.Model):
    id = models.BigAutoField(primary_key=True)
    identity = models.CharField(max_length=255)
    username = models.CharField(max_length=255, null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    bio = models.CharField(max_length=255, null=True, blank=True)
    interest_ids = models.CharField(max_length=255, null=True, blank=True)
    profile = models.CharField(max_length=255, null=True, blank=True)
    background_image = models.CharField(max_length=255, null=True, blank=True)
    is_push_notifications = models.IntegerField(default=1)
    is_invited_to_room = models.IntegerField(default=1)
    is_verified = models.IntegerField(default=0)
    is_block = models.IntegerField(default=0)
    block_user_ids = models.CharField(max_length=255, null=True, blank=True)
    following = models.IntegerField(null=True, blank=True)
    followers = models.IntegerField(null=True, blank=True)
    login_type = models.IntegerField()
    device_type = models.IntegerField()
    device_token = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    info = models.JSONField("Thông tin bổ sung", default=dict, blank=True)
