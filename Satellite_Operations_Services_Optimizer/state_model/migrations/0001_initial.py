# Generated by Django 4.1.12 on 2023-10-06 09:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GroundStation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('groundStationId', models.CharField(max_length=50, unique=True)),
                ('stationName', models.CharField(max_length=100)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('height', models.FloatField()),
                ('stationMask', models.CharField(max_length=100)),
                ('uplinkRate', models.FloatField()),
                ('downlinkRate', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='GroundStationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stationName', models.CharField(max_length=100)),
                ('acquisitionOfSignal', models.DateTimeField()),
                ('lossOfSignal', models.DateTimeField()),
                ('satelliteScheduleId', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Satellite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('satelliteId', models.CharField(max_length=50, unique=True)),
                ('TLE', models.TextField()),
                ('storageCapacity', models.FloatField()),
                ('powerCapacity', models.FloatField()),
                ('fieldOfView', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='SatelliteSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheduleID', models.CharField(max_length=50, unique=True)),
                ('activityWindow', models.DateTimeField()),
                ('satellite', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='state_model.satellite')),
            ],
        ),
        migrations.CreateModel(
            name='Outage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('startTime', models.DateTimeField()),
                ('endTime', models.DateTimeField()),
                ('groundStation', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='outages', to='state_model.groundstation')),
                ('satellite', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='outages', to='state_model.satellite')),
            ],
        ),
        migrations.CreateModel(
            name='MaintenanceTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TaskID', models.CharField(max_length=50, unique=True)),
                ('revisitFrequency', models.PositiveIntegerField()),
                ('priority', models.PositiveIntegerField()),
                ('target', models.CharField(max_length=255)),
                ('timeWindow', models.DateTimeField()),
                ('duration', models.DurationField()),
                ('payloadOperationAffected', models.BooleanField()),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='maintenance_tasks', to='state_model.satelliteschedule')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ImagingTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TaskID', models.CharField(max_length=50, unique=True)),
                ('revisitFrequency', models.PositiveIntegerField()),
                ('priority', models.PositiveIntegerField()),
                ('imagingRegionLatitude', models.FloatField()),
                ('imagingRegionLongitude', models.FloatField()),
                ('imagingTime', models.DateTimeField()),
                ('deliveryTime', models.DateTimeField()),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='imaging_tasks', to='state_model.satelliteschedule')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imageId', models.CharField(max_length=50, unique=True)),
                ('imageSize', models.PositiveIntegerField()),
                ('imageType', models.CharField(choices=[('SL', 'Spotlight'), ('MR', 'Medium Resolution'), ('LR', 'Low Resolution')], max_length=2)),
                ('groundStationRequest', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='images', to='state_model.groundstationrequest')),
                ('imagingTask', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='images', to='state_model.imagingtask')),
            ],
        ),
        migrations.AddField(
            model_name='groundstationrequest',
            name='satellite',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='ground_station_requests', to='state_model.satellite'),
        ),
        migrations.CreateModel(
            name='DownlinkTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TaskID', models.CharField(max_length=50, unique=True)),
                ('revisitFrequency', models.PositiveIntegerField()),
                ('priority', models.PositiveIntegerField()),
                ('imageId', models.CharField(max_length=50)),
                ('downlinkStartTime', models.DateTimeField()),
                ('downlinkEndTime', models.DateTimeField()),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='downlink_tasks', to='state_model.satelliteschedule')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
