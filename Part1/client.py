'''
This module defines the behaviour of a client in your Chat Application
'''
import sys
import getopt
import socket
import random
from threading import Thread
import os
import util
import time

'''
Write your code inside this class. 
In the start() function, you will read user-input and act accordingly.
receive_handler() function is running another thread and you have to listen 
for incoming messages in this function.
'''

class Client:
    '''
    This is the main Client Class. 
    '''
    def __init__(self, username, dest, port, window_size):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(None)
        self.sock.bind(('', random.randint(10000, 40000)))
        self.name = username
        self.window = window_size
        self.sent = True
        self.disconnect = True
    def start(self):
        '''
        Main Loop is here
        Start by sending the server a JOIN message.
        Waits for userinput and then process it
        '''

        #printing the name of username
        print(self.name)

        #making packet for join first make_message then make_packet
        JoinPacket = util.get_work_done('join',1,self.name)

        #sending join request to server
        self.sock.sendto(JoinPacket.encode('utf-8'), (self.server_addr, self.server_port))

        #self.disconnect is true
        while self.disconnect:
            time.sleep(.1)
            if(self.disconnect):

                #inputing in the console by user
                console_input=input("")

                #spliting user input 
                temp = console_input.split()

                #whatToDo tells the required work to do
                whatToDo = temp[0]

                #if user entered list
                if(console_input == 'list'):

                        #making_message and make_packet of request_users_list
                        sending= util.get_work_done('request_users_list',2,)
                        self.sock.sendto(sending.encode('utf-8'), (self.server_addr, self.server_port))
                
                #if user entered msg
                elif (whatToDo == "msg"):
                        #making_message and make_packet of send_message and sending it 
                        sending = util.get_work_done('send_message', 4,console_input)
                        self.sock.sendto(sending.encode('utf-8'), (self.server_addr, self.server_port))
                
                #if user entered file 
                elif (whatToDo == "file"):
                        
                        #if user enter file 2 a
                        #it will cause an error 
                        #it will handle that
                        new_list = temp[2:]
                        if(int(temp[1]) >= len(new_list)):
                            sending = util.get_work_done('send_file',4,console_input)
                            self.sock.sendto(sending.encode('utf-8'), (self.server_addr, self.server_port))     
                        
                        #sending the file to server
                        else:
                            console_input = console_input + ' '
                            sending_file = open(temp[-1],'r')
                            for each in sending_file:
                                console_input = console_input + each
                            sending = util.get_work_done('send_file',4,console_input)
                            self.sock.sendto(sending.encode('utf-8'), (self.server_addr, self.server_port))     
                
                #when user enter help
                elif(console_input == 'help'):
                    print("Message: msg <number_of_users> <username1> <username2> ... <message>")
                    print("Available Users: list")
                    print("File Sharing: file <>number_of_users> <username1> <username2> ... <filename> ")
                    print("Quit: quit")

                #when user enter quit
                elif(console_input == 'quit'):
                    sending = util.get_work_done('disconnect',1,self.name)
                    self.sock.sendto(sending.encode('utf-8'), (self.server_addr, self.server_port))
                
                #for wrong input commands
                else:
                    print('incorrect userinput format')
        self.sock.close()



        # util.make_message()
        # raise NotImplementedError
            

    def receive_handler(self):
        '''
        Waits for a message from server and process it accordingly
        '''
        while self.disconnect:
            bitsMessage=self.sock.recv(4096)
            _,_,message,_=util.parse_packet(bitsMessage.decode('utf-8'))
           
           #spliting the message from server
            temp = message.split()
           
           #whatToDo will tell the client to what to do with what server is telling
            whatToDo = temp[0]

            #when server send response_users_list
            if(whatToDo == 'response_users_list'):

                #response_users_list will print the active users on clients screen
                show = ' '.join([str(elem) for elem in temp[2:]]) 
                print('list:',show)

            #when user take forward_message from server
            elif(whatToDo == 'forward_message'):

                #forward_message from server will now join the splited temp and 
                #will print the message on clients screen

                show = ' '.join([str(elem) for elem in temp[2:]]) 
                print('msg:',show)

            #when server send forward_file to client
            elif(whatToDo == 'forward_file'):
               
                #making the new file of required content
                file_name = temp[3]
                new_file_name = self.name + '_' + file_name
                sender_client = temp[2]
                show = ' '.join([str(elem) for elem in temp[4:]]) 
                f = open(new_file_name, 'wt')
                f.write(show)
                f.close()

                #printing the file: sender: file_name on client screen
                print('file: '+sender_client+': '+file_name)

            #when server has no username available will send err_username_unavailable to client
            elif(whatToDo == 'err_username_unavailable'):

                print('disconnected: username not available')
                self.disconnect=False

            #when server is full    
            elif(whatToDo == 'err_server_full'):
                
                print('disconnected: server full')
                self.disconnect=False
            
            #when message is unknown
            elif(whatToDo == 'err_unknown_message'):
                
                print('disconnected: server received an unknown command')
                self.disconnect=False
            
            #when user enter quit and server sends disconnect command to client
            elif(whatToDo == 'disconnect'):
                print('quitting')
                self.disconnect=False
                
        self.sock.close()
        # raise NotImplementedError


# Do not change this part of code
if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our Client module completion
        '''
        print("Client")
        print("-u username | --user=username The username of Client")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW_SIZE | --window=WINDOW_SIZE The window_size, defaults to 3")
        print("-h | --help Print this help")
    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "u:p:a:w", ["user=", "port=", "address=","window="])
    except getopt.error:
        helper()
        exit(1)

    PORT = 15000
    DEST = "localhost"
    USER_NAME = None
    WINDOW_SIZE = 3
    for o, a in OPTS:
        if o in ("-u", "--user="):
            USER_NAME = a
        elif o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a
        elif o in ("-w", "--window="):
            WINDOW_SIZE = a

    if USER_NAME is None:
        print("Missing Username.")
        helper()
        exit(1)

    S = Client(USER_NAME, DEST, PORT, WINDOW_SIZE)
    try:
        # Start receiving Messages
        T = Thread(target=S.receive_handler)
        T.daemon = True
        T.start()
        # Start Client
        S.start()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
