from django.urls import path

from users.apps import UsersConfig
from users.views.ssr_views import LoginView, LogoutView, RegisterView, UserProfile, email_verification, \
    password_recovery, \
    UserListView, user_toggle_activity, UserDitailView, UserDeleteView, UserUpdateView, ChangePasswordView

app_name = UsersConfig.name

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('user/<int:pk>/', UserDitailView.as_view(), name='user'),
    path('profile/', UserProfile.as_view(), name='profile'),
    path('user/<int:pk>/update/', UserUpdateView.as_view(), name='user_update'),
    path('user/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('verification/', email_verification, name='verification'),
    path('recovery/', password_recovery, name='recovery'),
    path('list/', UserListView.as_view(), name='users_list'),
    path('user/activity/<int:pk>/', user_toggle_activity, name='user_activity'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
]
