from django.db import migrations, models
import commercialoperator.components.proposals.models
from commercialoperator.components.main.models import private_storage


class Migration(migrations.Migration):

    dependencies = [
        (
            "commercialoperator",
            "0142_merge_0141_jobqueue_and_more_0141_merge_20260629_1030",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="vessel",
            name="vessel_length",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="vessel",
            name="vessel_weight",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="vessel",
            name="number_of_tenders",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="vessel",
            name="certificate_of_survey",
            field=models.FileField(
                blank=True,
                max_length=512,
                null=True,
                storage=private_storage,
                upload_to=commercialoperator.components.proposals.models.update_vessel_doc_filename,
            ),
        ),
    ]