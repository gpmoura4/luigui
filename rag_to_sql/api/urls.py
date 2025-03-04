from django.urls import path, include

from . import views


urlpatterns = [
    path('databases/',  views.DatabaseList.as_view() ),
    path('databases/<int:pk>', views.DatabaseDetail.as_view()),
    path('databases/<int:database>/tables/',  views.TableList.as_view() ),
    path('databases/<int:database>/tables/<int:pk>/',  views.TableDetail.as_view() ),
    path('databases/<int:database>/question',  views.QuestionAnswerList.as_view() ),
]


