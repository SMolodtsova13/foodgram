# Generated by Django 3.2 on 2024-09-23 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_ingredientrecipe_recipe'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='short_url',
            field=models.CharField(blank=True, db_index=True, max_length=20, unique=True),
        ),
    ]