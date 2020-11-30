import base64
import os
import uuid

from django.conf import settings
from django.test import TestCase
from django.utils.timezone import now

from apps.document.models.document_constants import OUTGOING
from apps.document.models.document_model import BaseDocument, REGISTERED
from apps.document.models.sign_model import Sign
from apps.l_core.models import CoreOrganization,CoreUser
from apps.l_core.ua_sign import verify_external
from ..services.sender_service import CreateSevOutgoing

MEDIA_ROOT = settings.MEDIA_ROOT


class TestCase(TestCase):
    def setUp(self):
        producer = self.create_producer()
        print('PRODUCER: ', producer)
        signer = self.create_signer(producer)
        print('SIGNER: ', signer)
        consumer = self.create_consumer()
        print('CONSUMER: ', consumer)
        document = self.create_document(producer, consumer, signer)
        document_2 = self.create_document(producer, consumer, signer)
        print('DOCUMENT: ', document)
        sign = self.create_sign(document,signer)
        print('SIGN: ', sign.sign_info)
        self.create_outgoing_document(document=document)
        self.create_reply_outgoing_document(document=document_2, referred_document=document)

    def create_producer(self):
        producer_data = {
            "name": "PRODUCER",
            "full_name": "TEST PRODUCER",
            "edrpou": "23455432",
            "system_id": "ecc37736-8da8-415c-85b6-d12a8fc3e62d",
            "system_password": "08a3d06a-ccb6-4465-b8fa-937e7276b442"
        }
        producer = CoreOrganization(**producer_data)
        producer.save()

        return producer

    def create_signer(self, producer):
        data = {"password": "pbkdf2_sha256$216000$XHvaAXUupOJ5$CWSLLClQj7FwFZFX4uhK0Di6EcE2sSPexUKsR5M/ILk=",
                "is_superuser": True,
                "username": "test",
                "is_staff": True,
                "is_active": True,
                "date_joined": "2020-10-03T19:06:23.517Z",
                "organization": producer,
                "department": None,
                "first_name": "TEST",
                "last_name": "TEST",
                "email": "test@gmail.com",
                "ipn": None, }
        signer = CoreUser(**data)
        signer.save()
        return signer


    def create_consumer(self):
        cons_data = {"name": "CONSUMER",
                     "full_name": "TEST CONSUMER",
                     "edrpou": "12341234",
                     "system_id": "2c1e8ad0-3a19-41fb-9540-74b5189cca5e",
                     "system_password": "c106b12a-a704-460e-ba2b-30dbf9a6c823"}
        consumer = CoreOrganization(**cons_data)
        consumer.save()
        return consumer

    def create_document(self, producer, consumer,signer):
        reg_number = uuid.uuid4().__str__()[:10]
        reg_date = now().date()
        document = BaseDocument(document_cast=OUTGOING, organization=producer, reg_number=reg_number,
                                reg_date=reg_date)
        document.main_file.name = 'test/CryptoAutograph_ProgrammerHelp - 2.0.pdf'
        document.save()
        document.mailing_list.add(consumer)

        document.status = REGISTERED
        document.main_signer = signer
        document.author = signer
        document.save()
        return document

    def create_sign(self, document,signer):
        sign_data_relative_path = 'test/CryptoAutograph_ProgrammerHelp - 2.0.pdf.p7s'
        sign_data_path = os.path.join(MEDIA_ROOT, sign_data_relative_path)
        with open(sign_data_path, 'rb') as sign:
            data = sign.read()
            data_b_64 = base64.b64encode(data).decode()
        sign_info = verify_external(data_path=document.main_file.path, sign_path=sign_data_path)
        sign = Sign(document=document, sign=data_b_64, sign_info=sign_info,signer = signer)
        sign.save()
        return sign

    def create_outgoing_document(self, document):
        print('CREATE TEST DATA')
        sev_outgoing = CreateSevOutgoing(document=document)
        sev_outgoing.run()

    def create_reply_outgoing_document(self, document, referred_document):
        print('CREATE TEST REPLY DATA')
        sev_outgoing = CreateSevOutgoing(document=document, referred_document=referred_document)
        sev_outgoing.run()

    def test_download_incoming(self):
        print('DOWNLOADING TEST DATA')
        from apps.sevovvintegration.services import download_service
        ds = download_service.DownloadMessages()
        ds.run()

        for document in BaseDocument.objects.all():
            print(document.main_file.name)
