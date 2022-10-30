####################################################
#  D1014636 潘子珉                                      									
####################################################
import SAWSocket
import sys
import time

PORT = 8888
BUF_Size = 1024


client = SAWSocket.SAWSocket(3, PORT, "127.0.0.1")
client.connect()
	
for i in range(30):
	msg = 'Test message ' + str(i)
	client.send(msg.encode('utf-8'))
client.close()

# end of main