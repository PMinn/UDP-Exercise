####################################################
#  D1014636 潘子珉                                      									
####################################################
import SAWSocket
import math
import eel
eel.init('gui', allowed_extensions=['.js', '.html'])

PORT = 8888
BUF_Size = 1024


@eel.expose
def main(slidingWindow, numberOfPack): 
	# Create a SAWSocket Server 
	server = SAWSocket.SAWSocket(slidingWindow, 8888)		# Listen on port 8888
	server.accept()

	for i in range(math.ceil(numberOfPack/slidingWindow)):
		try:
			msg = server.receive()
			msg = msg.decode('utf-8')
			print('Receive message: ' + msg)
			eel.writeServerMessage(msg,"")
		except Exception:
			print("timeout")
	server.close()
# end of main



eel.start('server.html', size=(500, 500),port=0)  # Start
