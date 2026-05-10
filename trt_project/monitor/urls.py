from django.urls import path
from . import views

urlpatterns = [
    path('login/',                     views.login_view,    name='login'),
    path('logout/',                    views.logout_view,   name='logout'),
    path('register/',                  views.register_view, name='register'),
    path('guest/',                     views.guest_login,   name='guest_login'),
    path('',                           views.home,          name='home'),
    path('portfolio/',                 views.stock_list,    name='stock_list'),
    path('portfolio/add/',             views.stock_add,     name='stock_add'),
    path('portfolio/<int:pk>/remove/',     views.stock_remove,         name='stock_remove'),
    path('portfolio/<int:pk>/toggle/',     views.stock_toggle,         name='stock_toggle'),
    path('portfolio/<int:pk>/thresholds/', views.stock_set_thresholds, name='stock_set_thresholds'),
    path('ativo/<path:symbol_yf>/',    views.stock_detail,  name='stock_detail'),
    path('settings/',                  views.settings_view, name='settings'),
    path('monitor/run/',               views.run_monitor,   name='run_monitor'),
    path('settings/test-email/',       views.test_email,    name='test_email'),
    path('alerts/',                    views.alert_history, name='alert_history'),
    path('search/', views.search, name='search'),
    path('search/suggest/', views.search_suggest, name='search_suggest'),
]