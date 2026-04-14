from django.shortcuts import render, redirect, get_object_or_404
from django.db.models.deletion import ProtectedError
from .models import *
from .forms import ClienteForm, VeiculoForm
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin

class IndexView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'index.html')

    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, 'Usuário ou senha inválidos.')
            return render(request, 'index.html', status=401)

        login(request, user)
        messages.success(request, 'Login realizado com sucesso.')
        return redirect('dashboard')


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'dashboard.html')


class ClienteCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = ClienteForm()
        return render(request, 'cliente/cliente_form.html', {'form': form, 'is_edit': False})

    def post(self, request):
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente cadastrado com sucesso.')
            return redirect('cliente_create')

        messages.error(request, 'Corrija os campos destacados e tente novamente.')
        return render(request, 'cliente/cliente_form.html', {'form': form, 'is_edit': False}, status=400)


class ClienteListView(LoginRequiredMixin, View):
    def get(self, request):
        clientes = Cliente.objects.all().order_by('nome')
        return render(request, 'cliente/cliente_list.html', {'clientes': clientes})


class ClienteUpdateView(LoginRequiredMixin, View):
    def get(self, request, cliente_id):
        cliente = get_object_or_404(Cliente, id=cliente_id)
        form = ClienteForm(instance=cliente)
        context = {'form': form, 'cliente': cliente, 'is_edit': True}
        return render(request, 'cliente/cliente_form.html', context)

    def post(self, request, cliente_id):
        cliente = get_object_or_404(Cliente, id=cliente_id)
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso.')
            return redirect('cliente_list')

        messages.error(request, 'Corrija os campos destacados e tente novamente.')
        context = {'form': form, 'cliente': cliente, 'is_edit': True}
        return render(request, 'cliente/cliente_form.html', context, status=400)


class ClienteDeleteView(LoginRequiredMixin, View):
    def get(self, request, cliente_id):
        cliente = get_object_or_404(Cliente, id=cliente_id)
        return render(request, 'cliente/cliente_confirm_delete.html', {'cliente': cliente})

    def post(self, request, cliente_id):
        cliente = get_object_or_404(Cliente, id=cliente_id)
        try:
            cliente.delete()
        except ProtectedError:
            messages.error(request, 'Nao foi possivel excluir este cliente porque ele possui veiculos ou tickets vinculados.')
            return redirect('cliente_list')

        messages.success(request, 'Cliente excluido com sucesso.')
        return redirect('cliente_list')


class VeiculoCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = VeiculoForm()
        return render(request, 'veiculo/veiculo_form.html', {'form': form, 'is_edit': False})

    def post(self, request):
        form = VeiculoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Veículo cadastrado com sucesso.')
            return redirect('veiculo_create')

        messages.error(request, 'Corrija os campos destacados e tente novamente.')
        return render(request, 'veiculo/veiculo_form.html', {'form': form, 'is_edit': False}, status=400)


class VeiculoListView(LoginRequiredMixin, View):
    def get(self, request):
        veiculos = Veiculo.objects.select_related('cliente').all().order_by('placa')
        return render(request, 'veiculo/veiculo_list.html', {'veiculos': veiculos})


class VeiculoUpdateView(LoginRequiredMixin, View):
    def get(self, request, veiculo_id):
        veiculo = get_object_or_404(Veiculo, id=veiculo_id)
        form = VeiculoForm(instance=veiculo)
        context = {'form': form, 'veiculo': veiculo, 'is_edit': True}
        return render(request, 'veiculo/veiculo_form.html', context)

    def post(self, request, veiculo_id):
        veiculo = get_object_or_404(Veiculo, id=veiculo_id)
        form = VeiculoForm(request.POST, instance=veiculo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Veículo atualizado com sucesso.')
            return redirect('veiculo_list')

        messages.error(request, 'Corrija os campos destacados e tente novamente.')
        context = {'form': form, 'veiculo': veiculo, 'is_edit': True}
        return render(request, 'veiculo/veiculo_form.html', context, status=400)


class VeiculoDeleteView(LoginRequiredMixin, View):
    def get(self, request, veiculo_id):
        veiculo = get_object_or_404(Veiculo, id=veiculo_id)
        return render(request, 'veiculo/veiculo_confirm_delete.html', {'veiculo': veiculo})

    def post(self, request, veiculo_id):
        veiculo = get_object_or_404(Veiculo, id=veiculo_id)
        veiculo.delete()
        messages.success(request, 'Veículo excluído com sucesso.')
        return redirect('veiculo_list')

class ContatoView(View):
    def get(self, request):
        return render(request, 'contato.html')

    def post(self, request):
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        assunto = request.POST.get('assunto', '').strip()
        mensagem = request.POST.get('mensagem', '').strip()

        if not all([nome, email, assunto, mensagem]):
            messages.error(request, 'Por favor, preencha todos os campos.')
            return render(request, 'contato.html', status=400)

        # Aqui você pode adicionar lógica para enviar email ou salvar em BD
        messages.success(request, 'Mensagem enviada com sucesso! Retornaremos em breve.')
        return render(request, 'contato.html')


class LogoutView(LoginRequiredMixin, View):
    def post(self, request):
        logout(request)
        messages.success(request, 'Sessão encerrada com sucesso.')
        return redirect('login')

# Create your views here.
