from django.db import migrations, models


GLOBAL_SETTINGS_KEYS = [
    ("credit_facility_link", "Credit Facility Link"),
    ("deed_poll", "Deed poll"),
    ("deed_poll_filming", "Deed poll Filming"),
    ("deed_poll_event", "Deed poll Event"),
    (
        "online_training_document",
        "Online Training Document (Commercial Operations)",
    ),
    ("event_online_training_document", "Online Training Document (Event)"),
    ("park_finder_link", "Park Finder Link"),
    ("fees_and_charges", "Fees and charges link"),
    ("event_fees_and_charges", "Event Fees and charges link"),
    ("commercial_filming_handbook", "Commercial Filming Handbook link"),
    ("park_stay_link", "Park Stay Link"),
    ("event_traffic_code_of_practice", "Event traffic code of practice"),
    ("trail_section_map", "Trail section map"),
    ("dwer_application_form", "DWER Application Form"),
    ("tourism_standards_link", "Tourism Standards Link"),
    ("privacy_policy_url", "Privacy Policy URL"),
    (
        "civil_aviation_safety_authority_link",
        "Civil Aviation Safety Authority Link",
    ),
]


def add_casa_link(apps, schema_editor):
    global_settings = apps.get_model("commercialoperator", "GlobalSettings")
    casa_url = "https://www.casa.gov.au/drones"
    casa_setting = global_settings.objects.filter(
        key="civil_aviation_safety_authority_link"
    ).first()

    if casa_setting is None:
        casa_setting = global_settings.objects.filter(
            key__in=["casa_link", "Civil Aviation Safety Authority Link"]
        ).first()

    if casa_setting is None:
        global_settings.objects.create(
            key="civil_aviation_safety_authority_link",
            value=casa_url,
        )
    else:
        casa_setting.key = "civil_aviation_safety_authority_link"
        casa_setting.value = casa_setting.value or casa_url
        casa_setting.save(update_fields=["key", "value"])


def remove_casa_link(apps, schema_editor):
    global_settings = apps.get_model("commercialoperator", "GlobalSettings")
    global_settings.objects.filter(
        key="civil_aviation_safety_authority_link"
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("commercialoperator", "0143_vessel_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="globalsettings",
            name="key",
            field=models.CharField(
                choices=GLOBAL_SETTINGS_KEYS,
                max_length=255,
            ),
        ),
        migrations.RunPython(add_casa_link, remove_casa_link),
    ]
