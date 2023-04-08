import json
from typing import Dict, List, Tuple, Union

from functions import *


def bash_with_perms(command: str) -> str:
    """
    Runs a bash command with root permissions obtained through pkexec

    Args:
        command (str): Bash command to run

    Returns:
        str: Output of the command
    """
    return bash(f"pkexec bash -c '{command}'")


def deep_sleep_enabled() -> bool:
    """
    Checks if deep sleep is enabled

    Returns:
        bool: True if deep sleep is enabled
              False if deep sleep is disabled
    """
    return path_exists("/etc/systemd/sleep.conf.d/deep_sleep_block.conf")


def toggle_deep_sleep() -> None:
    """
    Disables/enables deep sleep via a systemd config, depending on the current state
    """
    if not deep_sleep_enabled():
        # TODO: Implement a python version of this
        with contextlib.suppress(subprocess.CalledProcessError):
            # the sleep.conf.d directory may not exist -> create it
            # copy the deep_sleep_block.conf file to the sleep.conf.d directory
            # reload systemd for the changes to take effect
            bash_with_perms("mkdir -p /etc/systemd/sleep.conf.d && cp /usr/share/eupnea/deep_sleep_block.conf "
                            "/etc/systemd/sleep.conf.d/deep_sleep_block.conf && systemctl daemon-reload")
    else:
        bash_with_perms("rm -f /etc/systemd/sleep.conf.d/deep_sleep_block.conf")


def read_package_version(package_name: str) -> str:
    """
    Read specified package version in the current distribution

    Args:
        package_name (str): Name of the package to read the version for

    Returns:
        str: Version of the specified package if it is installed

    Raises:
        subprocess.CalledProcessError: If package information read fails
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
                raw_dnf = bash(f"dnf list -yC {package_name}")  # -C prevents from updating repos -> faster operations
                if raw_dnf.__contains__("Installed Packages"):
                    return raw_dnf.split("                  ")[1].strip()
                else:
                    return "Error"
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


def install_kernel(reinstall: bool = False) -> None:
    """
    Reinstalls the kernel packages using the "eupnea modify-packages script"
    """
    temp_file = bash("mktemp")
    if get_kernel_version().startswith("5."):
        with open(temp_file, "w") as f:
            f.write("!eupnea-chromeos-kernel" if reinstall else "eupnea-chromeos-kernel")
    else:
        with open(temp_file, "w") as f:
            f.write("!eupnea-mainline-kernel" if reinstall else "eupnea-mainline-kernel")
    bash_with_perms(f"/usr/lib/eupnea/modify-packages --file {temp_file}")


def get_current_cmdline() -> Tuple[str, str]:
    """
    Returns the current kernel command line parameters or an error message if an error occurred

    Returns:
        str: error if file read fails
        str: contents of the file
    """
    try:
        with open("/proc/cmdline", "r") as f:
            content = f.read().strip()
        print(content)
        return "", content
    except subprocess.CalledProcessError:
        return "Error reading cmdline", ""


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
        bash_with_perms(f"/usr/lib/eupnea/install-kernel --kernel-flags {temp_file}")
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
