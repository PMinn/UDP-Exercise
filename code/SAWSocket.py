####################################################
#  Network Programming - Unit 5  User Datagram Protocol          
#  Program Name: SAWSocket.py                                      			
#  This program implements stop and wait protocol based on UDP.          		
#  2021.07.19                                                 									
####################################################
import socket
import threading
import time
import struct

import random

BufSize = 1024
DEBUG = True

class SAWSocket:
	def __init__(self,  port, addr = ''):			# addr == '' if server
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		if(addr == ''):		# Server side
			self.isServer = True
			self.PeerAddr = ''
			self.PeerPort = 0
			# Bind 	on any incoming interface with port, '' is any interface
			self.socket.bind(('', port))
		else:					# Client side
			self.isServer = False
			self.PeerAddr = socket.gethostbyname(addr)
			self.PeerPort = port
		# end if

		# Variables share between process and daemon
		# these variable must be accessed in the critical section
		self.CS_busy = False		# True if CS_buf contains data
		self.CS_sn_send = 0		# sequence number for send DATA 
		self.CS_sn_receive = 0	# sequence number for next DATA
		self.CS_ack_sn = 0			# sequence number for acknowledgement
		self.CS_running = True	# True after SAWsocket is active (created)
		self.CS_buf = ''				# for message buffer
		self.CS_length = 0			# received message length

		# constant
		self.SocketIdle = float(1.0)			# 1 sec
		self.SleepIdle = float(0.1)				# 0.1 sec
		self.BufSize = BufSize
		self.lock = threading.Lock()				# for synchronization
		self.condition = threading.Condition()
		self.ReceiveD = 0						# receive daemon
	# end of __init__()
	
	def get_sn_receive(self):
		self.lock.acquire()
		sn_receive = self.CS_sn_receive
		self.lock.release()
		return sn_receive
	# end of get_sn_receive()
	
	def get_sn_send(self):
		self.lock.acquire()
		sn_send = self.CS_sn_send
		self.lock.release()
		return sn_send
	# end of get_sn_send()
	
	def add_sn_receive(self):
		self.lock.acquire()
		self.CS_sn_receive = (self.CS_sn_receive + 1) % 2
		sn_receive = self.CS_sn_receive
		self.lock.release()
		return sn_receive
	# end of add_sn_receive()
	
	def add_sn_send(self):
		self.lock.acquire()
		self.CS_sn_send = (self.CS_sn_send + 1) % 2
		sn_send = self.CS_sn_send
		self.lock.release()
		return sn_send
	# end of add_sn_send()
	
	def receive_ack(self, sn):
		self.lock.acquire()
		self.CS_ack_sn = sn
		with self.condition:
			self.condition.notify()
		self.lock.release()
	# end of receive_ack()
	
	def get_ack_sn(self):
		self.lock.acquire()
		ack_sn = self.CS_ack_sn
		self.lock.release()
		return ack_sn
	# end of get_ack_sn()
	
	def has_data(self):
		self.lock.acquire()
		busy = self.CS_busy
		self.lock.release()
		return busy
	# end of has_data()
	
	def copy2CS_buf(self, src_buf):
		self.lock.acquire()
		self.CS_buf = src_buf
		self.CS_busy = True
		self.lock.release()
	# end of copy2CS_buf()
	
	def copy4CS_buf(self):
		self.lock.acquire()
		ret_msg = self.CS_buf
		self.CS_busy = False
		self.lock.release()
		return ret_msg
	# end of copy4CS_buf()
	
	def  wait_data(self):
		with self.condition:
			self.condition.wait()
	# end of wait_data()
	
	def data_ready(self):
		with self.condition:
			self.condition.notify()
	# end of data_ready()
	
	def wait_ack(self):
		with self.condition:
			self.condition.wait(self.SocketIdle)
	# end of wait_ack()
	
	def is_running(self):
		self.lock.acquire()
		running = self.CS_running
		self.lock.release()
		return running
	# end of is_running()
	
	def accept(self):
		if(not self.isServer):
			print('accept() can only be called by server!!')
			exit(1)
		# end if
		
		# Wait for SYN
		recv_msg, (rip, rport) = self.socket.recvfrom(self.BufSize)
		self.PeerAddr = rip
		self.PeerPort = rport
		if(DEBUG):
			print('Connect from IP: ' + str(self.PeerAddr) + ' port: ' + str(self.PeerPort))
			
		# Send SYN/ACK
		reply = 'SYN/ACK'
		self.socket.sendto(reply.encode('utf-8'), (self.PeerAddr, self.PeerPort))
		
		# Wait for ACK
		recv_msg, (rip, rport) = self.socket.recvfrom(self.BufSize)

		if(DEBUG):
			print('Connection from: ' + str(self.PeerAddr) + ':' + str(self.PeerPort) + ' established')
		
		# Create ReceiveD
		self.ReceiveD = ReceiveD(self.socket, self.PeerAddr, self.PeerPort, self)
	# end of accept()
	
	def connect(self):
		if(self.isServer):
			print('connect() can only be called by client!!')
			exit(1)	
		# end if
		
		# send SYN
		message = 'SYN'
		self.socket.sendto(message.encode('utf-8'), (self.PeerAddr, self.PeerPort))
		if(DEBUG):
			print('Connect to: ' + str(self.PeerAddr) + ' port: ' + str(self.PeerPort))
		
		# Receive SYN/ACK
		recv_msg, (rip, rport) = self.socket.recvfrom(self.BufSize)
		
		# send ACK
		message = 'ACK'
		self.socket.sendto(message.encode('utf-8'), (self.PeerAddr, self.PeerPort))
		if(DEBUG):
			print('Connection to: ' + str(self.PeerAddr) + ':' + str(self.PeerPort) + ' established')
		
		# Create ReceiveD
		self.ReceiveD = ReceiveD(self.socket, self.PeerAddr, self.PeerPort, self)
	# end of connect()
	
	def send(self, buf):
		length = len(buf)
		sn_send = self.get_sn_send()
		msg_type = ord('M')
		value = (msg_type, sn_send, buf)
		msg_format = '!' + 'B I ' + str(length) + 's'
		s = struct.Struct(msg_format)
		packed_data = s.pack(*value)
		
		success = False
		while(not success):
			# send message
			self.socket.sendto(packed_data, (self.PeerAddr, self.PeerPort))

			# wait ACK
			self.wait_ack()
			
			ack_sn = self.get_ack_sn()
			if(ack_sn != sn_send):
				success = True
			elif(DEBUG):
				print('Send failed !! SN = ' + str(sn_send))
		# end while
	# end of send()
	
	def receive(self):
		sn = self.get_sn_receive()
		if(not self.has_data()):
			self.wait_data()
		ret_msg = self.copy4CS_buf()
		self.add_sn_receive()
		return ret_msg
	# end of receive()
	
	def close(self):
		# Send Finish
		sn = self.get_sn_send()
		msg_format1 = '!' + 'B I ' 				# !: network order
		s = struct.Struct(msg_format1)
		value = (ord('F'), sn)
		packed_data = s.pack(*value)
		self.socket.sendto(packed_data, (self.PeerAddr, self.PeerPort))	
		self.CS_running = False
		time.sleep(1)
		self.socket.close()
		self.ReceiveD.join()						# Waiting receive daemon closed
	# end of close()
