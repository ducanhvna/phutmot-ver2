from django.urls import path
from .views import (
    FetchSettingView,
    AddUserView,
    FetchProfileView,
    EditProfileView,
    CheckUsernameView,
    FetchPostsView,
    FetchStoryView,
    AddPostView,
    FetchCommentsView,
    LikePostView,
    DislikePostView,
    CreateStoryView,
    FetchRandomRoomsView,
    FetchPostByUserView
)


app_name = "bot_manager"


urlpatterns = [
    path('fetchSetting/', FetchSettingView.as_view(), name='fetch_setting'),
    path('addUser', AddUserView.as_view(), name='add_user'),
    path('fetchProfile', FetchProfileView.as_view(), name='fetch_profile'),
    path('editProfile', EditProfileView.as_view(), name='edit_profile'),
    path('checkUsername', CheckUsernameView.as_view(), name='check_username'),
    path('fetchPosts', FetchPostsView.as_view(), name='fetch_posts'),
    path('fetchStory', FetchStoryView.as_view(), name='fetch_story'),
    path('addPost', AddPostView.as_view(), name='addPost'),
    path('fetchComments', FetchCommentsView.as_view(), name='fetchComments'),
    path('likePost', LikePostView.as_view(), name='likePost'),
    path('dislikePost', DislikePostView.as_view(), name='dislikePost'),
    path('createStory', CreateStoryView.as_view(), name='createStory'),
    path('fetchRandomRooms', FetchRandomRoomsView.as_view(), name='fetchRandomRooms'),
    path('fetchPostByUser', FetchPostByUserView.as_view, name='fetchPostByUser'),
]
