import re

from django import forms

from .models import Avaria, Cliente, Tarifa, Veiculo


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
