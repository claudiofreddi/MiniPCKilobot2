# https://www.simplilearn.com/tutorials/python-tutorial/speech-recognition-in-python
# pip install SpeechRecognition 
# pip install pyaudio

# https://medium.com/john-snow-labs/the-complete-guide-to-information-extraction-from-texts-with-spark-nlp-and-python-c862dd33995f

import speech_recognition as sr
from Lib_SpeakToMe import *
from Socket_Utils_Timer import *
from thefuzz import process, fuzz

collection = ["come stai", "io sono", "spegni la luce"]

ACTIVATION_KEYWORD = "robot"
WAIT_TIMEOUT_AFTER_ASK = 15

print(sr.__version__)
recognizer_instance = sr.Recognizer() # Crea una istanza del recognizer
MySpeak = Service_SpeakToMe("",True)
MyTimer = Socket_Timer()

AskSomething = False
#source = sr.Microphone()

with  sr.Microphone() as source:  
    recognizer_instance.adjust_for_ambient_noise(source,3)
    print(f"recognizer_instance.energy_threshold:  {recognizer_instance.energy_threshold}")
    print(f"recognizer_instance.pause_threshold:  {recognizer_instance.pause_threshold}")
    
    if (True):
        while True:
            try:
                if (not AskSomething):
                    print("Waiting keyword...")
                else:
                    print("Waiting request...")
                audio = recognizer_instance.listen(source,1000)
                print("...")
                #print(len(audio.frame_data))
                try:
                    text = recognizer_instance.recognize_google(audio, language="it-IT")
                    print(text)
                    if (not AskSomething):
                        if (text == ACTIVATION_KEYWORD):
                            print("Dimmi...")
                            MySpeak.Speak("Ciao, dimmi")
                            MyTimer.start(WAIT_TIMEOUT_AFTER_ASK)
                            AskSomething = True
                    else:
                        print(process.extract(text, collection, scorer=fuzz.ratio))
                        if (MyTimer.IsTimeout()):
                            AskSomething = False
                        MyTimer.Reset()
                        
                except Exception as e:
                    print(e)
            
            except Exception as e:
                print(e)