#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import getopt
import signal
import subprocess
from packaging import version
from requests import get
import time

VERSION = "1.5"
IPAPI = "https://api.ipify.org/?format=json"
LATEST = "https://api.github.com/repos/bissisoft/torall/releases/latest"
TORUID = "tor" if os.path.exists('/usr/bin/pacman') else "debian-tor"
MARGIN = "        "


class clr:
    RED = '\033[31m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    YELLOW = '\033[33m'


def sigint_handler(signum, frame):
    print("User interrupted! Stopping TorAll service...")
    stop_torall()


def print_logo():
    os.system('clear')
    print(clr.RED + clr.BOLD)
    print("""
         _______________          ____  ___  ___
        /____    _____//         /    \ \  \ \  \{R}
            /   //{Y}___{G}V/{R}   __ __ /  /\  \ \  \ \  \{R}
           /   /{Y}/  _  \. {R}/  ,._|  //_\  \ \  \ \  \{R}
         _/   ({Y}(  (O)  )){R}  // /  ______  \ \  \_\  \_
        /_____//{Y}\_____//{R}\_//  \_//     \_// \__//\__//
        {G}v{V} {B}- github.com/bissisoft/torall
    """.format(R=clr.RED, G=clr.GREEN, B=clr.BLUE, Y=clr.YELLOW, V=VERSION))
    print(clr.END)


def usage():
    print_logo()
    print(MARGIN + clr.BOLD + "Usage: torall [option]" + clr.END)
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


def backup_sysctl():
    print(MARGIN + clr.BLUE + 'Backing up sysctl...' + clr.END)
    os.system('sysctl -a >/var/lib/torall/sysctl.conf.bak')


def restore_sysctl():
    print(MARGIN + clr.BLUE + 'Restoring sysctl...' + clr.END)
    os.system('sysctl -p /var/lib/torall/sysctl.conf.bak >/dev/null 2>&1')


def disable_ipv6():
    print(MARGIN + clr.BLUE + 'Disabling IPv6...' + clr.END)
    os.system('sysctl -w net.ipv6.conf.all.disable_ipv6=1 >/dev/null')
    os.system('sysctl -w net.ipv6.conf.default.disable_ipv6=1 >/dev/null')


def alert_if_running():
    if os.path.exists('/var/lib/torall/started'):
        print_logo()
        print(MARGIN + clr.GREEN + clr.BOLD + 'TorAll is running...' + clr.END)
        print(MARGIN + clr.BLUE + 'Fetching current IP... ' +
              clr.GREEN + ip() + clr.END)
        print(MARGIN + clr.GREEN +
              'All traffic is being redirected through TOR!' + clr.END)
        sys.exit()


def alert_if_clearnet():
    if not os.path.exists('/var/lib/torall/started'):
        print_logo()
        print(MARGIN + clr.RED + clr.BOLD + 'TorAll is NOT running!' + clr.END)
        print(MARGIN + clr.BLUE + 'Fetching current IP... ' + clr.END + ip())
        print(MARGIN + clr.RED + 'You are on the clearnet with your regular ip!')
        sys.exit()


def switch_nameservers():
    print(MARGIN + clr.BLUE + 'Switching nameservers...' + clr.END)
    os.system('cp /etc/resolv.conf /var/lib/torall/resolv.conf.bak')
    os.system('cp /var/lib/torall/nameservers.conf /etc/resolv.conf')


def restore_nameservers():
    print(MARGIN + clr.BLUE + 'Restoring nameservers...' + clr.END)
    os.system('mv /var/lib/torall/resolv.conf.bak /etc/resolv.conf')


def spoof_mac_addresses():
    print(MARGIN + clr.BLUE + 'Spoofing mac addresses...' + clr.END)
    for iface in os.listdir('/sys/class/net/'):
        if iface != 'lo':
            os.system('macchanger -r ' + iface + ' >/dev/null 2>&1')


def revert_mac_addresses():
    print(MARGIN + clr.BLUE + 'Reverting mac addresses...' + clr.END)
    for iface in os.listdir('/sys/class/net/'):
        if iface != 'lo':
            os.system('macchanger -p ' + iface + ' >/dev/null 2>&1')


def start_daemon():
    print(MARGIN + clr.BLUE + 'Starting new tor daemon...' + clr.END)
    os.system('sudo -u ' + TORUID + ' tor -f /etc/tor/torallrc >/dev/null')


def stop_daemon():
    print(MARGIN + clr.BLUE + 'Stopping tor daemon...' + clr.END)
    os.system('systemctl stop tor.service')
    os.system('fuser -k 9051/tcp >/dev/null 2>&1')


def disable_firewall():
    if os.system('command -v ufw >/dev/null') == 0:
        if os.system('! ufw status | grep -q inactive$') == 0:
            print(MARGIN + clr.RED + 'Disabling UFW firewall...')
            os.system('ufw disable >/dev/null 2>&1')
        else:
            backup_iptables()
    else:
        backup_iptables()


def enable_firewall():
    if os.path.exists('/var/lib/torall/iptables.rules.bak'):
        restore_iptables()
        os.system('rm /var/lib/torall/iptables.rules.bak')
    else:
        print(MARGIN + clr.RED + 'Enabling back UFW firewall...')
        os.system('ufw enable >/dev/null 2>&1')


def backup_iptables():
    print(MARGIN + clr.BLUE + 'Backing up iptables rules...' + clr.END)
    os.system('iptables-save >/var/lib/torall/iptables.rules.bak')


def restore_iptables():
    print(MARGIN + clr.BLUE + 'Restoring iptables rules...' + clr.END)
    os.system('iptables-restore </var/lib/torall/iptables.rules.bak')


def set_iptables():
    print(MARGIN + clr.BLUE + 'Setting up new iptables rules...' + clr.END)
    iptables_rules = open('/var/lib/torall/iptables.conf').read()
    os.system(iptables_rules % subprocess.getoutput('id -ur ' + TORUID))


def flush_iptables():
    print(MARGIN + clr.BLUE + 'Flushing iptables...' + clr.END)
    os.system('iptables -P INPUT ACCEPT')
    os.system('iptables -P FORWARD ACCEPT')
    os.system('iptables -P OUTPUT ACCEPT')
    os.system('iptables -t nat -F')
    os.system('iptables -t mangle -F')
    os.system('iptables -F')
    os.system('iptables -X')


def restart_network_manager():
    print(MARGIN + clr.BLUE + 'Restarting NetworkManager...' + clr.END)
    os.system('systemctl restart NetworkManager.service')


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
    print(MARGIN + clr.GREEN + clr.BOLD + 'STARTING TorAll...' + clr.END)
    if os.system('systemctl is-active --quiet tor') == 0:
        stop_daemon()
    switch_nameservers()
    backup_sysctl()
    disable_ipv6()
    spoof_mac_addresses()
    start_daemon()
    disable_firewall()
    set_iptables()
    print(MARGIN + clr.BLUE + 'Fetching new IP... ' + clr.GREEN + ip() + clr.END)
    print('\n' + MARGIN + clr.GREEN + clr.BOLD +
          'All traffic is being redirected through TOR!' + clr.END)
    os.system('touch /var/lib/torall/started')


def stop_torall():
    print_logo()
    alert_if_clearnet()
    print(MARGIN + clr.RED + clr.BOLD + 'STOPPING TorAll service...' + clr.END)
    restore_nameservers()
    restore_sysctl()
    flush_iptables()
    stop_daemon()
    revert_mac_addresses()
    enable_firewall()
    restart_network_manager()
    print(MARGIN + clr.BLUE + 'Fetching current IP... ' + clr.END + ip() + '\n')
    print(MARGIN + clr.RED + clr.BOLD +
          'You are on the clearnet with your regular ip!' + clr.END)
    os.system('rm /var/lib/torall/started')


def change_id():
    print_logo()
    alert_if_clearnet()
    print(MARGIN + clr.GREEN + clr.BOLD + 'Changing tor identity...' + clr.END)
    print(MARGIN + clr.BLUE + 'Requesting new onion circuit...' + clr.END)
    os.system('fuser -k 9051/tcp >/dev/null 2>&1')
    time.sleep(1)
    os.system('sudo -u ' + TORUID + ' tor -f /etc/tor/torallrc >/dev/null')
    print(MARGIN + clr.BLUE + 'Fetching new IP... ' + clr.GREEN + ip() + clr.END)


def check_update():
    print_logo()
    response = get(LATEST).json()
    latest = response["tag_name"][1:]
    if version.parse(latest) > version.parse(VERSION):
        print(MARGIN + clr.GREEN + clr.BOLD +
              'New update available!\n' + clr.END)
        print(MARGIN + 'Your TorAll version: ' + clr.RED + VERSION + clr.END)
        print(MARGIN + 'Latest TorAll version: ' +
              clr.GREEN + latest + clr.END + '\n')
        yes = {'yes', 'y', 'ye', ''}
        no = {'no', 'n'}
        user_input = False
        msg = MARGIN + clr.BOLD + "Update to new version? [Y/n] " + clr.END
        while not user_input:
            choice = input(msg).lower()
            if choice in yes:
                print('\n' + MARGIN + clr.GREEN +
                      'Updating your version...' + clr.END + '\n')
                os.system('mv /usr/bin/torall /tmp/torall.old')
                os.system(
                    'cd /tmp && git clone  https://github.com/bissisoft/torall')
                os.system('cd /tmp/torall && sudo ./build.sh')
                print('\n' + MARGIN + clr.GREEN + 'Done!' + clr.END + '\n')
                input(MARGIN + clr.BOLD + 'Press any key to restart ^.^  ')
                os.system('torall')
                sys.exit()
            elif choice in no:
                print('\n' + MARGIN + clr.RED +
                      'Update aborted by user' + clr.END)
                user_input = True
            else:
                msg = '\n' + MARGIN + "Please respond with 'yes' or 'no' "
    else:
        print(MARGIN + clr.RED + 'No new update available!\n' + clr.END)
        print(MARGIN + 'Your version... ' + clr.GREEN + VERSION + clr.END)
        print(MARGIN + 'Latest version: ' +
              clr.GREEN + latest + clr.END + '\n')
        print(MARGIN + clr.BOLD + 'TorAll is up to date!')


def main():
    check_root()
    if len(sys.argv) <= 1:
        check_update()
        usage()
    try:
        (opts, args) = getopt.getopt(
            sys.argv[1:], 'sxcuh', [
                'start', 'stop', 'change', 'update', 'help']
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
            change_id()
        elif o in ('-u', '--update'):
            check_update()
        elif o in ('-h', '--help'):
            usage()
        else:
            usage()


if __name__ == '__main__':
    main()
