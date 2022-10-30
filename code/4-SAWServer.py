####################################################
#  D1014636 潘子珉                                      									
####################################################
import SAWSocket

PORT = 8888
BUF_Size = 1024

# Create a SAWSocket Server 
server = SAWSocket.SAWSocket(3, 8888)		# Listen on port 8888
server.accept()
	
for i in range(10):
	msg = server.receive()
	print('Receive message: ' + msg.decode('utf-8'))
	
server.close()
# end of main