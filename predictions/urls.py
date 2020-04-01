from django.urls import path
from . import views

app_name = 'predictions'
urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('predict/', views.predict_home, name='predict_home'),
    path('predict/result/', views.predict, name='predict'),
    path('tracking/', views.tracking_ship, name='search'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('top/', views.Top.as_view(), name='top'),
    path('user_detail/<int:pk>/', views.User_detail.as_view(), name='user_detail'),
    path('user_update/<int:pk>/', views.User_update.as_view(), name='user_update'),
    path('user_create/', views.User_create.as_view(), name='user_create'),
    path('user_create/done', views.User_create_done.as_view(),
         name='user_create_done'),
    path('user_create/complete/<token>/',
         views.User_create_complete.as_view(), name='user_create_complete'),
]
