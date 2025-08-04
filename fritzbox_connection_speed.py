#!/usr/bin/env python3
"""
  fritzbox_homeauto_power - A munin plugin for Linux to monitor AVM Fritzbox connection speedss
  Like Munin, this plugin is licensed under the GNU GPL v2 license
  http://www.opensource.org/licenses/GPL-2.0
  This plugin requires the fritzconnection plugin. To install it using pip:
  pip install fritzconnection
  This plugin supports the following munin configuration parameters:

  [fritzbox_*]
  env.fritzbox_ip [ip address of the fritzbox]
  env.fritzbox_username [fritzbox username]
  env.fritzbox_password [fritzbox password]
  env.expected_down_rate_mbps [expected/target speed down]
  env.expected_up_rate_mbps [expected/target speed up]
  env.max_dl_speed [highest speed to expect for graph height]

  #%# family=auto contrib
  #%# capabilities=autoconf
"""
import os
import sys
import traceback
from fritzconnection.lib.fritzstatus import FritzStatus

# FritzBox credentials from environment variables
server = os.environ.get("FRITZBOX_IP", "192.168.178.1")
username = os.environ.get("FRITZBOX_USERNAME", "")
password = os.environ.get("FRITZBOX_PASSWORD", "")

def get_env_int(key, default):
    try:
        return int(os.environ.get(key, default))
    except ValueError:
        return int(default)

# Expected speeds in Mbps
EXPECTED_DOWN_RATE_MBPS = get_env_int("EXPECTED_DOWN_RATE_MBPS", "100")
EXPECTED_UP_RATE_MBPS = get_env_int("EXPECTED_UP_RATE_MBPS", "40")
MAX_SPEED = int(os.environ.get("MAX_DL_SPEED", 120))  # Max speed for graph height in Mbps

# Conversion factor from bytes/sec to Mbps
BYTES_TO_MBPS = 8 / 1_000_000

def print_values():
    try:
        fs = FritzStatus(address=server, user=username, password=password)
        up_rate, down_rate = fs.max_byte_rate
        down_rate_mbps = down_rate * BYTES_TO_MBPS
        up_rate_mbps = up_rate * BYTES_TO_MBPS
    except Exception as e:
        print("Error: Could not retrieve Fritz!Box data.")
        traceback.print_exc()
        sys.exit(1)

    print("down.value %d" % down_rate_mbps)
    print("up.value %d" % up_rate_mbps)
    print("expdown.value %d" % EXPECTED_DOWN_RATE_MBPS)
    print("expup.value %d" % EXPECTED_UP_RATE_MBPS)


def print_config():
    print("graph_title AVM Fritz!Box connection speed")
    print("graph_args --base 1000 -r --lower-limit 0 --upper-limit %d" % MAX_SPEED)
    print("graph_vlabel Mbit/s")
    print("graph_category network")
    print("graph_order down up expdown expup")

    print("down.label Download")
    print("down.type GAUGE")
    print("down.draw AREA")
    print("down.colour 00ff00")

    print("up.label Upload")
    print("up.type GAUGE")
    print("up.draw AREA")
    print("up.colour 0000ff")

    print("expdown.label Expected Download")
    print("expdown.type GAUGE")
    print("expdown.draw LINE1")
    print("expdown.colour ff0000")

    print("expup.label Expected Upload")
    print("expup.type GAUGE")
    print("expup.draw LINE1")
    print("expup.colour ff00ff")

    if os.environ.get("host_name"):
        print("host_name " + os.environ["host_name"])


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "config":
        print_config()
    elif len(sys.argv) == 2 and sys.argv[1] == "autoconf":
        print("yes")
    elif len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == "fetch"):
        print_values()





























































































