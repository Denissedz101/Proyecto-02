# Generated by Django 5.2 on 2025-05-02 18:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("E11evenStore", "0010_alter_cliente_usuario"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="administrativo",
            name="usuario",
        ),
    ]
