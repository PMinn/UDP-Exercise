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
	client = SAWSocket.SAWSocket(2, PORT, "127.0.0.1")
	client.connect()
	
	for i in range(10):
		msg = 'Test message ' + str(i)
		client.send(msg.encode('utf-8'))

	client.close()

# end of main

if __name__ == '__main__':
	main()
