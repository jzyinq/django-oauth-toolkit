import django.db.models.deletion
import swapper as swapper
from django.conf import settings
from django.db import migrations, models

import oauth2_provider.generators
import oauth2_provider.validators


class Migration(migrations.Migration):
    """
    The following migrations are squashed here:
    - 0001_initial.py
    - 0002_08_updates.py
    - 0003_auto_20160316_1503.py
    - 0004_auto_20160525_1623.py
    - 0005_auto_20170514_1141.py
    - 0006_auto_20171214_2232.py
    """
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        swapper.dependency('oauth2_provider', 'Application'),
        swapper.dependency('oauth2_provider', 'AccessToken'),
        swapper.dependency('oauth2_provider', 'Grant'),
        swapper.dependency('oauth2_provider', 'RefreshToken'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(serialize=False, primary_key=True)),
                ('client_id',
                 models.CharField(default=oauth2_provider.generators.generate_client_id, unique=True, max_length=100,
                                  db_index=True)),
                ('redirect_uris', models.TextField(help_text='Allowed URIs list, space separated', blank=True)),
                ('client_type',
                 models.CharField(max_length=32, choices=[('confidential', 'Confidential'), ('public', 'Public')])),
                ('authorization_grant_type', models.CharField(max_length=32,
                                                              choices=[('authorization-code', 'Authorization code'),
                                                                       ('implicit', 'Implicit'),
                                                                       ('password', 'Resource owner password-based'),
                                                                       ('client-credentials', 'Client credentials')])),
                ('client_secret',
                 models.CharField(default=oauth2_provider.generators.generate_client_secret, max_length=255,
                                  db_index=True, blank=True)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('user',
                 models.ForeignKey(related_name="oauth2_provider_application", blank=True, to=settings.AUTH_USER_MODEL,
                                   null=True, on_delete=models.CASCADE)),
                ('skip_authorization', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
                'swappable': swapper.swappable_setting('oauth2_provider', 'Application'),
            },
        ),
        migrations.CreateModel(
            name='AccessToken',
            fields=[
                ('id', models.BigAutoField(serialize=False, primary_key=True)),
                ('token', models.CharField(unique=True, max_length=255)),
                ('expires', models.DateTimeField()),
                ('scope', models.TextField(blank=True)),
                ('application', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                                  to=swapper.get_model_name('oauth2_provider', 'Application'))),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                           related_name='oauth2_provider_accesstoken', to=settings.AUTH_USER_MODEL)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                # Circular reference. Can't add it here.
                # ('source_refresh_token', models.OneToOneField(blank=True, null=True,
                # on_delete=django.db.models.deletion.SET_NULL, to=oauth2_settings.REFRESH_TOKEN_MODEL,
                # related_name="refreshed_access_token")),
            ],
            options={
                'abstract': False,
                'swappable': swapper.swappable_setting('oauth2_provider', 'AccessToken')
            },
        ),
        migrations.CreateModel(
            name='Grant',
            fields=[
                ('id', models.BigAutoField(serialize=False, primary_key=True)),
                ('code', models.CharField(unique=True, max_length=255)),
                ('expires', models.DateTimeField()),
                ('redirect_uri', models.CharField(max_length=255)),
                ('scope', models.TextField(blank=True)),
                ('application', models.ForeignKey(to=swapper.get_model_name('oauth2_provider', 'Application'),
                                                  on_delete=models.CASCADE)),
                ('user',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='oauth2_provider_grant',
                                   to=settings.AUTH_USER_MODEL)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
                'swappable': swapper.swappable_setting('oauth2_provider', 'Grant')
            },
        ),
        migrations.CreateModel(
            name='RefreshToken',
            fields=[
                ('id', models.BigAutoField(serialize=False, primary_key=True)),
                ('token', models.CharField(max_length=255)),
                ('access_token', models.OneToOneField(blank=True, null=True, related_name="refresh_token",
                                                      to=swapper.get_model_name('oauth2_provider', 'AccessToken'),
                                                      on_delete=models.SET_NULL)),
                ('application', models.ForeignKey(to=swapper.get_model_name('oauth2_provider', 'Application'),
                                                  on_delete=models.CASCADE)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name='oauth2_provider_refreshtoken', to=settings.AUTH_USER_MODEL)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('revoked', models.DateTimeField(null=True)),
            ],
            options={
                'abstract': False,
                'swappable': swapper.swappable_setting('oauth2_provider', 'RefreshToken'),
                'unique_together': set([("token", "revoked")]),
            },
        ),
        migrations.AddField(
            model_name='AccessToken',
            name='source_refresh_token',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                       to=swapper.get_model_name('oauth2_provider', 'RefreshToken'),
                                       related_name="refreshed_access_token"),
        ),
    ]
