'''
This file contains basic utility functions that you can use.
'''
import binascii
import random

MAX_NUM_CLIENTS = 10
TIME_OUT = 2 # 500ms
NUM_OF_RETRANSMISSIONS = 3
CHUNK_SIZE = 1400 # 1400 Bytes
Random_Seq_No = random.randint(0,500) #Starting Sequence Number
checkMsg = True
checkNonexistent= True
sendFile = False
Num_of_clients = 0
name=''
printt = True
recieved = True
fileRecieved = []

def validate_checksum(message):
    '''
    Validates Checksum of a message and returns true/false
    '''
    try:
        msg, checksum = message.rsplit('|', 1)
        msg += '|'
        return generate_checksum(msg.encode()) == checksum
    except BaseException:
        return False


def generate_checksum(message):
    '''
    Returns Checksum of the given message
    '''
    return str(binascii.crc32(message) & 0xffffffff)


def make_packet(msg_type="data", seqno=0, msg=""):
    '''
    This will add the header to your message.
    The formats is `<message_type> <sequence_number> <body> <checksum>`
    msg_type can be data, ack, end, start
    seqno is a packet sequence number (integer)
    msg is the actual message string
    '''

    body = "%s|%d|%s|" % (msg_type, seqno, msg)
    checksum = generate_checksum(body.encode())
    packet = "%s%s" % (body, checksum)
    return packet


def parse_packet(message):
    '''
    This function will parse the packet in the same way it was made in the above function.
    '''
    pieces = message.split('|')
    msg_type, seqno = pieces[0:2]
    checksum = pieces[-1]
    data = '|'.join(pieces[2:-1])
    return msg_type, seqno, data, checksum


def make_message(msg_type, msg_format, message=None):
    '''
    This function can be used to format your message according
    to any one of the formats described in the documentation.
    msg_type defines type like join, disconnect etc.
    msg_format is either 1,2,3 or 4
    msg is remaining. 
    '''
    if msg_format == 2:
        msg_len = 0
        return "%s %d" % (msg_type, msg_len)
    if msg_format in [1, 3, 4]:
        msg_len = len(message)
        return "%s %d %s" % (msg_type, msg_len, message)
    return ""


# get_client function will take the address and clients dictionary and will
# return the client key(client name )
def get_client(address, clients):
    for name, addresses in clients.items():
         if address == addresses:
             return name
 
    return "key doesn't exist"




# get_work_done will make_message and then make_packet both
def get_work_done(ToDo, type_, msg=None):
    typeMsg = make_message(ToDo,type_, msg)

    packet = make_packet(msg = typeMsg)
    return packet

def start_packet(self):
    start_packet = make_packet('start', Random_Seq_No,)
    self.sock.sendto(start_packet.encode('utf-8'),(self.server_addr,self.server_port))

def end_packet(self):
    packet = make_packet('end',Random_Seq_No)
    self.sock.sendto(packet.encode('utf-8'),(self.server_addr,self.server_port))
def ack_packet_client(self):
    packet = make_packet('ack',Random_Seq_No)
    self.sock.sendto(packet.encode('utf-8'),(self.server_addr,self.server_port))

def ack_packet(self,send_seq,addr):
    ack_packet = make_packet('ack',send_seq)
    self.sock.sendto(ack_packet.encode('utf-8'),addr)

def start_pack_serv(self,addr,seq_no):
    start_packet = make_packet('start', seq_no)
    self.sock.sendto(start_packet.encode('utf-8'),addr)

def end_pack_serv(self,addr,seq_no):
    start_packet = make_packet('end', seq_no)
    self.sock.sendto(start_packet.encode('utf-8'),addr)

    
