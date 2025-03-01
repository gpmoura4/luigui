from django.urls import path, include

from . import views


urlpatterns = [
    path('databases/',  views.DatabaseList.as_view() ),
    path('databases/<int:pk>', views.DatabaseDetail.as_view()),
    path('databases/<int:db_id>/tables/',  views.TableList.as_view() ),
    path('databases/<int:db_id>/tables/<int:pk>/',  views.TableDetail.as_view() ),
]


