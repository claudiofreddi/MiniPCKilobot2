from Lib_MailSender import MailSender

MyMailSender = MailSender("me@claudiofreddi.eu")

subject = "Mail Subject"
body = "Mail Body"
recipients = "me@claudiofreddi.eu"

MyMailSender.send_email(subject, body,recipients)
