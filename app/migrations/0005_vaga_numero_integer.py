from django.db import migrations, models


def converter_numeros_vaga(apps, schema_editor):
    Vaga = apps.get_model("app", "Vaga")

    for vaga in Vaga.objects.all():
        if isinstance(vaga.numero, str):
            vaga.numero = int(vaga.numero)
            vaga.save(update_fields=["numero"])


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0004_user_native_and_avaria_vehicle"),
    ]

    operations = [
        migrations.RunPython(converter_numeros_vaga, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="vaga",
            name="numero",
            field=models.PositiveIntegerField(unique=True, verbose_name="Número"),
        ),
    ]
