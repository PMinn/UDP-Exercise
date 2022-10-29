####################################################
#  Network Programming - Unit 5  User Datagram Protocol          
#  Program Name: 4-SAWClient.py                                      			
#  This program build a client based on SAWSocket.           		
#  2021.07.21                                             									
####################################################
import SAWSocket
import sys
import time

PORT = 8888
BUF_Size = 1024


client = SAWSocket.SAWSocket(4, PORT, "127.0.0.1")
client.connect()
	
for i in range(400):
	msg = 'Test message ' + str(i)
	client.send(msg.encode('utf-8'))
	# time.sleep(1)
client.close()

# end of main