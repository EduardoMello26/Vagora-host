from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import ClienteForm
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
        return render(request, 'cliente_form.html', {'form': form})

    def post(self, request):
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente cadastrado com sucesso.')
            return redirect('cliente_create')

        messages.error(request, 'Corrija os campos destacados e tente novamente.')
        return render(request, 'cliente_form.html', {'form': form}, status=400)

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
