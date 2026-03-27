from django.shortcuts import render, redirect, get_object_or_404
from .models import *
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


class LogoutView(LoginRequiredMixin, View):
    def post(self, request):
        logout(request)
        messages.success(request, 'Sessão encerrada com sucesso.')
        return redirect('login')

# Create your views here.
