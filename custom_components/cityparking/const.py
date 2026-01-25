"""Constants for the shell_recharge integration."""

from datetime import timedelta
from enum import IntFlag
from enum import Enum

DOMAIN = "cityparking"
SerialNumber = str
Origin = str
UPDATE_INTERVAL = timedelta(minutes=5)
CONF_ORIGIN = "origin"
