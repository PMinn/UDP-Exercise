####################################################
#  Network Programming - Unit 5  User Datagram Protocol          
#  Program Name: 4-SAWClient.py                                      			
#  This program build a client based on SAWSocket.           		
#  2021.07.21                                             									
####################################################
import SAWSocket
import sys

PORT = 8888
BUF_Size = 1024

def main():
	if(len(sys.argv) < 2):
		print("Usage: python3 3-SAWClient.py ServerIP\n")
		exit(1)

	# Create a SAWSocket client 
	client = SAWSocket.SAWSocket(PORT, sys.argv[1])
	client.connect()
	
	for i in range(10):
		msg = 'Test message ' + str(i)
		client.send(msg.encode('utf-8'))

	client.close()

# end of main

if __name__ == '__main__':
	main()
