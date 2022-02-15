#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import getopt
import signal
import subprocess
from stem import Signal
from stem.control import Controller
from packaging import version
from requests import get

VERSION = "1.0"
IPAPI = "https://api.ipify.org/?format=json"
LATEST = "https://api.github.com/repos/bissisoft/torall/releases/latest"
TORUID = "tor" if os.path.exists('/usr/bin/pacman') else "debian-tor"
RESOLV = "/etc/resolv.conf"
RESOLVBAK = "/var/lib/torall/resolv.conf.bak"
NAMESRVS = "/var/lib/torall/nameservers.conf"
MARGIN = "        "


class clr:
    RED = '\033[31m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'


def sigint_handler(signum, frame):
    print("User interrupt ! shutting down")
    stop_torall()


def print_logo():
    os.system('clear')
    print(clr.RED + clr.BOLD)
    print("""
     ___________             _____  .__  .__
     \___   ___/___ ___ __  /  _  \ |  | |  |
        |   | /    \\  V\_\/  /_\  \|  | |  |
        |   |(  <>  )  |  /    |    \  |_|  |__
        |___| \____/|__|  \____|__  /____/____/
                                  \/
        v{V}  github.com/bissisoft/torall
    """.format(V=VERSION) + clr.ENDC)


def usage():
    print_logo()
    print(clr.GREEN + clr.BOLD)
    print("        Usage: torall [option]" + clr.ENDC)
    print("""
        -s    --start     Start TorAll and redirect all traffic through TOR
        -x    --stop      Stop TorAll and resume all traffic through clearnet
        -c    --change    Change identity -- Change exit node and ip address
        -u    --update    Check for updated version with option to upgrade
        -h    --help      Print this help and exit
    """)
    sys.exit()


def check_root():
    if os.geteuid() != 0:
        print("Run as root or with 'sudo' ^.^")
        sys.exit(0)


def alert_if_running():
    if os.path.exists('/var/lib/torall/started'):
        print_logo()
        print(MARGIN + clr.GREEN + clr.BOLD +
              'TorAll is already running!' + clr.ENDC)
        print(MARGIN + clr.GREEN +
              'All traffic is being redirected through TOR!' + clr.ENDC)
        print(MARGIN + clr.BLUE + 'Fetching current IP... ' +
              clr.GREEN + ip() + clr.ENDC)
        sys.exit()


def alert_if_clearnet():
    if not os.path.exists('/var/lib/torall/started'):
        print_logo()
        print(MARGIN + clr.RED + clr.BOLD + 'TorAll is NOT running!' + clr.ENDC)
        print(MARGIN + clr.RED + 'You are on the clearnet with your regular ip!')
        print(MARGIN + clr.BLUE + 'Fetching current IP... ' + clr.ENDC + ip())
        sys.exit()


def stop_tor_service():
    os.system('sudo systemctl stop tor')
    os.system('sudo fuser -k 9051/tcp > /dev/null 2>&1')
    print(clr.BLUE + 'Stopping tor service... ' + clr.ENDC)


def switch_nameservers():
    os.system('sudo cp ' + RESOLV + ' ' + RESOLVBAK)
    os.system('sudo cp ' + NAMESRVS + ' ' + RESOLV)
    print(clr.BLUE + 'Switching nameservers... ' + clr.ENDC)


def restore_nameservers():
    os.system('mv ' + RESOLVBAK + ' ' + RESOLV)
    print(clr.BLUE + 'Restoring back your nameservers... ' + clr.ENDC)


def start_daemon():
    os.system('sudo -u ' + TORUID + ' tor -f /etc/tor/torallrc > /dev/null')
    print(clr.BLUE + 'Starting new tor daemon... ' + clr.ENDC)


def set_iptables():
    iptables_rules = open('/var/lib/torall/iptables.conf').read()
    os.system(iptables_rules % subprocess.getoutput('id -ur ' + TORUID))
    print(clr.BLUE + 'Setting up iptables rules... ' + clr.ENDC)