# end of class SAWSocket

class ReceiveD(threading.Thread):
	def __init__(self, socket, sAddr, sPort, SAWSocket):
		super().__init__(name = 'ReceiveD')
		self.socket = socket
		self.peerAddr = sAddr
		self.peerPort = sPort
		self.data = SAWSocket
		self.running = True
		self.start()
	# end of __init__()
	
	def run(self):
		while(self.data.is_running()):
			# Receive a message			
			recv_msg, (rip, rport) = self.socket.recvfrom(self.data.BufSize)
			length = len(recv_msg) - 5
			msg_format1 = '!' + 'B I ' + str(length) + 's'				# !: network order
			msg_format2 = '!' + str(length) + 's'
			s = struct.Struct(msg_format1)
			data = s.unpack(recv_msg)
			msg_type = data[0]
			msg_sn = data[1]
			msg_value = (data[2], )
			s = struct.Struct(msg_format2)
			msg_msg = s.pack(*msg_value)
			
			if(msg_type == ord('M')):
				if(msg_sn == self.data.get_sn_receive()):		# receive a new message
					while(self.data.has_data()):							# data still in CS_buf
						time.sleep(self.data.SleepIdle)
				
					self.data.copy2CS_buf(msg_msg)
					self.data.data_ready()									# notify
					msg_sn = (msg_sn + 1) % 2						# for acknowledgement
				elif(DEBUG):
					print('Duplicate message. SN = ' + str(msg_sn))
				# This program does not consider the case that the system lost the ACK message.
				# if (msg_sn != self.data.get_sn_receive()), this is a reply message
				# 		 that is, sender losts the previous acknowledgement message
				
				# Reply ACK
				msg_format1 = '!' + 'B I ' 				# !: network order
				s = struct.Struct(msg_format1)
				value = (ord('A'), msg_sn)
				packed_data = s.pack(*value)
				self.socket.sendto(packed_data, (self.peerAddr, self.peerPort))
			elif(msg_type == ord('A')):
				if(msg_sn != self.data.get_sn_send()):
					self.data.receive_ack(msg_sn)
					self.data.add_sn_send()
				elif(DEBUG):
					print('Duplicate ACK. SN = ' + str(msg_sn))
			elif(msg_type == ord('F')):
				# Reply ACK
				msg_format1 = '!' + 'B I ' 				# !: network order
				s = struct.Struct(msg_format1)
				value = (ord('A'), msg_sn)
				packed_data = s.pack(*value)
				self.socket.sendto(packed_data, (self.peerAddr, self.peerPort))
			else:
				if(DEBUG):
					print('Message error. SN = ' + str(msg_sn))
		# end of while
		if(DEBUG):
			print('Receive daemon closed()')
	# end of run()
# end of class ReceiveD

if __name__ == '__main__':
	print('Hello!!')

