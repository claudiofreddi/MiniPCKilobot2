from Lib_MailSender import MailSender

MyMailSender = MailSender()

subject = "Mail Subject"
body = "Mail Body"
recipients = "me@claudiofreddi.eu"

MyMailSender.send_email(subject, body,recipients)
