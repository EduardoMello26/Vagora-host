import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_ticket_operador_cliente"),
    ]

    operations = [
        migrations.AddField(
            model_name="tarifa",
            name="hora_fim",
            field=models.TimeField(default=datetime.time(23, 59), verbose_name="Hora Fim"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="tarifa",
            name="hora_inicio",
            field=models.TimeField(default=datetime.time(0, 0), verbose_name="Hora Início"),
            preserve_default=False,
        ),
    ]
