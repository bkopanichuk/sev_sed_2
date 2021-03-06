from apps.document.models.document_model import BaseDocument
from apps.document.models.task_model import Flow, EXECUTE, PENDING, FlowApprove

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class CreateFlow:
    """Створити процес виконання завдання, або підтвердження(залежно від параметру goal)
    Примітка: до виконання відноситься також візування та підпис докумету
    """
    def __init__(self, doc, goal=None):
        self.document: BaseDocument = doc
        self.flow = Flow
        self.goal = goal or EXECUTE
        self.approvers_list = self.document.approvers_list.all()

    def run(self):
        return self.create_flow()

    def create_flow(self):
        ##Якщо не вказано список підтвердження не створюємо новий процес виконання
        logger.info(self.approvers_list)
        if not self.approvers_list:
            return
        ## Додати новий процес розгляду
        flow_q = self.flow.objects.filter(status=PENDING, document=self.document)
        if flow_q.exists():
            flow = flow_q.first()
            flow.approvers_list.clear()
        else:
            flow = self.flow.objects.create(author=self.document.author, status=PENDING, document=self.document,
                                            goal=self.goal)

        flow.approvers_list.add(*self.approvers_list)
        ## Код що нижче додає список розглядачів.
        # Ніякої бізнес логіки окрім створення списку розглядаів немає.
        ## TODO Автоматично змінювати статус розгляду при відкритті документа

        for approver in self.document.approvers_list.all():
            if not FlowApprove.objects.filter(flow=flow, approver=approver).exists():
                FlowApprove.objects.create(author=self.document.author, status=PENDING, flow=flow, approver=approver)
        return flow