# Read Email and transform into events 'MailNotification'
start cmd /k Events_MailNotification_Run.bat

# Read 'MailNotification' events 
#  
# and transform into commands
start cmd /k Actuators_Dispatch_Mail_Commands_Run.bat
