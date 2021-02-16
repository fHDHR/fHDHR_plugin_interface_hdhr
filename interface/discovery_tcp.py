import threading
import socket

from .discovery_shared import (HDHR_Discovery_Service_Shared,
                               HDHOMERUN_MAX_PACKET_SIZE, HDHOMERUN_TYPE_DISCOVER_REQ, HDHOMERUN_TYPE_GETSET_REQ,
                               HDHOMERUN_TYPE_DISCOVER_RPY, HDHOMERUN_CONTROL_TCP_PORT)


class HDHR_Discovery_Service_TCP():

    def __init__(self, fhdhr, plugin_utils, interface):
        self.fhdhr = fhdhr
        self.plugin_utils = plugin_utils
        self.interface = interface

        self.discovery_shared = HDHR_Discovery_Service_Shared(fhdhr, plugin_utils, interface)

        if self.fhdhr.config.dict["hdhr"]["discovery"]:
            self.fhdhr.logger.info("Initializing HDHR TCP Discovery system")
            self.fhdhr.threads["hdhr_tcp_discovery"] = threading.Thread(target=self.discovery_service_listen)
            self.setup_discovery()

        else:
            self.fhdhr.logger.info("HDHR TCP Discovery system will not be Initialized: Not Enabled")

    def discovery_service_listen(self):
        self.sock.listen(1)
        while True:

            connection, client = self.sock.accept()

            try:
                packet = connection.recv(HDHOMERUN_MAX_PACKET_SIZE)
                if not packet:
                    self.fhdhr.logger.ssdp('No packet received')
                    break

                self.fhdhr.logger.ssdp("Request: %s" % self.discovery_shared.format_packet(packet))
                (packetType, requestPayload) = self.discovery_shared.retrieveTypeAndPayload(packet)

                if packetType == HDHOMERUN_TYPE_DISCOVER_REQ:
                    self.fhdhr.logger.ssdp("Discovery request received from %s" % str(client))

                    for origin in self.plugin_utils.origins.valid_origins:
                        responsePacket = self.discovery_shared.discover_responsePacket(origin)
                        if responsePacket:
                            self.fhdhr.logger.ssdp("Sending %s discovery reply over tcp to %s" % (origin, str(client)))
                            connection.send(responsePacket)

                elif packetType == HDHOMERUN_TYPE_GETSET_REQ:
                    self.fhdhr.logger.ssdp('Get set request received from ' + client[0])
                    responsePacket = self.discovery_shared.getset_responsePacket(origin, requestPayload)
                    if responsePacket:
                        connection.send(responsePacket)

                elif packetType == HDHOMERUN_TYPE_DISCOVER_RPY:
                    self.fhdhr.logger.ssdp("RPY from %s" % str(client))

                else:
                    self.fhdhr.logger.ssdp("Unknown packet type %s" % str(packetType))
            finally:
                connection.close()

        self.sock.close()

    def setup_discovery(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("0.0.0.0", HDHOMERUN_CONTROL_TCP_PORT))
