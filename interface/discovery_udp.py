import threading
import socket
import struct
import zlib
from io import StringIO


HDHOMERUN_DISCOVER_UDP_PORT = 65001
HDHOMERUN_MAX_PACKET_SIZE = 1460
HDHOMERUN_MAX_PAYLOAD_SIZE = 1452

HDHOMERUN_TYPE_DISCOVER_REQ = 0x0002
HDHOMERUN_TYPE_DISCOVER_RPY = 0x0003
HDHOMERUN_TYPE_GETSET_REQ = 0x0004
HDHOMERUN_TYPE_GETSET_RPY = 0x0005
HDHOMERUN_TAG_DEVICE_TYPE = 0x01
HDHOMERUN_TAG_DEVICE_ID = 0x02
HDHOMERUN_TAG_GETSET_NAME = 0x03
HDHOMERUN_TAG_GETSET_VALUE = 0x04
HDHOMERUN_TAG_GETSET_LOCKKEY = 0x15
HDHOMERUN_TAG_ERROR_MESSAGE = 0x05
HDHOMERUN_TAG_TUNER_COUNT = 0x10
HDHOMERUN_TAG_DEVICE_AUTH_BIN = 0x29
HDHOMERUN_TAG_BASE_URL = 0x2A
HDHOMERUN_TAG_LINEUP_URL = 0x27
HDHOMERUN_TAG_DEVICE_AUTH_STR = 0x2B

HDHOMERUN_DEVICE_TYPE_WILDCARD = 0xFFFFFFFF
HDHOMERUN_DEVICE_TYPE_TUNER = 0x00000001
HDHOMERUN_DEVICE_ID_WILDCARD = 0xFFFFFFFF


