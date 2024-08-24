# MiniPCKilobot

@2024 Freddi Claudio
New Version of Robot Kilobot based on Mini PC and 2 Arduinos

## Classe Client - Comune

### Inizializzazione

```py
def __init__():

    self.ServiceParamStdBy =  "STANDBY"
    self.LocalParamSleepTime = "SLEEPTIME"
    self.LocalCommand_TESTCLIENT = "TESTCLIENT"

```

### Messaggi dal server

```py
def Client_Listening_Task(self)

    # CLIENT LOGIN and rgistration
    if (ReceivedMessage.Message == Socket_ClientServer_Local_Commands.SOCKET_LOGIN_MSG):
        ....

        LocalListOfStatusParams.List
        LocalListOfCommands.List


    # CLIENT SPECIFIC TOPIC (PARAMS UPDATE AND COMMANDS)
    LocalTopicTest = TopicManager(ReceivedMessage.Topic)
        
        def Execute_Service_SpecificCommand()  #local command
            def After_Execute_Service_SpecificCommands() #child command (oevrrride)
        
        SendToServer(ObjToServer)       #notification to server
        SendToServer(ObjToReplyTopic)   #notification to replyto

    #Chiama il metodo del child
    def OnClient_Receive()   #all commands to child



```

## Classe Server

### Inizializzazione

```py
def __init__():

    self.ServerListOfStatusParams = StatusParamList()
    self.ServerListOfCommands = ServiceCommandList()
    self.Standard_Topics_For_Server = Topics_Standard_For_Service(self.ServiceName)

    self.Connect()    
```

```py
# Receiving New Clients / Listening Function
def WaitingForNewClient(self)

    while True:
        client, address = self.ServerConnection.accept()
```

```py
# Handling Messages From Clients
def handle(self,client:socket):

    CurrClientObject,retval = self.GetClientObject(client)

    while True:

        ReceivedEnvelope, AdditionaByteData, retval = self.GetFromClient(client)

        if (ReceivedEnvelope.To == SocketMessageEnvelopeTargetType.BROADCAST):   
            #Broadcast requested by client
            self.broadcastObj(ReceivedMessage, ReceivedEnvelope.From)
        else:
            #By Topic
            self.BroadCastMessageByTopic(ReceivedMessage,AdditionaByteData)

        if (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_REGISTER):
        elif (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_SUBSCRIBE):
        elif (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_CLIENT_PARAM_SERVER_REGISTER):  
        elif (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_CLIENT_COMMAND_SERVER_REGISTER):


```