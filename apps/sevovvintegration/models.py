import os
import uuid
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.timezone import now

from apps.document.models.document_model import BaseDocument
from apps.document.models.sign_model import Sign
from apps.l_core.models import CoreOrganization


def get_outgoing_xml_file_path(instance, filename):
    _now = now()
    return os.path.join(
        f'sevovv_integration/organization_{instance.document.organization.id}/outgoing/{_now.year}/{_now.month}/{_now.day}/{filename}')


def get_incoming_xml_file_path(instance, filename):
    _now = now()
    return os.path.join(
        f'sevovv_integration/organization_{instance.to_org.id}/incoming/{_now.year}/{_now.month}/{_now.day}/{filename}')


class SEVOutgoing(models.Model):
    sign = models.ForeignKey(Sign, on_delete=models.PROTECT,null=True)
    document = models.ForeignKey(BaseDocument, on_delete=models.PROTECT)
    referred_document = models.ForeignKey(BaseDocument, related_name="referred_doc", on_delete=models.PROTECT, null=True)
    from_org = models.ForeignKey(CoreOrganization, on_delete=models.PROTECT, related_name='outgoing_from')
    to_org = models.ForeignKey(CoreOrganization, on_delete=models.PROTECT, related_name='outgoing_to')
    xml_file = models.FileField(upload_to=get_outgoing_xml_file_path, null=True)
    message_id = models.CharField(max_length=256,default=uuid.uuid4)
    sending_result = JSONField(null=True)
    status = models.CharField(max_length=50, null=True)
    attestation = models.CharField(max_length=50, null=True)
    comment = models.CharField(max_length=50, null=True)


class SEVIncoming(models.Model):
    from_org = models.ForeignKey(CoreOrganization, on_delete=models.PROTECT, related_name='incoming_from')
    to_org = models.ForeignKey(CoreOrganization, on_delete=models.PROTECT, related_name='incoming_to')
    xml_file = models.FileField(upload_to=get_incoming_xml_file_path)
    status = models.CharField(max_length=50)
