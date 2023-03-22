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


def get_current_cmdline() -> str:
    """
    Returns the current kernel command line parameters or an error message if an error occurred

    Returns:
        str: contents of the file or an error message
        str: contents of the file or an error message
    """
    try:
        with open("/proc/cmdline", "r") as f:
            content = f.read().strip()
        print(content)
        return "Error reading cmdline" if content == "" else content
    except subprocess.CalledProcessError:
        return "Error reading cmdline"


def apply_kernel(cmdline: str) -> str:
    """
    Apply a new kernel with the specified command line options

    Args:
        cmdline (str): The command line options

    Returns:
        str: Empty string if the kernel was applied successfully
             Error message if an error occurred
    """
    # Create temp cmdline file
    temp_file = bash("mktemp")
    with open(temp_file, "w") as f:
        f.write(cmdline)
    try:
        bash(f"pkexec /usr/lib/eupnea/install-kernel --kernel-flags {temp_file}")
        return ""
    except subprocess.CalledProcessError as e:
        if e.returncode == 65:
            print_error("System is pending reboot. Please reboot and try again.")
            return "PENDING_REBOOT"  # system is pending reboot
        return e.output.decode("utf-8")  # return error message


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
