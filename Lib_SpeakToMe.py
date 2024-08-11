#Env

# Python program to convert 
# text to speech 
  
# import the required module from text to speech conversion 
# pip install pywin32
import win32com.client 
  
# Calling the Dispatch method of the module which  
# interact with Microsoft Speech SDK to speak 
# the given input from the keyboard 


class Service_SpeakToMe:

    _Speaker_On = False
        
    def __init__(self, StartupText = "", SpeakerOn = False):
        self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
        self._Speaker_On = SpeakerOn
        if (StartupText != ""):
            if (self._Speaker_On):
                self.speaker.Speak(StartupText) 
        return
        
  
    def Speak(self,text):
        if (self._Speaker_On):
            self.speaker.Speak(text) 
        else:
            print("Audio Disabled")
  
# To stop the program press 
# CTRL + Z 

if (__name__== "__main__"):
    MySpeak = Service_SpeakToMe(SpeakerOn=True)
    MySpeak.Speak("Messaggio di prova")

