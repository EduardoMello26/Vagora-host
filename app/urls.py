from django.urls import path

from .views import *

urlpatterns = [
    path('', IndexView.as_view(), name='login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('clientes/novo/', ClienteCreateView.as_view(), name='cliente_create'),
    path('clientes/', ClienteListView.as_view(), name='cliente_list'),
    path('clientes/<int:cliente_id>/editar/', ClienteUpdateView.as_view(), name='cliente_edit'),
    path('clientes/<int:cliente_id>/excluir/', ClienteDeleteView.as_view(), name='cliente_delete'),
    path('tarifas/novo/', TarifaCreateView.as_view(), name='tarifa_create'),
    path('tarifas/', TarifaListView.as_view(), name='tarifa_list'),
    path('tarifas/<int:tarifa_id>/editar/', TarifaUpdateView.as_view(), name='tarifa_edit'),
    path('tarifas/<int:tarifa_id>/excluir/', TarifaDeleteView.as_view(), name='tarifa_delete'),
    path('veiculos/novo/', VeiculoCreateView.as_view(), name='veiculo_create'),
    path('veiculos/', VeiculoListView.as_view(), name='veiculo_list'),
    path('veiculos/<int:veiculo_id>/editar/', VeiculoUpdateView.as_view(), name='veiculo_edit'),
    path('veiculos/<int:veiculo_id>/excluir/', VeiculoDeleteView.as_view(), name='veiculo_delete'),
    path('tickets/novo/', TicketCreateView.as_view(), name='ticket_create'),
    path('tickets/', TicketListView.as_view(), name='ticket_list'),
    path('tickets/<int:ticket_id>/pdf/', TicketPdfView.as_view(), name='ticket_pdf'),
    path('pagamentos/<int:ticket_id>/novo/', PagamentoCreateView.as_view(), name='pagamento_create'),
    path('vagas/', VagaListView.as_view(), name='vaga_list'),
    path('vagas/<int:vaga_id>/alternar/', VagaToggleView.as_view(), name='vaga_toggle'),
    path('vagas/<int:vaga_id>/excluir/', VagaDeleteView.as_view(), name='vaga_delete'),
    path('vagas/excluir-todas/', VagaDeleteAllView.as_view(), name='vaga_delete_all'),
    path('avarias/novo/', AvariaCreateView.as_view(), name='avaria_create'),
    path('avarias/', AvariaListView.as_view(), name='avaria_list'),
    path('avarias/<int:avaria_id>/editar/', AvariaUpdateView.as_view(), name='avaria_edit'),
    path('avarias/<int:avaria_id>/excluir/', AvariaDeleteView.as_view(), name='avaria_delete'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('contato/', ContatoView.as_view(), name='contato'),
]
