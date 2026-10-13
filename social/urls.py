from django.urls import path
from . import views

app_name = "social"

urlpatterns = [
    # 🔑 Authentication Endpoints (for 3D login.html)
    path("auth/password-login/", views.password_login, name="password_login"),
    path("auth/request-otp/", views.request_otp, name="request_otp"),
    path("auth/self-signup/", views.self_signup, name="self_signup"),
    path("auth/verify-otp/", views.verify_otp, name="verify_otp"),
    path("auth/set-credentials/", views.set_credentials, name="set_credentials"),

    # 📱 Social Feed & Posts
    path("", views.feed, name="feed"),
    path("post/<int:pk>/", views.post_detail, name="post_detail"),
    path("post/<int:pk>/like/", views.like_toggle, name="like_toggle"),
    path("post/<int:pk>/save/", views.save_toggle, name="save_toggle"),
    path("post/<int:pk>/comment/", views.add_comment_ajax, name="add_comment_ajax"),
    path("post/<int:pk>/likes/", views.post_likes_list, name="post_likes_list"),
    path("post/<int:pk>/delete/", views.delete_post, name="delete_post"),
    path("post/<int:pk>/share-dm/", views.share_post_dm, name="share_post_dm"),
    path("saved/", views.saved_posts, name="saved_posts"),

    # 💬 Comment Interactions (Replies, Likes, Delete)
    path("comment/<int:pk>/reply/", views.reply_comment_ajax, name="reply_comment_ajax"),
    path("comment/<int:pk>/like/", views.like_comment_ajax, name="like_comment_ajax"),
    path("comment/<int:pk>/delete/", views.delete_comment_ajax, name="delete_comment_ajax"),

    # 🎬 Reels
    path("reels/", views.reels_feed, name="reels_feed"),
    path("reels/create/", views.create_reel, name="create_reel"),
    path("reels/<int:pk>/like/", views.like_reel_api, name="like_reel_api"),

    # 📖 Stories & Highlights
    path("story/create/", views.create_story, name="create_story"),
    path("story/<int:pk>/view/", views.view_story_api, name="view_story_api"),
    path("story/<int:pk>/react/", views.react_story_api, name="react_story_api"),
    path("story/<int:pk>/viewers/", views.story_viewers_api, name="story_viewers_api"),
    path("highlight/create/", views.create_highlight, name="create_highlight"),

    # 👥 Follow System
    path("user/<str:username>/follow/", views.follow_toggle, name="follow_toggle"),
    path("user/<str:username>/followers/", views.followers_list, name="followers_list"),
    path("user/<str:username>/following/", views.following_list, name="following_list"),
    path("api/followers/<str:username>/", views.followers_list, name="api_followers_list"),
    path("api/following/<str:username>/", views.following_list, name="api_following_list"),

    # 🔔 Notifications
    path("notifications/", views.notifications_list_api, name="notifications_list_api"),
    path("notifications/read/", views.mark_notifications_read, name="mark_notifications_read"),
    path("api/notifications/", views.notifications_list_api, name="api_notifications_list"),
    path("api/notifications/read/", views.mark_notifications_read, name="api_mark_notifications_read"),

    # 🔍 Search & Discovery
    path("search/", views.search_api, name="search_api"),
    path("api/search/", views.search_api, name="api_search"),

    # 🛡️ Reporting
    path("report/", views.submit_report_api, name="submit_report_api"),
    path("api/report/", views.submit_report_api, name="api_submit_report"),

    # 📤 Share via DM
    path("api/share/dm/", views.share_post_dm, name="api_share_post_dm"),
    path("api/story/<int:pk>/react/", views.react_story_api, name="api_react_story"),
    path("api/story/<int:pk>/viewers/", views.story_viewers_api, name="api_story_viewers"),

    # 👤 User Profile
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("edit-profile/", views.edit_profile),
    path("profile/<str:username>/", views.profile_view, name="profile"),

    # 🧭 Explore & Messages
    path("explore/", views.explore, name="explore"),
    path("messages/", views.inbox, name="inbox"),
    path("inbox/", views.inbox),
    path("messages/<int:pk>/", views.conversation_detail, name="conversation_detail"),
    path("messages/start/<str:username>/", views.start_conversation, name="start_conversation"),
    path("messages/<int:pk>/send/", views.send_message_ajax, name="send_message_ajax"),
]