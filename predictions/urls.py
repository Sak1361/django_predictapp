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
    path('calendar/', views.MonthCalendar.as_view(), name='month'),
    path('calendar/month/<int:year>/<int:month>/',
         views.MonthCalendar.as_view(), name='month'),
    path('calendar/week/', views.WeekCalendar.as_view(), name='week'),
    path('calendar/week/<int:year>/<int:month>/<int:day>/',
         views.WeekCalendar.as_view(), name='week'),
    path('calendar/week_with_schedule/', views.WeekWithScheduleCalendar.as_view(),
         name='week_with_schedule'),
    path('calendar/week_with_schedule/<int:year>/<int:month>/<int:day>/',
         views.WeekWithScheduleCalendar.as_view(),
         name='week_with_schedule'
         ),
    path('calendar/month_with_schedule/',
         views.MonthWithScheduleCalendar.as_view(), name='month_with_schedule'
         ),
    path('calendar/month_with_schedule/<int:year>/<int:month>/',
         views.MonthWithScheduleCalendar.as_view(), name='month_with_schedule'
         ),
    path('calendar/mycalendar/', views.MyCalendar.as_view(), name='mycalendar'),
    path('calendar/mycalendar/<int:year>/<int:month>/<int:day>/', views.MyCalendar.as_view(),
         name='mycalendar'
         ),
    path('calendar/month_with_forms/',
         views.MonthWithFormsCalendar.as_view(), name='month_with_forms'
         ),
    path('calendar/month_with_forms/<int:year>/<int:month>/',
         views.MonthWithFormsCalendar.as_view(), name='month_with_forms'
         ),

]
