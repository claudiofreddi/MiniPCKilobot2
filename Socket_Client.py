import socket
import threading
import time

# Choosing Nickname
nickname = input("Choose your nickname: ")
ServerIP = '127.0.0.1'
ServerPort = 55555
client = None

# Listening to Server and Sending Nickname
def receive():
    global client
    IsConnected = False
    while True:
        
        try:
            if (IsConnected == False):
                # Connecting To Server
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((ServerIP, ServerPort))
                IsConnected = True
        
        
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        except:
            IsConnected = False
            # Close Connection When Errorclaudio
            print("An error occured! Retry in 15 sec..")
            client.close()
            time.sleep(15) #Wait 30 sec and retry
            #break
        
# Sending Messages To Server
def write():
    global client
    while True:
        #message = '{}: {}'.format(nickname, input(''))
        message = '{}'.format(input(''))
        client.send(message.encode('ascii'))   
        
        
        
# Starting Threads For Listening And Writing
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
        
        
        
        
         