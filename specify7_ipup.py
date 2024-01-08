"""this document is for seeking out files containing absolute ip address in the specify7 files, and
   replace them with the current absolute ip address"""
# importing packages
import socket
import os
import re

def ip_getter():
    """ip_getter:
       gets a copy of the host machine's absolute ip address
       returns:
            ip_ad: a copy of the host machine's absolute ip address"""
    hostname = socket.gethostname()
    ip_ad = socket.gethostbyname(hostname)
    print(ip_ad)
    return ip_ad


def set_direct():
    """get_direct: changes directory to
       current file location directory
       returns:
            none
            """
    # get current directory
    #current_directory = os.getcwd()
    # this is absolute path for running chron from bin
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # set current directory
    os.chdir(current_directory)


def ip_replace(filename: str):
    """ip_replace: opens a target file path, and replaces,
                   all references to ip addresses
                   to the current ip address
    """
    with open(filename, 'r') as file:
        # Read the contents of the file
        content = file.read()
    ip_ad = ip_getter()
    # Replace the string
    new_content = re.sub(r'\b10.1.12.\w*\b', ip_ad, content)

    # Open the file in write mode
    with open(filename, 'w') as file:
        # Write the modified content back to the file
        file.write(new_content)


def master_run():
    """runs all functions in this file sequentially"""
    set_direct()

    ip_replace('../specify7/docker-compose.yml')

    ip_replace('settings.py')

    ip_replace('docker-compose.yml')

# running master function
master_run()

print(socket.gethostname())
