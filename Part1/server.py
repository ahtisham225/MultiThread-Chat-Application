'''
This module defines the behaviour of server in your Chat Application
'''
import getopt
import socket
import sys
import threading
import util
from collections import OrderedDict


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

    def start(self):
        '''
        Main loop.
        continue receiving messages from Clients and processing it
        '''

        #clients variable dictionary to store username as key and address as value 
        clients ={}

        #starting to recieve the data
        while True:
            packet ,addr=self.sock.recvfrom(4096)
            _,_,message,_=util.parse_packet(packet.decode('utf-8'))
            
            #spliting the recieving message to check the first entry of list 

            temp = message.split()

            #whatToDo will check what user did ( joined,messaged,etc.)
            whatToDo = temp[0]
            
            #if User Joins
            if(whatToDo=='join'):
                
                #if clients have not reached the MAX_NUMBER
                if(len(clients) < util.MAX_NUM_CLIENTS):
                   
                   #if the new username not exists in saved clients
                   #adding the new user in clients dictionary
                    if temp[-1] not in clients:
                        print(whatToDo+': '+temp[-1])
                        clients[temp[-1]] = addr
                    
                    #if username already exists
                    else:
                        user_unavailable = util.get_work_done('err_username_unavailable',2,)
                        self.sock.sendto(user_unavailable.encode('utf-8'),addr)
                
                #if clients have reached the MAX_NUMBER 
                else:
                        server_full = util.get_work_done('err_server_full',2,)
                        self.sock.sendto(server_full.encode('utf-8'),addr)

            #if user request list    
            elif(whatToDo=='request_users_list'):                            
                
                #printing request_users_list: username(who input list) on server
                print(whatToDo + ': ' + util.get_client(addr,clients))
                
                #Sorting the clients
                sortedDict=OrderedDict(sorted(clients.items()))
                sortedNames = sortedDict.keys()
                
                #joining the clients as a string
                listToStr = ' '.join([str(elem) for elem in sortedNames]) 
                
                #sending the string to make_message and make_packet
                response = util.get_work_done('response_users_list',3,listToStr)
                self.sock.sendto(response.encode('utf-8'),addr)
            
            #if user sends a message
            elif(whatToDo=='send_message'):
                #temp_var is input of user after the clients
                #for example if user intered msg 2 a b hey
                #then 4 index is a
                temp_var = 4

                #printing the msg: username who messages
                print_server = 0

                #list started from the first username
                new_list = temp[4:]

                #msg 2 talal error handled 
                if(int(temp[3])>len(new_list)):
                   
                    print('disconnected: '+util.get_client(addr,clients)+' sent unknown command')
                    sending = util.get_work_done('err_unknown_message',2,)
                    self.sock.sendto(sending.encode('utf-8'),addr)
                    
                    #client deleted after Unknown message error
                    clients.pop(util.get_client(addr,clients))
                
                #if there is no message error
                else:
                    for i in range(int(temp[3])):
                        
                        #if the reciepent username is in clients
                        if temp[temp_var] in clients:
                            
                            if(print_server == 0):
                                    print('msg: '+util.get_client(addr,clients))
                                    print_server = 1
                            
                            #sending message
                            sending_message = temp[4+int(temp[3]):]
                            listToStr = ' '.join([str(elem) for elem in sending_message])
                            listToStr = util.get_client(addr,clients) + ': ' + listToStr
                            forward = util.get_work_done('forward_message',4,listToStr)
                            self.sock.sendto(forward.encode('utf-8'),clients[temp[temp_var]])
                        
                        #if reciepent not exists
                        else:
                            print('msg: '+util.get_client(addr,clients)+' to non-existent user '+temp[temp_var])
                        temp_var = temp_var +1  

                        #if user sent file   
            elif(whatToDo == 'send_file'):
                
                #index for first client temp_var 
                temp_var = 4

                #printing server only once
                print_server = 0

                #new_list form starting from first client
                new_list = temp[4:]

                #handling file 2 a hello.txt error 
                if(int(temp[3])>=len(new_list)):
                   
                    print('disconnected: '+util.get_client(addr,clients)+' sent unknown command')
                    sending = util.get_work_done('err_unknown_message',2,)
                    self.sock.sendto(sending.encode('utf-8'),addr)
                    
                    #deleting client giving unknown message error
                    clients.pop(util.get_client(addr,clients))
                
                #if no error in file
                else:

                    #looping through clients
                    for i in range(int(temp[3])):
                        #if reciepent client exists
                        if temp[temp_var] in clients:
                      
                            if(print_server == 0):
                                print('file: '+util.get_client(addr,clients))
                                print_server = 1
                      
                            sending_message = temp[4+int(temp[3]):]
                            listToStr = ' '.join([str(elem) for elem in sending_message])
                            listToStr = util.get_client(addr,clients) + ' ' + listToStr
                            forward = util.get_work_done('forward_file',4,listToStr)
                            self.sock.sendto(forward.encode('utf-8'),clients[temp[temp_var]])
                    
                        #non existent user
                        else:
                            print('msg: '+util.get_client(addr,clients)+' to non-existent user '+temp[temp_var])
                        temp_var = temp_var +1  

                #if username entered quit
            elif(whatToDo == 'disconnect'):
                    print('disconnected: '+util.get_client(addr,clients))
                    sending = util.get_work_done('disconnect',1,util.get_client(addr,clients))
                    self.sock.sendto(sending.encode('utf-8'),addr)
                    
                    #deleting client as he entered quit
                    clients.pop(util.get_client(addr,clients))        
                # raise NotImplementedError

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
