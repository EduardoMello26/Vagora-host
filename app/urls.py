from django.urls import path

from .views import *

urlpatterns = [
    path('', IndexView.as_view(), name='login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('clientes/novo/', ClienteCreateView.as_view(), name='cliente_create'),
    path('clientes/', ClienteListView.as_view(), name='cliente_list'),
    path('clientes/<int:cliente_id>/editar/', ClienteUpdateView.as_view(), name='cliente_edit'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('contato/', ContatoView.as_view(), name='contato'),
]
