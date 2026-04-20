from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


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
    valor_diaria = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Valor Diário")
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
        return f"{self.descricao} ({self.tipo_veiculo}) - {self.hora_inicio.strftime('%H:%M')} às {self.hora_fim.strftime('%H:%M')}"

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

    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, verbose_name="Veículo")
    vaga = models.ForeignKey(Vaga, on_delete=models.CASCADE, verbose_name="Vaga")
    operador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Operador")
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, verbose_name="Cliente")
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
        return f"Ticket {self.id} - {self.veiculo.placa} ({self.status})"

    def save(self, *args, **kwargs):
        self.full_clean()
        # Se o veiculo ainda nao tiver cliente, vincula automaticamente ao cliente do ticket.
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
