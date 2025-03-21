#!/usr/bin/env python3
"""
  fritzbox_traffic - A munin plugin for Linux to monitor AVM Fritzbox WAN traffic
  Copyright (C) 2025 s7mon
  Author: s7mon
  Like Munin, this plugin is licensed under the GNU GPL v2 license
  http://www.opensource.org/licenses/GPL-2.0
  Like Munin, this plugin is licensed under the GNU GPL v2 license
  http://www.opensource.org/licenses/GPL-2.0
  This plugin requires the fritzconnection plugin. To install it using pip:
  pip install fritzconnection
  This plugin supports the following munin configuration parameters:

  [fritzbox_*]
  env.fritzbox_ip [ip address of the fritzbox]
  env.fritzbox_username [fritzbox username]
  env.fritzbox_password [fritzbox password]
  user = munin 

  #%# family=auto contrib
  #%# capabilities=autoconf
"""
import os
import sys
import time
import pickle
import traceback  
from fritzconnection.lib.fritzstatus import FritzStatus

# Environment variables for Fritz!Box access
server   = os.environ["fritzbox_ip"]
username = os.environ["fritzbox_username"]
password = os.environ["fritzbox_password"]

# File to store accumulated daily totals
STATE_FILE = "/var/lib/munin/plugin-fritzbox-traffic.pkl"

# Unit selection (MB or GB)
TRAFFIC_UNIT = "MB"
UNIT_DIVISOR = 1_000_000 if TRAFFIC_UNIT == "MB" else 1_000_000_000
UNIT_LABEL = "MB" if TRAFFIC_UNIT == "MB" else "GB"


def load_state():
    """ Load previous state from file. """
    try:
        with open(STATE_FILE, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {"last_time": 0, "last_down": 0, "last_up": 0, "total_down": 0, "total_up": 0, "last_date": time.strftime("%Y-%m-%d")}

def save_state(state):
    """ Save current state to file. """
    with open(STATE_FILE, "wb") as f:
        pickle.dump(state, f)

def print_values():
    """ Calculate and print accumulated traffic in MB or GB """
    try:
        state = load_state()  # Load previous data from pickle file
        
        # Fetch traffic data from Fritz!Box
        try:
            fs = FritzStatus(address=server, user=username, password=password)
        except Exception as e:
            print("Error: Could not connect to Fritz!Box.")
            print(f"Exception: {e}")
            traceback.print_exc()  # Print full stack trace
            sys.exit(1)

        down_now = fs.bytes_received
        up_now = fs.bytes_sent
        current_date = time.strftime("%Y-%m-%d")

        # Reset total if it's a new day
        if current_date != state["last_date"]:
            state["total_down"] = 0
            state["total_up"] = 0
            state["last_date"] = current_date

        # Calculate traffic difference
        down_diff = max(0, down_now - state["last_down"])
        up_diff = max(0, up_now - state["last_up"])

        # Accumulate totals
        state["total_down"] += down_diff
        state["total_up"] += up_diff

        # update last to current
        state["last_down"] = down_now
        state["last_up"] = up_now

        # Convert to MB or GB before printing
        print(f"total_down.value {state['total_down'] / UNIT_DIVISOR:.2f}")
        print(f"total_up.value {state['total_up'] / UNIT_DIVISOR:.2f}")

        # Save updated state
        try:
            save_state(state)
        except Exception as e:
            print("Error: Could not save state file.")
            print(f"Exception: {e}")
            traceback.print_exc()
            sys.exit(1)

    except Exception as e:
        print("Unexpected error in print_values()")
        print(f"Exception: {e}")
        traceback.print_exc()
        sys.exit(1)

def print_config():
    """ Print Munin configuration """
    print("graph_title AVM Fritz!Box WAN traffic (Daily Accumulated)")
    print("graph_args --base 1000 -l 0")
    print("graph_vlabel MB today")
    print("graph_category network")
    print("graph_order total_down total_up")
    print("total_down.label Total Received")
    print("total_down.type GAUGE")
    print("total_down.draw AREA")
    print("total_down.info Accumulated received MB over the day.")
    print("total_up.label Total Sent")
    print("total_up.type GAUGE")
    print("total_up.draw LINE1")
    print("total_up.info Accumulated sent MB over the day.")

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "config":
        print_config()
    elif len(sys.argv) == 2 and sys.argv[1] == "autoconf":
        print("yes")
    elif len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == "fetch"):
        try:
            print_values()
        except Exception:
            sys.exit("Couldn't retrieve fritzbox traffic")

