####################################################
#  D1014636 潘子珉                                      									
####################################################
import SAWSocket
import sys
import time

import eel
eel.init('gui', allowed_extensions=['.js', '.html'])

PORT = 8888
BUF_Size = 1024

@eel.expose
def main(slidingWindow, numberOfPack): 
	client = SAWSocket.SAWSocket(slidingWindow, PORT, "127.0.0.1")
	client.connect()
	for i in range(numberOfPack):
		msg = 'Test message ' + str(i)
		eel.writeClientMessage(0,msg)
		client.send(msg.encode('utf-8'))
# time.sleep(5)
# msg = 'Test message 999'
# client.send(msg.encode('utf-8'))
	client.close()

# end of main

eel.start('client.html', size=(500, 500),port=0)  # Start
