from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='animal',
            options={'ordering': ['ear_tag']},
        ),
        migrations.AddIndex(
            model_name='animal',
            index=models.Index(fields=['farm', 'status'], name='core_animal_farm_id_b8cf8f_idx'),
        ),
        migrations.AddIndex(
            model_name='animal',
            index=models.Index(fields=['group'], name='core_animal_group_i_01f5fd_idx'),
        ),
        migrations.AddConstraint(
            model_name='weightrecord',
            constraint=models.CheckConstraint(condition=models.Q(('weight_kg__gt', 0)), name='weight_positive'),
        ),
        migrations.AddIndex(
            model_name='weightrecord',
            index=models.Index(fields=['animal', '-date'], name='core_weightr_animal__f764af_idx'),
        ),
        migrations.AddConstraint(
            model_name='vaccination',
            constraint=models.CheckConstraint(condition=models.Q(next_due__isnull=True) | models.Q(next_due__gte=models.F('date')), name='vaccination_next_due_after_date'),
        ),
        migrations.AddIndex(
            model_name='vaccination',
            index=models.Index(fields=['animal', '-date'], name='core_vaccin_animal__1e0816_idx'),
        ),
        migrations.AddIndex(
            model_name='vaccination',
            index=models.Index(fields=['next_due'], name='core_vaccin_next_du_5d97d8_idx'),
        ),
        migrations.AddConstraint(
            model_name='treatment',
            constraint=models.CheckConstraint(condition=models.Q(next_due__isnull=True) | models.Q(next_due__gte=models.F('date')), name='treatment_next_due_after_date'),
        ),
        migrations.AddIndex(
            model_name='treatment',
            index=models.Index(fields=['animal', '-date'], name='core_treatm_animal__4f5aec_idx'),
        ),
        migrations.AddIndex(
            model_name='treatment',
            index=models.Index(fields=['next_due'], name='core_treatm_next_du_7cf65a_idx'),
        ),
        migrations.AddConstraint(
            model_name='movement',
            constraint=models.CheckConstraint(condition=~models.Q(('from_group', models.F('to_group'))), name='movement_distinct_groups'),
        ),
        migrations.AddIndex(
            model_name='movement',
            index=models.Index(fields=['animal', '-date'], name='core_moveme_animal__685fce_idx'),
        ),
        migrations.AddConstraint(
            model_name='sale',
            constraint=models.CheckConstraint(condition=models.Q(('price_brl__gt', 0)), name='sale_price_positive'),
        ),
        migrations.AddConstraint(
            model_name='costentry',
            constraint=models.CheckConstraint(condition=models.Q(('amount_brl__gt', 0)), name='cost_amount_positive'),
        ),
        migrations.AddIndex(
            model_name='costentry',
            index=models.Index(fields=['farm', '-date'], name='core_costen_farm_id_d2b2a5_idx'),
        ),
        migrations.AddIndex(
            model_name='costentry',
            index=models.Index(fields=['category', '-date'], name='core_costen_categor_2069fc_idx'),
        ),
    ]
