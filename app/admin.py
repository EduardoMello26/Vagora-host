from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Usuario)
admin.site.register(Cliente)
admin.site.register(Veiculo)
admin.site.register(Vaga)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
	list_display = ("id", "cliente", "veiculo", "vaga", "operador", "status", "entrada", "saida")
	list_filter = ("status", "entrada")
	search_fields = ("cliente__nome", "cliente__cpf", "veiculo__placa", "operador__nome")


admin.site.register(Pagamento)
admin.site.register(Tarifa)
admin.site.register(Avaria)
