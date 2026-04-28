from django.shortcuts import render, redirect, get_object_or_404
from django.db.models.deletion import ProtectedError
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from .models import *
from .forms import AvariaForm, ClienteForm, PagamentoForm, TarifaForm, TicketEmissaoForm, VagaQuantidadeForm, VeiculoForm
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin


def _escape_pdf_text(value):
    safe_value = str(value)
    safe_value = safe_value.replace("\\", "\\\\")
    safe_value = safe_value.replace("(", "\\(")
    safe_value = safe_value.replace(")", "\\)")
    return safe_value


def _build_simple_pdf(lines):
    content = ["BT", "/F1 11 Tf", "50 800 Td"]
    for line in lines:
        content.append(f"({_escape_pdf_text(line)}) Tj")
        content.append("0 -14 Td")
    content.append("ET")

    stream = "\n".join(content)
    stream_bytes_length = len(stream.encode("ascii", errors="ignore"))

    obj1 = "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    obj2 = "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    obj3 = "3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
    obj4 = f"4 0 obj\n<< /Length {stream_bytes_length} >>\nstream\n{stream}\nendstream\nendobj\n"
    obj5 = "5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"

    header = "%PDF-1.4\n"
    objects = [obj1, obj2, obj3, obj4, obj5]
    offsets = []
    current = len(header.encode("ascii"))
    body = ""

    for obj in objects:
        offsets.append(current)
        body += obj
        current += len(obj.encode("ascii"))

    xref_offset = len((header + body).encode("ascii"))
    xref = "xref\n0 6\n0000000000 65535 f \n"
    for offset in offsets:
        xref += f"{offset:010d} 00000 n \n"

    trailer = f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF"
    return (header + body + xref + trailer).encode("ascii")

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


class TicketCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = TicketEmissaoForm()
        return render(request, 'ticket/ticket_form.html', {'form': form})

    def post(self, request):
        form = TicketEmissaoForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'Corrija os campos destacados para emitir o ticket.')
            return render(request, 'ticket/ticket_form.html', {'form': form}, status=400)

        vaga_escolhida = form.cleaned_data['vaga']
        cliente = form.cleaned_data.get('cliente')
        veiculo = form.cleaned_data.get('veiculo')

        if cliente is None and veiculo and veiculo.cliente_id:
            cliente = veiculo.cliente

        with transaction.atomic():
            vaga = Vaga.objects.select_for_update().get(pk=vaga_escolhida.pk)
            if vaga.status != 'livre':
                messages.error(request, f'A vaga {vaga.numero} nao esta livre no momento.')
                return redirect('ticket_create')

            ticket = Ticket.objects.create(
                vaga=vaga,
                operador=request.user,
                cliente=cliente,
                veiculo=veiculo,
                status='aberto',
            )
            vaga.status = 'ocupada'
            vaga.save(update_fields=['status'])

        messages.success(request, f'Ticket {ticket.id} emitido com sucesso.')
        return redirect(f"{reverse('ticket_list')}?pdf_ticket_id={ticket.id}")


class TicketListView(LoginRequiredMixin, View):
    def get(self, request):
        tickets = Ticket.objects.select_related('vaga', 'operador', 'veiculo', 'cliente', 'pagamento').all().order_by('-entrada')
        pdf_ticket_id = request.GET.get('pdf_ticket_id')
        pdf_ticket_url = None

        if pdf_ticket_id and str(pdf_ticket_id).isdigit():
            try:
                ticket = Ticket.objects.get(pk=int(pdf_ticket_id))
                pdf_ticket_url = reverse('ticket_pdf', kwargs={'ticket_id': ticket.id})
            except Ticket.DoesNotExist:
                pdf_ticket_url = None

        return render(request, 'ticket/ticket_list.html', {'tickets': tickets, 'pdf_ticket_url': pdf_ticket_url})


class TicketPdfView(LoginRequiredMixin, View):
    def get(self, request, ticket_id):
        ticket = get_object_or_404(
            Ticket.objects.select_related('vaga', 'operador', 'veiculo', 'cliente'),
            id=ticket_id,
        )

        lines = [
            'TICKET DE AGENDAMENTO DE VAGA',
            '',
            f'Ticket: {ticket.id}',
            f'Vaga: {ticket.vaga.numero}',
            f'Entrada: {ticket.entrada.strftime("%d/%m/%Y %H:%M:%S")}',
            f'Saida: {ticket.saida.strftime("%d/%m/%Y %H:%M:%S") if ticket.saida else "Em aberto"}',
            f'Status: {ticket.get_status_display()}',
            f'Operador: {ticket.operador.get_username()}',
            f'Veiculo: {ticket.veiculo.placa if ticket.veiculo_id else "Nao informado"}',
            f'Cliente: {ticket.cliente.nome if ticket.cliente_id else "Nao informado"}',
            '',
            'Comprovante para impressao.',
        ]

        pdf_bytes = _build_simple_pdf(lines)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="ticket_{ticket.id}.pdf"'
        return response


class PagamentoCreateView(LoginRequiredMixin, View):
    def get(self, request, ticket_id):
        ticket = get_object_or_404(Ticket.objects.select_related('vaga', 'operador', 'veiculo', 'cliente'), id=ticket_id)

        if ticket.status != 'aberto':
            messages.error(request, 'Este ticket ja esta finalizado ou cancelado.')
            return redirect('ticket_list')

        if Pagamento.objects.filter(ticket=ticket).exists():
            messages.error(request, 'Este ticket ja possui pagamento registrado.')
            return redirect('ticket_list')

        form = PagamentoForm()
        if not form.fields['tarifa'].queryset.exists():
            messages.error(request, 'Nao ha tarifa ativa para este horario. Cadastre ou ajuste uma tarifa antes de pagar.')
            return redirect('ticket_list')

        return render(request, 'pagamento/pagamento_form.html', {'form': form, 'ticket': ticket})

    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket.objects.select_related('vaga', 'operador', 'veiculo', 'cliente'), id=ticket_id)

        if ticket.status != 'aberto':
            messages.error(request, 'Este ticket ja esta finalizado ou cancelado.')
            return redirect('ticket_list')

        if Pagamento.objects.filter(ticket=ticket).exists():
            messages.error(request, 'Este ticket ja possui pagamento registrado.')
            return redirect('ticket_list')

        form = PagamentoForm(request.POST)
        if not form.is_valid():
            return render(request, 'pagamento/pagamento_form.html', {'form': form, 'ticket': ticket}, status=400)

        tarifa = form.cleaned_data['tarifa']
        forma_pagamento = form.cleaned_data['forma_pagamento']

        with transaction.atomic():
            ticket = Ticket.objects.select_for_update().get(pk=ticket.pk)
            if ticket.status != 'aberto':
                messages.error(request, 'Este ticket nao esta mais aberto.')
                return redirect('ticket_list')

            saida = timezone.now()
            valor_total = Pagamento.calcular_valor(ticket, tarifa, saida)

            ticket.saida = saida
            ticket.status = 'finalizado'
            ticket.save(update_fields=['saida', 'status'])

            pagamento = Pagamento.objects.create(
                ticket=ticket,
                tarifa=tarifa,
                valor_total=valor_total,
                forma_pagamento=forma_pagamento,
            )

        messages.success(request, f'Pagamento registrado com sucesso. Valor total: R$ {pagamento.valor_total}.')
        return redirect('ticket_list')


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