class HDHR_UDP_Discovery_Service():

    def __init__(self, fhdhr, plugin_utils, interface):
        self.fhdhr = fhdhr
        self.plugin_utils = plugin_utils
        self.interface = interface

        if self.hdhr_discovery_address and self.fhdhr.config.dict["hdhr"]["discovery"]:
            self.fhdhr.logger.info("Initializing HDHR Discovery system")
            self.fhdhr.threads["hdhr_discovery"] = threading.Thread(target=self.discovery_service_listen)
            self.setup_discovery()

        elif not self.fhdhr.config.dict["hdhr"]["discovery"]:
            self.fhdhr.logger.info("HDHR Discovery system will not be Initialized: Not Enabled")
        elif not self.hdhr_discovery_address:
            self.fhdhr.logger.info("HDHR Discovery system will not be Initialized: Address not set in [hdhr]discovery_address [ssdp]multicast_address or [fhdhr]discovery_address")
        else:
            self.fhdhr.logger.info("HDHR Discovery system will not be Initialized")

    def discovery_service_listen(self):
        while True:

            packet, client = self.sock.recvfrom(HDHOMERUN_MAX_PACKET_SIZE)
            if not packet:
                self.fhdhr.logger.ssdp('No packet received')
                break
            self.fhdhr.logger.ssdp("Request: %s" % self.format_packet(packet))
            (packetType, requestPayload) = self.retrieveTypeAndPayload(packet)

            if packetType == HDHOMERUN_TYPE_DISCOVER_REQ:
                self.fhdhr.logger.ssdp("Discovery request received from %s" % str(client))

                for origin in self.plugin_utils.origins.valid_origins:
                    responsePacket = self.discover_responsePacket(origin)
                    if responsePacket:
                        self.fhdhr.logger.ssdp("Sending %s discovery reply over udp to %s" % (origin, str(client)))
                        self.sock.sendto(responsePacket, client)

            elif packetType == HDHOMERUN_TYPE_GETSET_REQ:
                self.fhdhr.logger.ssdp('Get set request received from ' + client[0])
                responsePacket = self.getset_responsePacket(origin, requestPayload)
                if responsePacket:
                    self.sock.sendto(responsePacket, client)

            elif packetType == HDHOMERUN_TYPE_DISCOVER_RPY:
                self.fhdhr.logger.ssdp("RPY from %s" % str(client))

            else:
                self.fhdhr.logger.ssdp("Unknown packet type %s" % str(packetType))

        self.sock.close()

    def getset_responsePacket(self, requestPayload):
        getSetName = None
        getSetValue = None
        payloadIO = StringIO(requestPayload)
        while True:

            header = payloadIO.read(2)
            if not header:
                break

            tag, length = struct.unpack('>BB', header)

            # TODO: If the length is larger than 127 the following bit is also needed to determine length
            if length > 127:
                self.fhdhr.logger.ssdp('Unable to determine tag length, the correct way to determine a length larger than 127 must still be implemented.')
                return None

            # TODO: Implement other tags
            if tag == HDHOMERUN_TAG_GETSET_NAME:
                getSetName = struct.unpack('>{0}s'.format(
                    length), payloadIO.read(length))[0]
            if tag == HDHOMERUN_TAG_GETSET_VALUE:
                getSetValue = struct.unpack('>{0}s'.format(
                    length), payloadIO.read(length))[0]

        if getSetName is None:
            return False
        else:
            responsePayload = struct.pack('>BB{0}s'.format(
                len(getSetName)), HDHOMERUN_TAG_GETSET_NAME, len(getSetName), getSetName)

            if getSetValue is not None:
                responsePayload += struct.pack('>BB{0}s'.format(
                    len(getSetValue)), HDHOMERUN_TAG_GETSET_VALUE, len(getSetValue), getSetValue)

            return self.createPacket(HDHOMERUN_TYPE_GETSET_RPY, responsePayload)

    def format_packet(self, data):
        return " ".join(["{:02x}".format(x) for x in data])

    def createUIntTag(self, tag, value):
        return struct.pack('>BBI', tag, 0x04, value)

    def createPacket(self, packetType, payload):
        header = struct.pack('>HH', packetType, len(payload))
        data = header + payload
        checksum = zlib.crc32(data)
        packet = data + struct.pack('<I', checksum)
        self.fhdhr.logger.ssdp("Response: %s" % str(self.format_packet(packet)))
        return packet

    def discover_responsePacket(self, origin):
        BaseUrl = "%s:%s/hdhr/%s" % (self.hdhr_discovery_address, self.fhdhr.api.port, origin)
        uid = self.interface.get_origin_uid(origin)
        device_id = int(uid[:8], 16)  # Hex string to int
        tuner_count = self.plugin_utils.origins.origins_dict[origin].tuners

        responsePayload = b''.join([
            self.createUIntTag(HDHOMERUN_TAG_DEVICE_TYPE,
                               HDHOMERUN_DEVICE_TYPE_TUNER),
            self.createUIntTag(HDHOMERUN_TAG_DEVICE_ID, device_id),
            self.createStringTag(HDHOMERUN_TAG_BASE_URL, BaseUrl.encode()),
            self.createStringTag(HDHOMERUN_TAG_LINEUP_URL,
                                 f'{BaseUrl}/discover.json'.encode()),
            self.createByteTag(HDHOMERUN_TAG_TUNER_COUNT, tuner_count)
        ])

        return self.createPacket(HDHOMERUN_TYPE_DISCOVER_RPY, responsePayload)

    def createStringTag(self, tag, value):
        length = self.write_var_length(len(value))
        payload = struct.pack('>B', tag)
        payload += length
        payload += struct.pack(f'>{len(value)}s', value)
        return payload

    def createByteTag(self, tag, value):
        return struct.pack('>BBB', tag, 0x01, value)

    def write_var_length(self, v):
        if(v <= 127):
            return struct.pack('B', v)
        else:
            l1 = v | 0x80
            l2 = v >> 7
            return struct.pack('BB', l1, l2)

    def retrieveTypeAndPayload(self, packet):

        header = packet[:4]

        packetType, payloadLength = struct.unpack('>HH', header)
        payload_and_crc = packet[4:4+payloadLength+4]
        payload = payload_and_crc[:-4]
        (checksum,) = struct.unpack("<I", payload_and_crc[-4:])

        if payloadLength != len(payload):
            self.fhdhr.logger.ssdp('Bad packet payload length')
            return False

        if checksum != zlib.crc32(header + payload):
            self.fhdhr.logger.ssdp('Bad checksum')
            return False

        return (packetType, payload)

    @property
    def hdhr_discovery_address(self):
        if self.fhdhr.config.dict["hdhr"]["discovery_address"]:
            return self.fhdhr.config.dict["hdhr"]["discovery_address"]
        elif self.fhdhr.config.dict["ssdp"]["multicast_address"]:
            return self.fhdhr.config.dict["ssdp"]["multicast_address"]
        elif self.fhdhr.config.dict["fhdhr"]["discovery_address"]:
            return self.fhdhr.config.dict["fhdhr"]["discovery_address"]
        return None

    def setup_discovery(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        # Enable broadcasting mode
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(('0.0.0.0', HDHOMERUN_DISCOVER_UDP_PORT))
