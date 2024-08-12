import socket
import struct
from Socket_ConsoleLog import * 


class Socket_SendReceive(Common_LogConsoleClass):

    def send_msg(self,sock:socket, msg1, msg2=b''):
        try:
            msg = struct.pack('>LL', len(msg1), len(msg2)) + msg1 + msg2
            sock.sendall(msg)
        except Exception as e:
            self.LogConsole("Socket_SendReceive Error in send_msg  " + str(e))

    def recv_msg(self,sock:socket):
    # try:
        # Read message length and unpack it into an integer
        raw_msglen1, retval = self.recvall(sock, struct.calcsize(">L"))
        # if not retval :
        #     return b'',b'', False
        if not raw_msglen1:
            return b'',b'', False
        msglen1 = struct.unpack('>L', raw_msglen1)[0]
        
        raw_msglen2, retval = self.recvall(sock, struct.calcsize(">L"))
        # if not retval :
        #     return b'',b'', False
        if not raw_msglen2:
            return b'',b'',False
        msglen2 = struct.unpack('>L', raw_msglen2)[0]
        
        msg1, retval = self.recvall(sock, msglen1)
        # if not retval :
        #     return b'',b'', False
                    
        msg2, retval = self.recvall(sock, msglen2)
        # if not retval :
        #     return b'',b'', False
                    
        # Read the message data
        return msg1, msg2,True
    
    # except Exception as e:
    #     self.LogConsole("Socket_SendReceive Error in recv_msg  " + str(e))
    #     time.sleep(3)
    #     return b'',b'',False

    def recvall(self,sock:socket, n):
    #try:
        # Helper function to recv n bytes or return None if EOF is hit
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return b'',False
            data.extend(packet)
        return data, True
    # except Exception as e:
    #     self.LogConsole("Socket_SendReceive Error in recvall  " + str(e))
    #     time.sleep(3)
    #     return b'',False