from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('connect_watson/', views.get_response, name="connect_watson"),
    path('authenticate_start_session_watson/', views.authenticate_start_session, name="authenticate_start_session_watson"),
    path('close_session_watson/',views.delete_session, name="close_session_watson"),
]