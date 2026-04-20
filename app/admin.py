from django.contrib import admin
from .models import Avaria, Cliente, Pagamento, Tarifa, Ticket, Vaga, Veiculo


# Register your models here.
admin.site.register(Cliente)
admin.site.register(Veiculo)


@admin.register(Vaga)
class VagaAdmin(admin.ModelAdmin):
	list_display = ("numero", "tipo", "status")
	list_filter = ("tipo", "status")
	search_fields = ("numero",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
	list_display = ("id", "cliente", "veiculo", "vaga", "operador", "status", "entrada", "saida")
	list_filter = ("status", "entrada")
	search_fields = ("cliente__nome", "cliente__cpf", "veiculo__placa", "operador__username", "operador__email")


admin.site.register(Pagamento)
admin.site.register(Tarifa)


@admin.register(Avaria)
class AvariaAdmin(admin.ModelAdmin):
	list_display = ("id", "veiculo", "operador", "registrado_em")
	list_filter = ("registrado_em",)
	search_fields = ("veiculo__placa", "operador__username", "descricao")
