from django.urls import path,re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    re_path(r'connect_watson/', views.get_response, name="connect_watson"),
    re_path(r'authenticate_start_session_watson/', views.authenticate_start_session, name="authenticate_start_session_watson"),
    re_path(r'close_session_watson/',views.delete_session, name="close_session_watson"),
    path('second_page/',views.secondPage, name="second page"),
    path('results_page/',views.show_results, name="results page"),
]