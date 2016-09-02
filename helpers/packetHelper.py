import struct
from constants import dataTypes

def uleb128Encode(num):
	"""
	Encode int -> uleb128

	num -- int to encode
	return -- bytearray with encoded number
	"""
	arr = bytearray()
	length = 0

	if num == 0:
		return bytearray(b"\x00")

	while num > 0:
		arr.append(num & 127)
		num = num >> 7
		if num != 0:
			arr[length] = arr[length] | 128
		length+=1

	return arr

def uleb128Decode(num):
	"""
	Decode uleb128 -> int

	num -- encoded uleb128
	return -- list. [total, length]
	"""
	shift = 0
	arr = [0,0]	#total, length

	while True:
		b = num[arr[1]]
		arr[1]+=1
		arr[0] = arr[0] | (int(b & 127) << shift)
		if b & 128 == 0:
			break
		shift += 7

	return arr

def unpackData(data, dataType):
	"""
	Unpacks data according to dataType

	data -- bytes array to unpack
	dataType -- data type. See dataTypes.py

	return -- unpacked bytes
	"""

	# Get right pack Type
	if dataType == dataTypes.uInt16:
		unpackType = "<H"
	elif dataType == dataTypes.sInt16:
		unpackType = "<h"
	elif dataType == dataTypes.uInt32:
		unpackType = "<L"
	elif dataType == dataTypes.sInt32:
		unpackType = "<l"
	elif dataType == dataTypes.uInt64:
		unpackType = "<Q"
	elif dataType == dataTypes.sInt64:
		unpackType = "<q"
	elif dataType == dataTypes.string:
		unpackType = "<s"
	elif dataType == dataTypes.ffloat:
		unpackType = "<f"
	else:
		unpackType = "<B"

	# Unpack
	return struct.unpack(unpackType, bytes(data))[0]

def packData(__data, dataType):
	"""
	Packs data according to dataType

	data -- bytes to pack
	dataType -- data type. See dataTypes.py

	return -- packed bytes
	"""

	data = bytes()	# data to return
	pack = True		# if True, use pack. False only with strings

	# Get right pack Type
	if dataType == dataTypes.bbytes:
		# Bytes, do not use pack, do manually
		pack = False
		data = __data
	elif dataType == dataTypes.intList:
		# Pack manually
		pack = False
		# Add length
		data = packData(len(__data), dataTypes.uInt16)
		# Add all elements
		for i in __data:
			data += packData(i, dataTypes.sInt32)
	elif dataType == dataTypes.string:
		# String, do not use pack, do manually
		pack = False
		if len(__data) == 0:
			# Empty string
			data += b"\x00"
		else:
			# Non empty string
			data += b"\x0B"
			data += uleb128Encode(len(__data))
			data += str.encode(__data, "latin_1", "ignore")
	elif dataType == dataTypes.uInt16:
		packType = "<H"
	elif dataType == dataTypes.sInt16:
		packType = "<h"
	elif dataType == dataTypes.uInt32:
		packType = "<L"
	elif dataType == dataTypes.sInt32:
		packType = "<l"
	elif dataType == dataTypes.uInt64:
		packType = "<Q"
	elif dataType == dataTypes.sInt64:
		packType = "<q"
	elif dataType == dataTypes.string:
		packType = "<s"
	elif dataType == dataTypes.ffloat:
		packType = "<f"
	else:
		packType = "<B"

	# Pack if needed
	if pack == True:
		data += struct.pack(packType, __data)

	return data

def buildPacket(__packet, __packetData = []):
	"""
	Build a packet

	packet -- packet id (int)
	packetData -- list [[data, dataType], [data, dataType], ...]

	return -- packet bytes
	"""
	# Set some variables
	packetData = bytes()
	packetLength = 0
	packetBytes = bytes()

	# Pack packet data
	for i in __packetData:
		packetData += packData(i[0], i[1])

	# Set packet length
	packetLength = len(packetData)

	# Return packet as bytes
	packetBytes += struct.pack("<h", __packet)		# packet id (int16)
	packetBytes += bytes(b"\x00")					# unused byte
	packetBytes += struct.pack("<l", packetLength)	# packet lenght (iint32)
	packetBytes += packetData						# packet data
	return packetBytes

def readPacketID(stream):
	"""
	Read packetID from stream (0-1 bytes)

	stream -- data stream
	return -- packet ID (int)
	"""
	return unpackData(stream[0:2], dataTypes.uInt16)

def readPacketLength(stream):
	"""
	Read packet length from stream (3-4-5-6 bytes)

	stream -- data stream
	return -- packet length (int)
	"""
	return unpackData(stream[3:7], dataTypes.uInt32)


def readPacketData(stream, structure = [], hasFirstBytes = True):
	"""
	Read packet data from stream according to structure

	stream -- data stream
	structure -- [[name, dataType], [name, dataType], ...]
	hasFirstBytes -- 	if True, stream has packetID and length bytes.
						if False, stream has only packetData.
						Optional. Default: True
	return -- dictionary. key: name, value: read data
	"""
	# Read packet ID (first 2 bytes)
	data = {}

	# Skip packet ID and packet length if needed
	if hasFirstBytes == True:
		end = 7
		start = 7
	else:
		end = 0
		start = 0

	# Read packet
	for i in structure:
		start = end
		unpack = True
		if i[1] == dataTypes.intList:
			# sInt32 list.
			# Unpack manually with for loop
			unpack = False

			# Read length (uInt16)
			length = unpackData(stream[start:start+2], dataTypes.uInt16)

			# Read all int inside list
			data[i[0]] = []
			for j in range(0,length):
				data[i[0]].append(unpackData(stream[start+2+(4*j):start+2+(4*(j+1))], dataTypes.sInt32))

			# Update end
			end = start+2+(4*length)
		elif i[1] == dataTypes.string:
			# String, don't unpack
			unpack = False

			# Check empty string
			if stream[start] == 0:
				# Empty string
				data[i[0]] = ""
				end = start+1
			else:
				# Non empty string
				# Read length and calculate end
				length = uleb128Decode(stream[start+1:])
				end = start+length[0]+length[1]+1

				# Read bytes
				data[i[0]] = ''.join(chr(j) for j in stream[start+1+length[1]:end])
		elif i[1] == dataTypes.byte:
			end = start+1
		elif i[1] == dataTypes.uInt16 or i[1] == dataTypes.sInt16:
			end = start+2
		elif i[1] == dataTypes.uInt32 or i[1] == dataTypes.sInt32:
			end = start+4
		elif i[1] == dataTypes.uInt64 or i[1] == dataTypes.sInt64:
			end = start+8

		# Unpack if needed
		if unpack == True:
			data[i[0]] = unpackData(stream[start:end], i[1])

	return data
