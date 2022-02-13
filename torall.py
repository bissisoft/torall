#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import getopt
from requests import get
import subprocess
import time
import signal
from stem import Signal
from stem.control import Controller
from packaging import version

VERSION = "1.0"
IPAPI = "https://api.ipify.org/?format=json"
LATEST = "https://api.github.com/repos/bissisoft/torall/releases/latest"
TORUID = "tor" if os.path.exists('/usr/bin/pacman') else "debian-tor"

RESOLV = "/etc/resolv.conf"
RESOLV_BAK = "/var/lib/torall/resolv.conf.bak"
NAMESRVS = "/var/lib/torall/nameservers.conf"

MARGIN = "        "

class bcolors:
    RED = '\033[31m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'

def t():
    current_time = time.localtime()
    ctime = time.strftime('%H:%M:%S', current_time)
    return MARGIN + '[' + ctime + ']'

def sigint_handler(signum, frame):
    print("User interrupt ! shutting down")
    stop_torall()

def print_logo():
    os.system('clear')
    print(bcolors.RED + bcolors.BOLD)
    print("""
     ___________             _____  .__  .__
     \___   ___/___ ______  /  _  \ |  | |  |
        |   | /    \|  ___\/  /_\  \|  | |  |
        |   |(  ()  )  |  /    |    \  |_|  |__
        |___| \____/|__|  \____|__  /____/____/
                                  \/
        {V} - github.com/bissisoft/torall
    """.format(V=VERSION) + bcolors.ENDC)

def usage():
    print_logo()
    print(bcolors.GREEN + bcolors.BOLD)
    print("        Usage: torall [option]" + bcolors.ENDC)
    print("""
        -s    --start      Start TorAll and redirect all traffic through TOR
        -x    --stop       Stop TorAll and redirect all traffic through clearnet
        -c    --change     Change tor identity -- get a new exit node and ip address
        -u    --update     Check for updated version with option to install
        -h    --help       Print this help and exit
    """)
    sys.exit()

def check_root():
    if os.geteuid() != 0:
        print("Run as root or with 'sudo' ^.^")
        sys.exit(0)

def alert_if_running():
    if os.path.exists('/var/lib/torall/started'):
        print_logo()
        print(MARGIN + bcolors.GREEN + bcolors.BOLD + 'TorAll is already running!' + bcolors.ENDC)
        print(MARGIN + bcolors.GREEN + 'All traffic is being redirected through TOR!' + bcolors.ENDC)
        print(MARGIN + bcolors.BLUE + 'Fetching current IP... ' + bcolors.GREEN + ip() + bcolors.ENDC)
        sys.exit()

def alert_if_clearnet():
    if not os.path.exists('/var/lib/torall/started'):
        print_logo()
        print(MARGIN + bcolors.RED + bcolors.BOLD + 'TorAll is NOT running!' + bcolors.ENDC)
        print(MARGIN + bcolors.RED + 'You are on the clearnet with your regular ip!')
        print(MARGIN + bcolors.BLUE + 'Fetching current IP... ' + bcolors.ENDC + ip())
        sys.exit()

def stop_tor_service():
    os.system('sudo systemctl stop tor')
    os.system('sudo fuser -k 9051/tcp > /dev/null 2>&1')
    print(t() + bcolors.BLUE + ' Stopping tor service... ' + bcolors.GREEN + '[done]' + bcolors.ENDC)

def switch_nameservers():
    os.system('sudo cp ' + RESOLV + ' ' + RESOLV_BAK)
    os.system('sudo cp ' + NAMESRVS + ' ' + RESOLV)
    print(t() + bcolors.BLUE  + ' Switching nameservers... ' + bcolors.GREEN + '[done]' + bcolors.ENDC)

def restore_nameservers():
    os.system('mv ' + RESOLV_BAK + ' ' + RESOLV)
    print(t() + bcolors.BLUE  + ' Restoring back your nameservers... ' + bcolors.GREEN + '[done]' + bcolors.ENDC)

def start_daemon():
    os.system('sudo -u ' + TORUID + ' tor -f /etc/tor/torallrc > /dev/null')
    print(t() + bcolors.BLUE  + ' Starting new tor daemon... ' + bcolors.GREEN + '[done]' + bcolors.ENDC)

