from django.urls import path
from . import views

urlpatterns = [
    path('login/',                     views.login_view,    name='login'),
    path('logout/',                    views.logout_view,   name='logout'),
    path('guest/',                     views.guest_login,   name='guest_login'),
    path('',                           views.home,          name='home'),
    path('portfolio/',                 views.stock_list,    name='stock_list'),
    path('portfolio/add/',             views.stock_add,     name='stock_add'),
    path('portfolio/<int:pk>/remove/', views.stock_remove,  name='stock_remove'),
    path('portfolio/<int:pk>/toggle/', views.stock_toggle,  name='stock_toggle'),
    path('ativo/<path:symbol_yf>/',    views.stock_detail,  name='stock_detail'),
    path('settings/',                  views.settings_view, name='settings'),
    path('monitor/run/',               views.run_monitor,   name='run_monitor'),
    path('alerts/',                    views.alert_history, name='alert_history'),
    path('search/', views.search, name='search'),
]