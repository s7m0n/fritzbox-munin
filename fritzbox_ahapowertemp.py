#!/usr/bin/env python3
# coding=utf-8
"""
  aha_powertemp - A munin plugin for Linux to monitor AVM home automation devices via fritzconnection 
  Copyright (C) 2024 s7m0n
  Author: s7m0n
  Like Munin, this plugin is licensed under the GNU GPL v2 license
  http://www.opensource.org/licenses/GPL-2.0
  Add the following section to your munin-node's plugin configuration:

  [fritzbox_*]
  env.fritzbox_ip [ip address of the fritzbox]
  env.fritzbox_username [fritzbox username]
  env.fritzbox_password [fritzbox password]
  env.configured_ahapowertemp_device_names [device name(s) which shall be monitored as name in SmartHome device configuration of the box]
  This plugin supports the following munin configuration parameters:
  #%# family=auto contrib
  #%# capabilities=autoconf
"""
import json
import os
import sys

from fritzconnection.lib.fritzhomeauto import FritzHomeAutomation

PAGE = "energy"
CATEGORIES = ["power", "temp"]


def get_power_consumption(configured_device_names):
    """get the current power consumption and temperature"""

    server = os.environ["fritzbox_ip"]
    username = os.environ["fritzbox_username"]
    password = os.environ["fritzbox_password"]
    
    fha = FritzHomeAutomation(address=server, user=username, password=password)

    infodata = fha.device_information()
    #print(infodata)
    try:
        for data in infodata:
            device_name = data['NewDeviceName']
            if device_name in configured_device_names:
                power = data['NewMultimeterPower'] * 0.01
                temp = data['NewTemperatureCelsius'] * 0.1
                print(f"{device_name}power.value {power}")
                print(f"{device_name}temp.value {temp}")
    except Exception as e:
        print("Exception: ", e)
        raise

def print_config():
    print("graph_title AVM Home Automation Consumption")
    print("graph_vlabel %")
    print("graph_category system")
    for device_name in configured_device_names:
        print(f"{device_name}power.label {device_name} Power in W")
        print(f"{device_name}power.type GAUGE")
        print(f"{device_name}power.graph LINE12")
        print(f"{device_name}power.min 0")
        print(f"{device_name}power.max 3500") 
        print(f"{device_name}power.info Power consumption of {device_name}")
        print(f"{device_name}temp.label {device_name} Temperature in °C")
        print(f"{device_name}temp.type GAUGE")
        print(f"{device_name}temp.graph LINE1")
        print(f"{device_name}temp.min 0")
        print(f"{device_name}temp.max 100")
        print(f"{device_name}temp.info Temperature of {device_name}")
    if os.environ.get("host_name"):
        print("host_name " + os.environ["host_name"])


if __name__ == "__main__":
    configured_device_names = os.environ.get("configured_ahapowertemp_device_names", "").split()
    
    if len(sys.argv) == 2 and sys.argv[1] == "config":
        print_config()
    elif len(sys.argv) == 2 and sys.argv[1] == "autoconf":
        print("yes")
    elif len(sys.argv) == 1 or len(sys.argv) == 2 and sys.argv[1] == "fetch":
        # Some docs say it'll be called with fetch, some say no arg at all
        try:
            get_power_consumption(configured_device_names)
        except:
            sys.exit("Couldn't retrieve fritzbox power consumption")
