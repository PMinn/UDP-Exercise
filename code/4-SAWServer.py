####################################################
#  Network Programming - Unit 5  User Datagram Protocol          
#  Program Name: 4-SAWServer.py                                      			
#  This program builds a server based on SAWSocket.           		
#  2021.07.21                                                 									
####################################################
import SAWSocket

PORT = 8888
BUF_Size = 1024

# Create a SAWSocket Server 
server = SAWSocket.SAWSocket(4, 8888)		# Listen on port 8888
server.accept()
	
for i in range(100):
	msg = server.receive()
	print('Receive message: ' + msg.decode('utf-8'))
	
server.close()
# end of main