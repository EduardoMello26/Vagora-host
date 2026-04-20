from django.shortcuts import render, redirect, get_object_or_404
from django.db.models.deletion import ProtectedError
from django.db import transaction
from .models import *
from .forms import AvariaForm, ClienteForm, TarifaForm, VagaQuantidadeForm, VeiculoForm
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


class TarifaCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = TarifaForm()
        return render(request, 'tarifa/tarifa_form.html', {'form': form, 'is_edit': False})

    def post(self, request):
        form = TarifaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarifa cadastrada com sucesso.')
            return redirect('tarifa_create')

        messages.error(request, 'Corrija os campos destacados e tente novamente.')
        return render(request, 'tarifa/tarifa_form.html', {'form': form, 'is_edit': False}, status=400)


class TarifaListView(LoginRequiredMixin, View):
    def get(self, request):
        tarifas = Tarifa.objects.all().order_by('hora_inicio', 'tipo_veiculo', 'descricao')
        return render(request, 'tarifa/tarifa_list.html', {'tarifas': tarifas})


class TarifaUpdateView(LoginRequiredMixin, View):
    def get(self, request, tarifa_id):
        tarifa = get_object_or_404(Tarifa, id=tarifa_id)
        form = TarifaForm(instance=tarifa)
        context = {'form': form, 'tarifa': tarifa, 'is_edit': True}
        return render(request, 'tarifa/tarifa_form.html', context)

    def post(self, request, tarifa_id):
        tarifa = get_object_or_404(Tarifa, id=tarifa_id)
        form = TarifaForm(request.POST, instance=tarifa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarifa atualizada com sucesso.')
            return redirect('tarifa_list')

        messages.error(request, 'Corrija os campos destacados e tente novamente.')
        context = {'form': form, 'tarifa': tarifa, 'is_edit': True}
        return render(request, 'tarifa/tarifa_form.html', context, status=400)


class TarifaDeleteView(LoginRequiredMixin, View):
    def get(self, request, tarifa_id):
        tarifa = get_object_or_404(Tarifa, id=tarifa_id)
        return render(request, 'tarifa/tarifa_confirm_delete.html', {'tarifa': tarifa})

    def post(self, request, tarifa_id):
        tarifa = get_object_or_404(Tarifa, id=tarifa_id)
        if Pagamento.objects.filter(tarifa=tarifa).exists():
            messages.error(request, 'Nao foi possivel excluir esta tarifa porque ela ja foi usada em pagamentos.')
            return redirect('tarifa_list')

        tarifa.delete()
        messages.success(request, 'Tarifa excluida com sucesso.')
        return redirect('tarifa_list')


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


class VagaListView(LoginRequiredMixin, View):
    def get(self, request):
        vagas = Vaga.objects.all().order_by('numero')
        form = VagaQuantidadeForm(initial={'quantidade': vagas.count() or 1})
        context = {
            'vagas': vagas,
            'form': form,
            'total_vagas': vagas.count(),
            'vagas_livres': vagas.filter(status='livre').count(),
            'vagas_ocupadas': vagas.filter(status='ocupada').count(),
        }
        return render(request, 'vaga/vaga_list.html', context)

    def post(self, request):
        form = VagaQuantidadeForm(request.POST)
        vagas = Vaga.objects.all().order_by('numero')

        if form.is_valid():
            quantidade = form.cleaned_data['quantidade']
            criadas = 0

            with transaction.atomic():
                for numero in range(1, quantidade + 1):
                    _, created = Vaga.objects.get_or_create(numero=numero, defaults={'status': 'livre'})
                    if created:
                        criadas += 1

            if criadas:
                messages.success(request, f'{criadas} vaga(s) criada(s) com sucesso.')
            else:
                messages.success(request, 'Nenhuma nova vaga foi criada. Todas as vagas já existem.')

            return redirect('vaga_list')

        context = {
            'vagas': vagas,
            'form': form,
            'total_vagas': vagas.count(),
            'vagas_livres': vagas.filter(status='livre').count(),
            'vagas_ocupadas': vagas.filter(status='ocupada').count(),
        }
        return render(request, 'vaga/vaga_list.html', context, status=400)


class VagaToggleView(LoginRequiredMixin, View):
    def post(self, request, vaga_id):
        vaga = get_object_or_404(Vaga, id=vaga_id)
        vaga.status = 'ocupada' if vaga.status == 'livre' else 'livre'
        vaga.save(update_fields=['status'])
        messages.success(request, f'Vaga {vaga.numero} atualizada para {vaga.get_status_display().lower()}.')
        return redirect('vaga_list')


class VagaDeleteView(LoginRequiredMixin, View):
    def get(self, request, vaga_id):
        vaga = get_object_or_404(Vaga, id=vaga_id)
        return render(request, 'vaga/vaga_confirm_delete.html', {'vaga': vaga})

    def post(self, request, vaga_id):
        vaga = get_object_or_404(Vaga, id=vaga_id)
        if Ticket.objects.filter(vaga=vaga).exists():
            messages.error(request, 'Nao foi possivel excluir esta vaga porque ela possui tickets vinculados.')
            return redirect('vaga_list')

        vaga.delete()
        messages.success(request, 'Vaga excluida com sucesso.')
        return redirect('vaga_list')


class VagaDeleteAllView(LoginRequiredMixin, View):
    def post(self, request):
        if Ticket.objects.filter(vaga__isnull=False).exists():
            messages.error(request, 'Nao foi possivel excluir todas as vagas porque existe ticket vinculado a pelo menos uma vaga.')
            return redirect('vaga_list')

        total = Vaga.objects.count()
        if total == 0:
            messages.error(request, 'Nao existem vagas cadastradas para excluir.')
            return redirect('vaga_list')

        with transaction.atomic():
            Vaga.objects.all().delete()

        messages.success(request, f'{total} vaga(s) excluida(s) com sucesso.')
        return redirect('vaga_list')


class AvariaCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = AvariaForm()
        return render(request, 'avaria/avaria_form.html', {'form': form, 'is_edit': False})

    def post(self, request):
        form = AvariaForm(request.POST)
        if form.is_valid():
            avaria = form.save(commit=False)
            avaria.operador = request.user
            avaria.save()
            messages.success(request, 'Avaria registrada com sucesso.')
            return redirect('avaria_create')

        messages.error(request, 'Corrija os campos destacados e tente novamente.')
        return render(request, 'avaria/avaria_form.html', {'form': form, 'is_edit': False}, status=400)


class AvariaListView(LoginRequiredMixin, View):
    def get(self, request):
        avarias = Avaria.objects.select_related('veiculo', 'operador').all().order_by('-registrado_em')
        return render(request, 'avaria/avaria_list.html', {'avarias': avarias})


class AvariaUpdateView(LoginRequiredMixin, View):
    def get(self, request, avaria_id):
        avaria = get_object_or_404(Avaria, id=avaria_id)
        form = AvariaForm(instance=avaria)
        context = {'form': form, 'avaria': avaria, 'is_edit': True}
        return render(request, 'avaria/avaria_form.html', context)

    def post(self, request, avaria_id):
        avaria = get_object_or_404(Avaria, id=avaria_id)
        form = AvariaForm(request.POST, instance=avaria)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.operador = avaria.operador
            updated.save()
            messages.success(request, 'Avaria atualizada com sucesso.')
            return redirect('avaria_list')

        messages.error(request, 'Corrija os campos destacados e tente novamente.')
        context = {'form': form, 'avaria': avaria, 'is_edit': True}
        return render(request, 'avaria/avaria_form.html', context, status=400)


class AvariaDeleteView(LoginRequiredMixin, View):
    def get(self, request, avaria_id):
        avaria = get_object_or_404(Avaria, id=avaria_id)
        return render(request, 'avaria/avaria_confirm_delete.html', {'avaria': avaria})

    def post(self, request, avaria_id):
        avaria = get_object_or_404(Avaria, id=avaria_id)
        avaria.delete()
        messages.success(request, 'Avaria excluída com sucesso.')
        return redirect('avaria_list')

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