def flush_iptables():
    os.system('iptables -P INPUT ACCEPT')
    os.system('iptables -P FORWARD ACCEPT')
    os.system('iptables -P OUTPUT ACCEPT')
    os.system('iptables -t nat -F')
    os.system('iptables -t mangle -F')
    os.system('iptables -F')
    os.system('iptables -X')
    os.system('sudo fuser -k 9051/tcp > /dev/null 2>&1')
    print(clr.BLUE + 'Flushing iptables, resetting to default... ' + clr.ENDC)


def restart_network_manager():
    os.system('systemctl restart NetworkManager.service')
    print(clr.BLUE + 'Restarting NetworkManager... ' + clr.ENDC)


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
    print(MARGIN + clr.GREEN + clr.BOLD +
          'STARTING TorAll service...' + clr.ENDC)
    if os.system('systemctl is-active --quiet tor') == 0:
        stop_tor_service()
    switch_nameservers()
    start_daemon()
    set_iptables()
    print(clr.BLUE + 'Fetching current IP... ' + clr.GREEN + ip() + clr.ENDC + '\n')
    print(MARGIN + clr.GREEN + clr.BOLD +
          'All traffic is being redirected through TOR!' + clr.ENDC)
    os.system('touch /var/lib/torall/started')


def stop_torall():
    print_logo()
    alert_if_clearnet()
    print(MARGIN + clr.RED + clr.BOLD + 'STOPPING TorAll service...' + clr.ENDC)
    restore_nameservers()
    flush_iptables()
    restart_network_manager()
    print(clr.BLUE + 'Fetching current IP... ' + clr.ENDC + ip() + '\n')
    print(MARGIN + clr.RED + clr.BOLD +
          'You are on the clearnet with your regular ip!' + clr.ENDC)
    os.system('rm /var/lib/torall/started')


def change_ip():
    print_logo()
    alert_if_clearnet()
    print(MARGIN + clr.GREEN + clr.BOLD + 'Changing exit node...' + clr.ENDC)
    print(clr.BLUE + 'Please wait...' + clr.ENDC)
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
    print(clr.BLUE + 'Requesting new circuit...' + clr.ENDC)
    print(clr.BLUE + 'Fetching current IP... ' + clr.GREEN + ip() + clr.ENDC)


def check_update():
    print_logo()
    response = get(LATEST).json()
    latest = response["tag_name"][1:]
    if version.parse(latest) > version.parse(VERSION):
        print(MARGIN + clr.GREEN + clr.BOLD +
              'New update available!\n' + clr.ENDC)
        print(MARGIN + 'Your TorAll version: ' + clr.RED + VERSION + clr.ENDC)
        print(MARGIN + 'Latest TorAll version: ' +
              clr.GREEN + latest + clr.ENDC + '\n')
        yes = {'yes', 'y', 'ye', ''}
        no = {'no', 'n'}
        user_input = False
        msg = MARGIN + clr.BOLD + "Upgrade to new version? [Y/n] " + clr.ENDC
        while not user_input:
            choice = input(msg).lower()
            if choice in yes:
                print('\n' + MARGIN + clr.GREEN + 'Upgrading...' + clr.ENDC + '\n')
                os.system('cd /tmp && git clone  https://github.com/bissisoft/torall')
                os.system('cd /tmp/torall && sudo ./build.sh')
                user_input = True
            elif choice in no:
                print('\n' + MARGIN + clr.RED + 'Upgrade aborted by user' + clr.ENDC)
                user_input = True
            else:
                msg = '\n' + MARGIN + "Please respond with 'yes' or 'no' "
    else:
        print(MARGIN + clr.RED + 'No new update available!\n' + clr.ENDC)
        print(MARGIN + 'Your version... ' + clr.GREEN + VERSION + clr.ENDC)
        print(MARGIN + 'Latest version: ' + clr.GREEN + latest + clr.ENDC + '\n')
        print(MARGIN + clr.BOLD + 'TorAll is up to date!')


def main():
    check_root()
    if len(sys.argv) <= 1:
        check_update()
        usage()
    try:
        (opts, args) = getopt.getopt(
            sys.argv[1:], 'sxcuh', ['start', 'stop', 'change', 'update', 'help']
        )
        if len(opts) == 0:
            usage()
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
