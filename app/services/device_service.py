'''Services for tracking devices'''

import logging
from datetime import datetime

log = logging.getLogger(__name__)

# simple in-memory store
device_last_seen = {}


def track_device(ip_address):
    """Record or update a device connection"""
    # log.info("Device connected: %s", ip_address)
    device_last_seen[ip_address] = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")


def get_devices():
    '''Getter to get devices'''
    return [
        {"ip": ip, "last_seen": ts}
        for ip, ts in device_last_seen.items()
    ]
