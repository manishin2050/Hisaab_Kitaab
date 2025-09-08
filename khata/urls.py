from django.urls import path
from khata import views
app_name = 'khata'
urlpatterns = [
   
    path('', views.home,name="home" ),
    path('add/', views.add_expense,name="add_expense" ),
    path('equalShareSplitor/', views.equalShareSplitor,name="equalShareSplitor" ),
    path('download/',views.download,name='download'),
    path('shopping/', views.shopping, name='shopping'),
    path('profile/', views.profile, name='profile'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.log_out, name='logout'),
]