def set_iptables():
    iptables_rules = open('/var/lib/torall/iptables.conf').read()
    os.system(iptables_rules % subprocess.getoutput('id -ur ' + TORUID))
    print(t() + bcolors.BLUE  + ' Setting up iptables rules... ' + bcolors.GREEN + '[done]' + bcolors.ENDC)

def flush_iptables():
    os.system('iptables -P INPUT ACCEPT')
    os.system('iptables -P FORWARD ACCEPT')
    os.system('iptables -P OUTPUT ACCEPT')
    os.system('iptables -t nat -F')
    os.system('iptables -t mangle -F')
    os.system('iptables -F')
    os.system('iptables -X')
    os.system('sudo fuser -k 9051/tcp > /dev/null 2>&1')
    print(t() + bcolors.BLUE  + ' Flushing iptables, resetting to default... ' + bcolors.GREEN + '[done]' + bcolors.ENDC)

def restart_network_manager():
    os.system('systemctl restart NetworkManager.service')
    print(t() + bcolors.BLUE  + ' Restarting NetworkManager... ' + bcolors.GREEN + '[done]' + bcolors.ENDC)

def ip():
    while True:
        try:
            response = get(IPAPI).json()
            ip = response["ip"]
        except:
            continue
        break
    return ip

signal.signal(signal.SIGINT, sigint_handler)

def start_torall():
    print_logo()
    alert_if_running()
    print(MARGIN + bcolors.GREEN + bcolors.BOLD + 'STARTING TorAll service...' + bcolors.ENDC)
    if os.system('systemctl is-active --quiet tor') == 0:
        stop_tor_service()
    switch_nameservers()
    start_daemon()
    set_iptables()
    print(t() + bcolors.BLUE + ' Fetching current IP... ' + bcolors.GREEN + ip() + bcolors.ENDC + '\n')
    print(MARGIN + bcolors.GREEN + bcolors.BOLD + 'All traffic is being redirected through TOR!' + bcolors.ENDC)
    os.system('touch /var/lib/torall/started')

def stop_torall():
    print_logo()
    alert_if_clearnet()
    print(MARGIN + bcolors.RED + bcolors.BOLD + 'STOPPING TorAll service...' + bcolors.ENDC)
    restore_nameservers()
    flush_iptables()
    restart_network_manager()
    print(t() + bcolors.BLUE  + ' Fetching current IP... ' + bcolors.ENDC + ip() + '\n')
    print(MARGIN + bcolors.RED + bcolors.BOLD + 'You are on the clearnet with your regular ip!' + bcolors.ENDC)
    os.system('rm /var/lib/torall/started')

def change_ip():
    print_logo()
    alert_if_clearnet()
    print(MARGIN + bcolors.GREEN + bcolors.BOLD + 'Changing exit node...' + bcolors.ENDC)
    print(t() + bcolors.BLUE  + ' Please wait...' + bcolors.ENDC)
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
    print(t() + bcolors.BLUE  + ' Requesting new circuit... ' + bcolors.GREEN + '[done]' + bcolors.ENDC)
    print(t() + bcolors.BLUE  + ' Fetching current IP... ' + bcolors.GREEN + ip() + bcolors.ENDC)

def check_update():
    print_logo()
    print(MARGIN + bcolors.BLUE + 'Checking for updates...' + bcolors.ENDC)
    print(MARGIN + bcolors.RED + 'Still in development... check back soon!' + bcolors.ENDC)

def main():
    check_root()
    if len(sys.argv) <= 1:
        check_update()
        usage()
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], 'sxcuh', [
            'start', 'stop', 'change', 'update', 'help'])
    except (getopt.GetoptError):
        usage()
        sys.exit(2)
    for (o, a) in opts:
        if o in ('-s', '--start'):
            start_torall()
        elif o in ('-x', '--stop'):
            stop_torall()
        elif o in ('-c', '--change'):
            change_ip()
        elif o in ('-u', '--update'):
            check_update()
        elif o in ('-h', '--help'):
            usage()
        else:
            usage()

if __name__ == '__main__':
    main()
