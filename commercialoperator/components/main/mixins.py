from django.db import models
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.exceptions import ValidationError

from reversion.models import Version
from reversion import revisions

from commercialoperator.components.segregation.utils import (
    retrieve_ledger_user_info_by_id,
)

from dirtyfields import DirtyFieldsMixin
from datetime import datetime
import uuid
import os

class SanitiseMixin(models.Model):
    """
    Sanitise models fields
    """

    def save(self, **kwargs):
        from commercialoperator.components.main.utils import sanitise_fields
        #sanitise
        exclude = kwargs.pop("exclude_sanitise", []) #fields that should not be subject to full tag removal
        error_on_change = kwargs.pop("error_on_sanitise", []) #fields that should not be modified through tag removal (and should throw and error if they are)
        self = sanitise_fields(self, exclude, error_on_change)
        super(SanitiseMixin, self).save(**kwargs)

    class Meta:
        abstract = True


class SanitiseFileMixin(SanitiseMixin, DirtyFieldsMixin):
    """
    Sanitise file extensions and names
    """
    def auto_generate_file_name(self, extension):
        return "{}_{}_{}.{}".format(self._meta.model_name,uuid.uuid4(),int(datetime.now().timestamp()*100000), extension)

    def save(self, **kwargs):
        from commercialoperator.components.main.utils import check_file

        path_to_file = kwargs.pop("path_to_file",None)
        file_content = kwargs.pop("file_content",None)
        storage = kwargs.pop("storage",None)

        if not path_to_file:
            try:
                #we specify an empty string here so we can substitute our own (NOTE: may be worth changing how this works to just return the path)
                path_to_file = self._meta.get_field('_file').upload_to(self,'')
            except Exception as e:
                print(e)
                path_to_file = None

        if not storage:
            storage = self._meta.get_field('_file').storage

        if not file_content:
            file_content = self._file

        if path_to_file and file_content and storage:
            #check file extension
            check_file(file_content, self._meta.model_name)

            #check file size
            if file_content.size > settings.FILE_SIZE_LIMIT_BYTES:
                raise ValidationError("File size too large: Max {}MB".format(settings.FILE_SIZE_LIMIT_BYTES/1000000))

            #auto-gen file name
            _, extension = os.path.splitext(str(file_content))
            generated_file_name = self.auto_generate_file_name(extension.replace(".",""))
            read = file_content.read()
            if bool(read):
                self._file = storage.save('{}/{}'.format(path_to_file,generated_file_name), ContentFile(read))
        elif '_file' in self.get_dirty_fields() and self.get_dirty_fields()['_file']:
            raise ValidationError("Cannot change file")

        #proceed with general sanitisation and save
        super(SanitiseFileMixin, self).save(**kwargs)
    
    class Meta:
        abstract = True


class RevisionedMixin(SanitiseMixin):
    """
    A model tracked by reversion through the save method.
    """

    def save(self, **kwargs):
        if kwargs.pop("no_revision", False):
            super(RevisionedMixin, self).save(**kwargs)
        else:
            with revisions.create_revision():
                if "version_user" in kwargs:
                    revisions.set_user(kwargs.pop("version_user", None))
                if "version_comment" in kwargs:
                    revisions.set_comment(kwargs.pop("version_comment", ""))
                super(RevisionedMixin, self).save(**kwargs)

    @property
    def created_date(self):
        return Version.objects.get_for_object(self).last().revision.date_created

    @property
    def modified_date(self):
        return Version.objects.get_for_object(self).first().revision.date_created

    class Meta:
        abstract = True


class RetrieveUserResidentialAddressMixin:
    @staticmethod
    def get_user_residential_address(user_id):
        return (
            retrieve_ledger_user_info_by_id(user_id)
            .get("user", {})
            .get("residential_address", {})
        )
