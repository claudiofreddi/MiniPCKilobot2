
# MAILING LIB
import smtplib
from email.mime.text import MIMEText
from Robot_Envs import PASSWORD
from Robot_Envs import ADMIN_MAIL
from Robot_Envs import MAIL_SENDER

class MailSender:
    
    def __init__(self, defaultRecipientMail):
        self._defaultRecipientMail = defaultRecipientMail
        self.PrintLogEnabled = False
        self.smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        if (self.PrintLogEnabled == True):
            print ('__init__')
            
    def send_email(self, subject, body, recipients=''):
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = MAIL_SENDER
        if (recipients == ''):
            recipients = self._defaultRecipientMail

        msg['To'] = recipients 
        #', '.join(recipients)
        self.smtp_server.login(MAIL_SENDER, PASSWORD)
        self.smtp_server.sendmail(MAIL_SENDER, recipients, msg.as_string())
        print("Message sent!")

