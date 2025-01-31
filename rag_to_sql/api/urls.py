from django.urls import path, include

from . import views


urlpatterns = [
    path('databases/',  views.DatabaseList.as_view() ),
    path('databases/<int:pk>', views.DatabaseDetail.as_view()),
    path('databases/<int:db_id>/table/',  views.TableList.as_view() ),
    path('databases/<int:db_id>/table/<int:pk>/',  views.TableDetail.as_view() ),
]


