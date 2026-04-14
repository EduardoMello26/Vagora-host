import re

from django import forms

from .models import Cliente, Veiculo


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
