from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='costentry',
            constraint=models.CheckConstraint(check=models.Q(('amount_brl__gt', 0)), name='costentry_amount_positive'),
        ),
        migrations.AddConstraint(
            model_name='herdgroup',
            constraint=models.UniqueConstraint(fields=('farm', 'name'), name='uniq_group_name_per_farm'),
        ),
        migrations.AddConstraint(
            model_name='pasture',
            constraint=models.UniqueConstraint(fields=('farm', 'name'), name='uniq_pasture_name_per_farm'),
        ),
        migrations.AddConstraint(
            model_name='sale',
            constraint=models.CheckConstraint(check=models.Q(('price_brl__gt', 0)), name='sale_price_positive'),
        ),
        migrations.AddConstraint(
            model_name='weightrecord',
            constraint=models.CheckConstraint(check=models.Q(('weight_kg__gt', 0)), name='weightrecord_weight_positive'),
        ),
    ]
