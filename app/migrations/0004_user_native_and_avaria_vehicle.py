from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations, models
import django.db.models.deletion


def migrate_legacy_usuarios_to_auth_user(apps, schema_editor):
    LegacyUsuario = apps.get_model("app", "Usuario")
    Ticket = apps.get_model("app", "Ticket")
    Avaria = apps.get_model("app", "Avaria")
    User = apps.get_model("auth", "User")

    using = schema_editor.connection.alias
    mapping = {}

    for legacy_usuario in LegacyUsuario.objects.using(using).all().order_by("id"):
        user = User.objects.using(using).filter(username=legacy_usuario.email).first()

        if user is None:
            user = User.objects.using(using).create(
                username=legacy_usuario.email,
                email=legacy_usuario.email,
                first_name=legacy_usuario.nome,
                is_staff=legacy_usuario.tipo == "admin",
                is_superuser=legacy_usuario.tipo == "admin",
            )
            user.password = make_password(legacy_usuario.senha)
            user.save(update_fields=["password"])

        mapping[legacy_usuario.id] = user.id

    for old_id, new_id in mapping.items():
        Ticket.objects.using(using).filter(operador_id=old_id).update(operador_id=new_id)
        Avaria.objects.using(using).filter(operador_id=old_id).update(operador_id=new_id)


def backfill_avaria_veiculo(apps, schema_editor):
    Avaria = apps.get_model("app", "Avaria")
    using = schema_editor.connection.alias

    for avaria in Avaria.objects.using(using).select_related("ticket", "ticket__veiculo").all():
        if avaria.veiculo_id is None and avaria.ticket_id:
            avaria.veiculo_id = avaria.ticket.veiculo_id
            avaria.save(update_fields=["veiculo"])


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("app", "0003_tarifa_horarios"),
    ]

    operations = [
        migrations.RenameField(
            model_name="avaria",
            old_name="usuario",
            new_name="operador",
        ),
        migrations.AddField(
            model_name="avaria",
            name="veiculo",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="app.veiculo", verbose_name="Veículo"),
        ),
        migrations.RunPython(migrate_legacy_usuarios_to_auth_user, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="ticket",
            name="operador",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name="Operador"),
        ),
        migrations.AlterField(
            model_name="avaria",
            name="operador",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name="Operador"),
        ),
        migrations.RunPython(backfill_avaria_veiculo, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="avaria",
            name="veiculo",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="app.veiculo", verbose_name="Veículo"),
        ),
        migrations.RemoveField(
            model_name="avaria",
            name="ticket",
        ),
        migrations.DeleteModel(
            name="Usuario",
        ),
    ]
