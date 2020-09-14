import logging
from django.conf import settings
from django.core import mail
from django.core.mail import send_mail
from . import Constants as const
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.

SENDER_DOMAIN = settings.EMAIL_HOST_USER


def send_attachment(subject,body_content,recipients,attachments):
    try:
        connection = mail.get_connection()
        connection.open()
        email1 = mail.EmailMessage(subject,body_content,SENDER_DOMAIN,recipients,connection=connection,)
        email1.send()
        connection.send_messages([email1])
        connection.close()
    except Exception as e:
        logging.error("Error in Sending Email attachment to User..",e)

def send_notification(subject,body_content,recipients):
    try:
        print(recipients, subject, body_content)
        connection = mail.get_connection()
        connection.open()
        email1 = mail.EmailMessage(subject,body_content,SENDER_DOMAIN,recipients,connection=connection,)
        email1.send()
        connection.send_messages([email1])
        connection.close()
    except Exception as e:
        print("sent..")
        logging.error("Error in Sending Email to User..",e)
