'''
This module defines the behaviour of server in your Chat Application
'''
import getopt
import socket
import sys
import threading
import util
from collections import OrderedDict
from queue import Queue
from threading import Thread

class Server:
    '''
    This is the main Server Class. You will to write Server code inside this class.
    '''
    def __init__(self, dest, port, window):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(None)
        self.sock.bind((self.server_addr, self.server_port))
        self.window = window
        self.que = Queue()
        self.clients = {}
        self.msg = ''
        self.sendClients = []
        self.br = True
        self.needAddr = self.server_addr
        self.seq_no=0
    
    def start(self):
        '''
        Main loop.
        continue receiving messages from Clients and processing it
        '''

        #clients variable dictionary to store username as key and address as value 
        

        #starting to recieve the data
        while True:
            packet ,addr=self.sock.recvfrom(4096)
            a,b,message,_=util.parse_packet(packet.decode('utf-8'))
            send_seq = int(b) + 1

           
           
            if(a == 'start'):

                #recieving Start packet from client and resetting all the requried variables.
                util.ack_packet(self,send_seq,addr)
                self.msg = ''
                util.checkMsg = True
                util.checkNonexistent = True
                while not self.que.empty():
                    self.que.get()
                util.Num_of_clients = 0
                util.sendFile = False
                self.sendClients = []
                util.recieved = True
                util.printt = True

            elif( a == 'end'):
                #recieving End Packet
                util.ack_packet(self,send_seq,addr)
                util.sendFile = False

           
            elif( a == 'data'):
                #if Recieved Data from the client
                util.ack_packet(self,send_seq,addr)
                
            #spliting the recieving message to check the first entry of list 
                temp = message.split()

            #whatToDo will check what user did ( joined,messaged,etc.
                whatToDo = temp[0]
                    
                
            
            #if User Joins
                if(whatToDo=='join'):
                    
                #if clients have not reached the MAX_NUMBER
                    if(len(self.clients) < util.MAX_NUM_CLIENTS):
                   
                   #if the new username not exists in saved clients
                   #adding the new user in clients dictionary
                        if temp[-1] not in self.clients:
                            print(whatToDo+': '+temp[-1])
                            self.clients[temp[-1]] = addr
                            
                    #if username already exists
                        else:
                            user_unavailable = util.make_message('err_username_unavailable',2,)
                            packet = util.make_packet('data',send_seq,user_unavailable)    
                            self.sock.sendto(packet.encode('utf-8'),addr)
                
                #if clients have reached the MAX_NUMBER 
                    else:
                        server_full = util.make_message('err_server_full',2,)
                        packet = util.make_packet('data',send_seq,server_full)
                        self.sock.sendto(packet.encode('utf-8'),addr)

            #if user request list    
                elif(whatToDo=='request_users_list'):               
                
                #printing request_users_list: username(who input list) on server
                    print(whatToDo + ': ' + util.get_client(addr,self.clients))

                
                #Sorting the clients
                    sortedDict=OrderedDict(sorted(self.clients.items()))
                    sortedNames = sortedDict.keys()
                
                #joining the clients as a string
                    listToStr = ' '.join([str(elem) for elem in sortedNames]) 
                
                #Sending Start Packet
                    util.start_pack_serv(self,addr,send_seq)
                    
                #sending the string to make_message and make_packet
                    response_message = util.make_message('response_users_list',3,listToStr)
                    
                    response = util.make_packet('data',send_seq,response_message)
                    self.sock.sendto(response.encode('utf-8'),addr)
                #Sending End Packet
                    util.end_pack_serv(self,addr,send_seq)
            
            #if user sends a message
                elif(whatToDo=='send_message'):
                #temp_var is input of user after the clients
                #for example if user intered msg 2 a b hey
                #then 4 index is a
                    temp_var = 4

                #printing the msg: username who messages
                    print_server = 0

                    
                    for i in range(int(temp[3])):

                    
                    #if the reciepent username is in clients
                        if temp[temp_var] in self.clients:
                            
                            if(print_server == 0 and util.checkMsg):
                                    print('msg: '+util.get_client(addr,self.clients))
                                    print_server = 1
                                    util.checkMsg = False

                        
        #sending message    
                            #Sending Start Packet
                            util.start_pack_serv(self,self.clients[temp[temp_var]],send_seq)
                            #Sending Message
                            sending_message = temp[4+int(temp[3]):]
                            ack_packet = util.make_packet('ack', send_seq)
                            self.sock.sendto(ack_packet.encode('utf-8'),addr)
                            listToStr = ' '.join([str(elem) for elem in sending_message])
                            listToStr = util.get_client(addr,self.clients) + ': ' + listToStr
                            forward = util.make_message('forward_message',4,listToStr)
                            while forward:
                                chunk = forward[0:util.CHUNK_SIZE]
                                forward = forward[util.CHUNK_SIZE:]
                                self.que.put(chunk)
                            while not self.que.empty():    
                                forwardPacket = util.make_packet('data',send_seq,self.que.get())
                                self.sock.sendto(forwardPacket.encode('utf-8'),self.clients[temp[temp_var]])
                            #Sending End Packet
                            util.end_pack_serv(self,self.clients[temp[temp_var]],send_seq)
                            #if reciepent not exists
                        else:
                            if(util.checkNonexistent):
                                print('msg: '+util.get_client(addr,self.clients)+' to non-existent user '+temp[temp_var])
                                util.checkNonexistent = False
                        temp_var = temp_var +1      

                        #if user Entered Quit
                elif(whatToDo == 'disconnect'):
                    #Sending Start Packet
                    util.start_pack_serv(self,addr,send_seq)
                    #Sending Disconnect Packet
                    print('disconnected: '+util.get_client(addr,self.clients))
                    sending = util.make_message('disconnect',1,util.get_client(addr,self.clients))
                    while sending:
                        chunk = sending[0:util.CHUNK_SIZE]
                        sending = sending[util.CHUNK_SIZE:]
                        self.que.put(chunk)
                    packet = util.make_packet('data',send_seq,self.que.get())
                    self.sock.sendto(packet.encode('utf-8'),addr)
                     #Sending end packet
                    util.end_pack_serv(self,addr,send_seq)
                    #deleting client as he entered quit
                    self.clients.pop(util.get_client(addr,self.clients))

                #Sending File
                elif(whatToDo == 'send_file'):    
                #index for first client temp_var 
                    temp_var = 4

                    util.start_pack_serv(self,addr,send_seq)
                    for i in range(int(temp[3])):
                        #if reciepent client exists
                        
                        if temp[temp_var] in self.clients:
                      
                            if(util.printt):
                                print('file: '+util.get_client(addr,self.clients))
                                print_server = 1
                                util.printt = False
                            
                            #Sending Start packet
                            util.start_pack_serv(self,self.clients[temp[temp_var]],send_seq)
                            #Sending Message
                            sending_message = temp[4+int(temp[3]):]
                            listToStr = ' '.join([str(elem) for elem in sending_message])
                            listToStr = util.get_client(addr,self.clients) + ' ' + listToStr
                            forward = util.get_work_done('forward_file',4,listToStr)
                            self.sock.sendto(forward.encode('utf-8'),self.clients[temp[temp_var]])
                            #Sending Recieve Packet 
                            util.end_pack_serv(self,self.clients[temp[temp_var]],send_seq)
                        #non existent user
                        else:
                            if(util.recieved):
                                print('file: '+util.get_client(addr,self.clients)+' to non-existent user '+temp[temp_var])
                                util.recieved = False
                        temp_var = temp_var +1
                
                
        

# Do not change this part of code

if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our module completion
        '''
        print("Server")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW | --window=WINDOW The window size, default is 3")
        print("-h | --help Print this help")

    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "p:a:w", ["port=", "address=","window="])
    except getopt.GetoptError:
        helper()
        exit()

    PORT = 15000
    DEST = "localhost"
    WINDOW = 3

    for o, a in OPTS:
        if o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a
        elif o in ("-w", "--window="):
            WINDOW = a

    SERVER = Server(DEST, PORT,WINDOW)
    try:
        SERVER.start()
        
    except (KeyboardInterrupt, SystemExit):
        exit()
