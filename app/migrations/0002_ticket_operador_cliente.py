from django.db import migrations, models
import django.db.models.deletion


def backfill_ticket_cliente(apps, schema_editor):
    Ticket = apps.get_model("app", "Ticket")
    Cliente = apps.get_model("app", "Cliente")

    for ticket in Ticket.objects.select_related("veiculo", "veiculo__cliente").all():
        cliente = None

        if ticket.veiculo_id and ticket.veiculo.cliente_id:
            cliente = ticket.veiculo.cliente
        else:
            cpf_temporario = f"TEMP{ticket.id:010d}"
            cliente = Cliente.objects.create(
                nome=f"Cliente sem cadastro #{ticket.id}",
                cpf=cpf_temporario,
                tipo="avulso",
            )
            if ticket.veiculo_id and ticket.veiculo.cliente_id is None:
                ticket.veiculo.cliente = cliente
                ticket.veiculo.save(update_fields=["cliente"])

        ticket.cliente = cliente
        ticket.save(update_fields=["cliente"])


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="ticket",
            old_name="usuario",
            new_name="operador",
        ),
        migrations.AddField(
            model_name="ticket",
            name="cliente",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="app.cliente",
                verbose_name="Cliente",
            ),
        ),
        migrations.AlterField(
            model_name="ticket",
            name="operador",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="app.usuario",
                verbose_name="Operador",
            ),
        ),
        migrations.RunPython(backfill_ticket_cliente, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="ticket",
            name="cliente",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="app.cliente",
                verbose_name="Cliente",
            ),
        ),
    ]
