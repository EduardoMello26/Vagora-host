from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from decimal import Decimal, ROUND_CEILING
import math


class Cliente(models.Model):
    TIPO_CHOICES = [
        ("avulso", "Avulso"),
        ("mensalista", "Mensalista"),
    ]

    nome = models.CharField(max_length=100, verbose_name="Nome")
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    telefone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default="avulso", verbose_name="Tipo")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        db_table = "cliente"
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return f"{self.nome} - {self.cpf}"


class Veiculo(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cliente")
    placa = models.CharField(max_length=10, unique=True, verbose_name="Placa")
    modelo = models.CharField(max_length=80, null=True, blank=True, verbose_name="Modelo")
    cor = models.CharField(max_length=40, null=True, blank=True, verbose_name="Cor")

    class Meta:
        db_table = "veiculo"
        verbose_name = "Veículo"
        verbose_name_plural = "Veículos"

    def __str__(self):
        return f"{self.placa} ({self.modelo or '---'})"


class Vaga(models.Model):
    TIPO_CHOICES = [
        ("carro", "Carro"),
        ("moto", "Moto"),
        ("deficiente", "Deficiente"),
        ("idoso", "Idoso"),
    ]
    STATUS_CHOICES = [
        ("livre", "Livre"),
        ("ocupada", "Ocupada"),
    ]

    numero = models.PositiveIntegerField(unique=True, verbose_name="Número")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default="carro", verbose_name="Tipo")
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default="livre", verbose_name="Status")

    class Meta:
        db_table = "vaga"
        verbose_name = "Vaga"
        verbose_name_plural = "Vagas"
        ordering = ["numero"]

    def __str__(self):
        return f"Vaga {self.numero} ({self.tipo}) [{self.status}]"


class Tarifa(models.Model):
    TIPO_VEICULO_CHOICES = [
        ("carro", "Carro"),
        ("moto", "Moto"),
        ("todos", "Todos"),
    ]

    descricao = models.CharField(max_length=100, verbose_name="Descrição")
    valor_hora = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Valor por Hora")
    PERIOD_CHOICES = [
        ("hora", "Hora"),
        ("dia", "Dia (valor fixo)"),
        ("semana", "Semana (valor fixo)"),
        ("mes", "Mês (valor fixo)"),
    ]
    periodo = models.CharField(max_length=10, choices=PERIOD_CHOICES, default="hora", verbose_name="Período")
    valor_fixo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Valor Fixo")
    tipo_veiculo = models.CharField(max_length=5, choices=TIPO_VEICULO_CHOICES, default="todos", verbose_name="Tipo de Veículo")
    hora_inicio = models.TimeField(verbose_name="Hora Início")
    hora_fim = models.TimeField(verbose_name="Hora Fim")

    class Meta:
        db_table = "tarifa"
        verbose_name = "Tarifa"
        verbose_name_plural = "Tarifas"
        ordering = ["hora_inicio", "tipo_veiculo", "descricao"]

    def clean(self):
        super().clean()
        if self.hora_inicio and self.hora_fim and self.hora_inicio >= self.hora_fim:
            raise ValidationError({"hora_fim": "A hora final deve ser maior que a hora inicial."})

    def __str__(self):
        return f"{self.descricao} ({self.tipo_veiculo}) - {self.hora_inicio.strftime('%H:%M')} às {self.hora_fim.strftime('%H:%M')} ({self.get_periodo_display()})"

    @classmethod
    def obter_tarifa_por_horario(cls, tipo_veiculo, horario):
        hora_referencia = getattr(horario, "time", lambda: horario)()
        candidatas = cls.objects.filter(
            hora_inicio__lte=hora_referencia,
            hora_fim__gt=hora_referencia,
            tipo_veiculo__in=[tipo_veiculo, "todos"],
        ).annotate(
            prioridade_tipo=models.Case(
                models.When(tipo_veiculo=tipo_veiculo, then=models.Value(0)),
                default=models.Value(1),
                output_field=models.IntegerField(),
            )
        ).order_by("prioridade_tipo", "hora_inicio")
        return candidatas.first()


