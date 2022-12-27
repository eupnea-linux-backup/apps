from typing import Tuple

from functions import *


def parse_keyboard_layouts() -> Tuple[dict, dict]:
    """Parses the layouts from /usr/share/X11/xkb/rules/base.lst and returns a python list of all the layouts"""
    with open("/usr/share/X11/xkb/rules/base.lst", "r") as file:
        raw_file = file.readlines()

    # Read basic layouts
    basic_layouts = raw_file[
                    raw_file.index("! layout\n") + 1:raw_file.index("  custom          A user-defined custom Layout\n")]
    # Parse into dict
    basic_dict = {}
    for layout in basic_layouts:
        layout = layout.strip()
        # Split line into key and value
        key = layout[layout.find(" ") + 1:].strip()
        value = layout[:layout.find(" ")].strip()
        basic_dict[key] = value

    # Read advanced layouts
    advanced_dict = {}
    advanced_layouts = raw_file[
                       raw_file.index("! variant\n") + 1:raw_file.index("! option\n")]
    # Parse into a nested dict
    for layout in advanced_layouts:
        layout = layout.strip()
        # Split line into 2 keys and 1 value
        key1 = layout[layout.find(" ") + 1:layout.find(":")].strip()
        if key1 == "":  # avoid empty keys
            continue
        key2 = layout[layout.find(":") + 1:].strip()
        value = layout[:layout.find(" ")].strip()
        try:
            advanced_dict[key1][key2] = value
        except KeyError:  # if key1 is not in dict yet
            advanced_dict[key1] = {key2: value}

    return basic_dict, advanced_dict


def set_keyboard_layout(layout: str) -> None:
    print("Setting keyboard layout to: " + layout)


def get_wifi_list() -> list:
    """List all Wi-Fi networks if not using ethernet"""
    print("Checking if already connected to the internet")
    if not bash("nmcli con show") == "":
        return ["Already connected to the internet"]

    # turn on Wi-Fi
    bash("nmcli radio wifi on")

    # try to scan for networks multiple times
    for i in range(5):
        print("Scanning for Wi-Fi networks")
        raw_wifi = bash("nmcli --terse --fields SSID,BARS,SECURITY dev wifi list").strip().split("\n")
        if len(raw_wifi) > 1:
            break
        sleep(1)

    # Parse list into a list of lists
    wifi_list = []
    for network in raw_wifi:
        network = network.split(":")
        # Transform bars into a number
        match network[1]:
            case "▂▄▆█":
                network[1] = 4
            case "▂▄▆_":
                network[1] = 3
            case "▂▄__":
                network[1] = 2
            case "▂___":
                network[1] = 1
        # Transform security into a boolean
        if network[2].__contains__("WPA"):
            network[2] = True
        else:
            network[2] = False
        wifi_list.append(network)

    return wifi_list
