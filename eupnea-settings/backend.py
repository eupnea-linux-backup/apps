import json
from typing import Dict, List, Tuple, Union

from functions import *


def read_package_version(package_name: str) -> str:
    """
    _summary_

    Args:
        package_name (str): _description_

    Returns:
        str: _description_
    """
    # Read eupnea.json to get distro info
    with open("/etc/eupnea.json", "r") as f:
        distro_info = json.load(f)

    match distro_info["distro_name"]:
        case "ubuntu" | "popos":
            try:
                raw_dpkg = bash(f"dpkg-query -s {package_name}")
                if raw_dpkg.__contains__("Status: install ok installed"):
                    return raw_dpkg.split("\n")[7][9:].strip()
            except subprocess.CalledProcessError:
                return "Error"
        case "fedora":
            try:
                raw_dnf = bash(f"dnf list -C {package_name}")  # -C prevents from updating repos -> faster operations
                if raw_dnf.__contains__("Installed Packages"):
                    return raw_dnf.split("                  ")[1].strip()
            except subprocess.CalledProcessError:
                return "Error"
        case "arch":
            try:
                # pacman errors out if package is not installed -> no need to check output for install status
                return bash(f"sudo pacman -Q {package_name}").split(" ")[1].strip()
            except subprocess.CalledProcessError:
                return "Error"


def get_kernel_version() -> str:
    """
    Returns the version of the currently running kernel

    Returns:
        str: version of the currently running kernel
    """
    return bash("uname -r")


def reinstall_kernel() -> None:
    """
    Reinstalls the kernel packages using the "eupnea/modify-packages"
    """
    bash("/usr/lib/eupnea/modify-packages")


def get_current_cmdline() -> Tuple[bool, str]:
    """
    Returns the current kernel command line parameters

    Returns:
        bool: flag indicating success or failure
        str: contents of the file
    """
    try:
        with open("/proc/cmdline", "r") as f:
            content = f.read()
        print(content)
        return 0, content
    except subprocess.CalledProcessError:
        return 1, ""


def apply_kernel(cmdline: str) -> bool:
    """
    Apply a new kernel with the specified command line options

    Args:
        cmdline (str): The command line options

    Raises:
        e: If an error occurs while applying the new kernel

    Returns:
        bool: 0 if the new kernel was applied successfully,
              1 if the system is pending reboot
    """
    # Create new cmdline file
    with open("/tmp/new_cmdline", "w") as f:
        f.write(cmdline)
    # read partitions
    partitions = bash("mount | grep ' / ' | cut -d' ' -f 1")
    partitions = partitions[:-1]  # get device name
    # save current kernel to a file
    print_status("Extracting current kernel")
    # each time we want to do a root action we need to ask for password
    # -> combine dd command and kernel flash command into one command to avoid asking for password twice
    try:
        bash(f"pkexec sh -c 'dd if={partitions}1 of=/tmp/current_kernel && /usr/lib/eupnea/install-kernel "
             f"/tmp/current_kernel --kernel-flags /tmp/new_cmdline'")
        return 0
    except subprocess.CalledProcessError as e:
        if e.returncode != 65:
            raise e
        print_error("System is pending reboot. Please reboot and try again.")
        return 1


def read_eupnea_json() -> Union[Dict, List, str, int, float, bool, None]:
    """
    Reads the Eupnea configuration

    Returns:
        Union: The parsed JSON object representing the Eupnea configuration
    """
    with open("/etc/eupnea.json") as f:
        return json.load(f)


def get_session_type() -> str:
    try:
        return bash("echo $XDG_SESSION_TYPE")
    except subprocess.CalledProcessError:
        return "Unknown"
