from django.urls import path

from .views import *

urlpatterns = [
    path('', IndexView.as_view(), name='login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('contato/', ContatoView.as_view(), name='contato'),
]
