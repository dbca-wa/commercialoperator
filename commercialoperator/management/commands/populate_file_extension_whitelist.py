from django.core.management.base import BaseCommand

from commercialoperator.components.main.models import FileExtensionWhitelist


class Command(BaseCommand):
    help = "Add the default file extensions to the global whitelist"

    extensions = ("pdf", "docx", "msg", "jpg", "jpeg", "png", "xlsx")

    def handle(self, *args, **options):
        created_extensions = []
        existing_extensions = []

        for extension in self.extensions:
            _, created = FileExtensionWhitelist.objects.get_or_create(
                name=extension,
                model="all",
            )
            if created:
                created_extensions.append(extension)
            else:
                existing_extensions.append(extension)

        if created_extensions:
            self.stdout.write(
                self.style.SUCCESS(
                    "Added file extensions: {}".format(
                        ", ".join(created_extensions)
                    )
                )
            )
        if existing_extensions:
            self.stdout.write(
                "Already present: {}".format(", ".join(existing_extensions))
            )