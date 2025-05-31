from django.urls import path, include
from rest_framework.authtoken import views as auth_views
from . import views

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('auth/login/', views.CustomAuthToken.as_view(), name='user-login'),
    path('auth/profile/', views.UserProfileView.as_view(), name='user-profile'),
    
    # Existing endpoints
    path('users/', views.UserList.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),
    path('databases/',  views.DatabaseList.as_view() ),
    path('databases/<int:pk>', views.DatabaseDetail.as_view()),
    path('databases/<int:database>/tables/',  views.TableList.as_view() ),
    path('databases/<int:database>/tables/<int:pk>/',  views.TableDetail.as_view() ),
    path('databases/<int:database>/question',  views.QuestionAnswerList.as_view() ),
    path('csrf/', views.get_csrf, name='csrf'),
    
    # New endpoints for database access management
    path('databases/<int:database>/access/', views.DatabaseAccessView.as_view(), name='database-access'),
    path('users/list/', views.UserListWithAccess.as_view(), name='user-list-with-access'),
]