class Ticket(models.Model):
    STATUS_CHOICES = [
        ("aberto", "Aberto"),
        ("finalizado", "Finalizado"),
        ("cancelado", "Cancelado"),
    ]

    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Veículo")
    vaga = models.ForeignKey(Vaga, on_delete=models.CASCADE, verbose_name="Vaga")
    operador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Operador")
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Cliente")
    entrada = models.DateTimeField(auto_now_add=True, verbose_name="Entrada")
    saida = models.DateTimeField(null=True, blank=True, verbose_name="Saída")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="aberto", verbose_name="Status")

    class Meta:
        db_table = "ticket"
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"

    def clean(self):
        super().clean()
        if self.veiculo_id and self.cliente_id:
            if self.veiculo.cliente_id and self.veiculo.cliente_id != self.cliente_id:
                raise ValidationError({"cliente": "O cliente do ticket deve ser o mesmo cliente do veículo."})

    def __str__(self):
        placa = self.veiculo.placa if self.veiculo_id else "sem veiculo"
        return f"Ticket {self.id} - {placa} ({self.status})"

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.veiculo_id and self.cliente_id and self.veiculo.cliente_id is None:
            self.veiculo.cliente = self.cliente
            self.veiculo.save(update_fields=["cliente"])
        super().save(*args, **kwargs)


class Pagamento(models.Model):
    FORMA_PAGAMENTO_CHOICES = [
        ("dinheiro", "Dinheiro"),
        ("cartao_debito", "Cartão Débito"),
        ("cartao_credito", "Cartão Crédito"),
        ("pix", "PIX"),
    ]

    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, verbose_name="Ticket")
    tarifa = models.ForeignKey(Tarifa, on_delete=models.CASCADE, verbose_name="Tarifa")
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Total")
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO_CHOICES, verbose_name="Forma de Pagamento")
    pago_em = models.DateTimeField(auto_now_add=True, verbose_name="Pago em")

    class Meta:
        db_table = "pagamento"
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"

    def __str__(self):
        return f"Pagamento {self.id} - {self.ticket}"

    @staticmethod
    def calcular_valor(ticket, tarifa, saida):
        duracao = saida - ticket.entrada
        total_seconds = int(duracao.total_seconds())

        # If tarifa is by hour (legacy), keep existing behavior (hourly + optional daily)
        if tarifa.periodo == "hora":
            horas_decimais = Decimal(str(total_seconds)) / Decimal("3600")
            horas_cobradas = int(horas_decimais.to_integral_value(rounding=ROUND_CEILING))
            horas_cobradas = max(horas_cobradas, 1)

            # Always charge by hours using valor_hora (no diaria fallback)
            total = Decimal(horas_cobradas) * tarifa.valor_hora
            return total.quantize(Decimal("0.01"))

        # For fixed-period tariffs (day/week/month), charge by whole periods (ceiling)
        period_seconds = {
            "dia": 86400,
            "semana": 604800,
            "mes": 2592000,  # 30 days approximation
        }.get(tarifa.periodo)

        if period_seconds and tarifa.valor_fixo is not None:
            periods = math.ceil(total_seconds / period_seconds)
            periods = max(periods, 1)
            total = Decimal(periods) * tarifa.valor_fixo
            return total.quantize(Decimal("0.01"))

        # Fallback to hourly calculation if configuration incomplete
        horas_decimais = Decimal(str(total_seconds)) / Decimal("3600")
        horas_cobradas = int(horas_decimais.to_integral_value(rounding=ROUND_CEILING))
        horas_cobradas = max(horas_cobradas, 1)
        total = Decimal(horas_cobradas) * tarifa.valor_hora
        return total.quantize(Decimal("0.01"))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.ticket.status != "finalizado":
            self.ticket.status = "finalizado"
            if self.ticket.saida is None:
                self.ticket.saida = self.pago_em
            self.ticket.save(update_fields=["status", "saida"])

        if self.ticket.vaga_id and self.ticket.vaga.status != "livre":
            self.ticket.vaga.status = "livre"
            self.ticket.vaga.save(update_fields=["status"])


class Avaria(models.Model):
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, verbose_name="Veículo")
    operador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Operador")
    descricao = models.TextField(verbose_name="Descrição")
    registrado_em = models.DateTimeField(auto_now_add=True, verbose_name="Registrado em")

    class Meta:
        db_table = "avaria"
        verbose_name = "Avaria"
        verbose_name_plural = "Avarias"

    def __str__(self):
        return f"Avaria {self.id} no veículo {self.veiculo.placa}"
