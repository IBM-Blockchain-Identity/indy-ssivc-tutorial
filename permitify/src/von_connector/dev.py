import binascii
import platform
import socket
import uuid


def get_unique_version():
    platform_name = platform.system()
    host_name = socket.gethostname()
    mac = uuid.getnode()
    verison = "{0}.{1}.{2}".format(binascii.crc32(platform_name.encode()), binascii.crc32(host_name.encode()), mac)
    return verison
