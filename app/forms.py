import re

from django import forms

from .models import Cliente


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
