import re

from django import forms
from django.utils import timezone

from .models import Avaria, Cliente, Pagamento, Tarifa, Ticket, Vaga, Veiculo


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nome", "cpf", "telefone", "tipo"]
        labels = {
            "nome": "Nome",
            "cpf": "CPF",
            "telefone": "Telefone",
            "tipo": "Tipo",
        }
        widgets = {
            "nome": forms.TextInput(attrs={"placeholder": "nome completo"}),
            "cpf": forms.TextInput(attrs={"placeholder": "000.000.000-00"}),
            "telefone": forms.TextInput(attrs={"placeholder": "(00) 00000-0000"}),
            "tipo": forms.Select(),
        }

    def clean_cpf(self):
        cpf = self.cleaned_data["cpf"]
        apenas_numeros = re.sub(r"\D", "", cpf)

        if len(apenas_numeros) != 11:
            raise forms.ValidationError("CPF deve conter 11 digitos.")

        cpf_formatado = (
            f"{apenas_numeros[0:3]}.{apenas_numeros[3:6]}."
            f"{apenas_numeros[6:9]}-{apenas_numeros[9:11]}"
        )
        return cpf_formatado

    def clean_telefone(self):
        telefone = self.cleaned_data.get("telefone", "")
        return telefone.strip() or None


class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = ["cliente", "placa", "modelo", "cor"]
        labels = {
            "cliente": "Cliente",
            "placa": "Placa",
            "modelo": "Modelo",
            "cor": "Cor",
        }
        widgets = {
            "cliente": forms.Select(),
            "placa": forms.TextInput(attrs={"placeholder": "AAA0A00"}),
            "modelo": forms.TextInput(attrs={"placeholder": "modelo do veículo"}),
            "cor": forms.TextInput(attrs={"placeholder": "cor do veículo"}),
        }

    def clean_placa(self):
        placa = self.cleaned_data["placa"].strip().upper()
        return placa

    def clean_modelo(self):
        modelo = self.cleaned_data.get("modelo", "")
        return modelo.strip() or None

    def clean_cor(self):
        cor = self.cleaned_data.get("cor", "")
        return cor.strip() or None


class TarifaForm(forms.ModelForm):
    class Meta:
        model = Tarifa
        fields = ["descricao", "tipo_veiculo", "hora_inicio", "hora_fim", "valor_hora", "valor_diaria"]
        labels = {
            "descricao": "Descrição",
            "tipo_veiculo": "Tipo de Veículo",
            "hora_inicio": "Hora Início",
            "hora_fim": "Hora Fim",
            "valor_hora": "Valor por Hora",
            "valor_diaria": "Valor Diário",
        }
        widgets = {
            "descricao": forms.TextInput(attrs={"placeholder": "tarifa padrão"}),
            "tipo_veiculo": forms.Select(),
            "hora_inicio": forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
            "hora_fim": forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
            "valor_hora": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "valor_diaria": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo_veiculo = cleaned_data.get("tipo_veiculo")
        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fim = cleaned_data.get("hora_fim")

        if not tipo_veiculo or not hora_inicio or not hora_fim:
            return cleaned_data

        tarifas = Tarifa.objects.exclude(pk=self.instance.pk)
        if tipo_veiculo == "todos":
            tarifas = tarifas.filter(
                hora_inicio__lt=hora_fim,
                hora_fim__gt=hora_inicio,
            )
        else:
            tarifas = tarifas.filter(
                hora_inicio__lt=hora_fim,
                hora_fim__gt=hora_inicio,
                tipo_veiculo__in=[tipo_veiculo, "todos"],
            )

        if tarifas.exists():
            raise forms.ValidationError("Ja existe uma tarifa que conflita com essa faixa de horário para o tipo de veículo informado.")

        return cleaned_data


class AvariaForm(forms.ModelForm):
    class Meta:
        model = Avaria
        fields = ["veiculo", "descricao"]
        labels = {
            "veiculo": "Veículo",
            "descricao": "Descrição",
        }
        widgets = {
            "veiculo": forms.Select(),
            "descricao": forms.Textarea(attrs={"placeholder": "descreva a avaria", "rows": 5}),
        }


class VagaQuantidadeForm(forms.Form):
    quantidade = forms.IntegerField(min_value=1, max_value=500, label="Quantidade de vagas")


class TicketEmissaoForm(forms.Form):
    vaga = forms.ModelChoiceField(
        queryset=Vaga.objects.none(),
        label="Vaga",
        empty_label="Selecione uma vaga",
    )
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.none(),
        label="Cliente",
        required=False,
        empty_label="Nao informar cliente",
    )
    veiculo = forms.ModelChoiceField(
        queryset=Veiculo.objects.none(),
        label="Veiculo",
        required=False,
        empty_label="Nao informar veiculo",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vaga"].queryset = Vaga.objects.filter(status="livre").order_by("numero")
        self.fields["cliente"].queryset = Cliente.objects.all().order_by("nome")
        self.fields["veiculo"].queryset = Veiculo.objects.select_related("cliente").all().order_by("placa")

    def clean(self):
        cleaned_data = super().clean()
        cliente = cleaned_data.get("cliente")
        veiculo = cleaned_data.get("veiculo")

        if cliente and veiculo and veiculo.cliente_id and veiculo.cliente_id != cliente.id:
            raise forms.ValidationError("O veiculo selecionado nao pertence ao cliente informado.")

        return cleaned_data


class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = ["tarifa", "forma_pagamento"]
        labels = {
            "tarifa": "Tarifa",
            "forma_pagamento": "Forma de Pagamento",
        }
        widgets = {
            "tarifa": forms.Select(),
            "forma_pagamento": forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        agora = timezone.localtime(timezone.now()).time()
        tarifas_ativas = Tarifa.objects.filter(hora_inicio__lte=agora, hora_fim__gt=agora).order_by("tipo_veiculo", "descricao")
        self.fields["tarifa"].queryset = tarifas_ativas

    def clean_tarifa(self):
        tarifa = self.cleaned_data["tarifa"]
        agora = timezone.localtime(timezone.now()).time()

        if not Tarifa.objects.filter(pk=tarifa.pk, hora_inicio__lte=agora, hora_fim__gt=agora).exists():
            raise forms.ValidationError("A tarifa selecionada nao esta ativa neste horario.")

        return tarifa


class RelatorioFinanceiroForm(forms.Form):
    data_inicio = forms.DateField(
        label="Data inicial",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    data_fim = forms.DateField(
        label="Data final",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get("data_inicio")
        data_fim = cleaned_data.get("data_fim")

        if data_inicio and data_fim and data_inicio > data_fim:
            raise forms.ValidationError("A data inicial nao pode ser maior que a data final.")

        return cleaned_data
