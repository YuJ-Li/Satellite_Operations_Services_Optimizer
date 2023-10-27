# Generated by Django 4.1.12 on 2023-10-18 09:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('state_model', '0003_alter_satelliteschedule_satellite'),
    ]

    operations = [
        migrations.AlterField(
            model_name='downlinktask',
            name='schedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='downlink_tasks', to='state_model.satelliteschedule'),
        ),
        migrations.AlterField(
            model_name='groundstationrequest',
            name='satellite',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ground_station_requests', to='state_model.satellite'),
        ),
        migrations.AlterField(
            model_name='imagingtask',
            name='schedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='imaging_tasks', to='state_model.satelliteschedule'),
        ),
        migrations.AlterField(
            model_name='maintenancetask',
            name='schedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='maintenance_tasks', to='state_model.satelliteschedule'),
        ),
    ]
