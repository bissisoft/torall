#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import geteuid, system, path, listdir
from sys import argv, exit
from getopt import getopt, GetoptError
from subprocess import getoutput
from json import loads, JSONDecodeError
from time import sleep

VER = "2.0"
LATEST = "https://api.github.com/repos/bissisoft/torall/releases/latest"
TORUID = "debian-tor" if path.exists('/usr/bin/apt') else "tor"
TORURL = "https://check.torproject.org/api/ip"
MARGIN = "        "


class clr:
    END = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[31m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[33m'


def print_logo():
    system('clear')
    print(clr.RED + clr.BOLD)
    print("""
         _______________          ____  ___  ___
        /____    _____//         /    \ \  \ \  \{R}
            /   //{Y}___{G}V/{R}   __ __ /  /\  \ \  \ \  \{R}
           /   /{Y}/  _  \. {R}/  ,._|  //_\  \ \  \ \  \{R}
         _/   ({Y}(  (O)  )){R}  // /  ______  \ \  \_\  \_
        /_____//{Y}\_____//{R}\_//  \_//     \_// \__//\__//
        {G}v{V} {B}- github.com/bissisoft/torall
    """.format(R=clr.RED, G=clr.GREEN, B=clr.BLUE, Y=clr.YELLOW, V=VER))
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
    exit()


def check_root():
    if geteuid() != 0:
        print("Run as root or with 'sudo' ^.^")
        exit()


def restore_sysctl():
    system('sysctl -p /var/lib/torall/sysctl.conf.bak >/dev/null 2>&1')
    sleep(0.5)


def set_new_sysctl():
    system('sysctl -a >/var/lib/torall/sysctl.conf.bak')
    print(MARGIN + clr.BLUE + 'Disabling IPv6...' + clr.END)
    system('sysctl -w net.ipv6.conf.all.disable_ipv6=1 >/dev/null 2>&1')
    system('sysctl -w net.ipv6.conf.default.disable_ipv6=1 >/dev/null 2>&1')
    sleep(0.5)


def alert_if_running():
    if path.exists('/var/lib/torall/started'):
        print_logo()
        print(MARGIN + clr.GREEN + clr.BOLD + 'TorAll is running...' + clr.END)
        print(MARGIN + clr.BLUE + 'Fetching current IP... ' + clr.GREEN + ip())
        print(clr.BOLD)
        print(MARGIN + 'All traffic is being redirected through TOR!')
        print(clr.END)
        exit()


def alert_if_clearnet():
    if not path.exists('/var/lib/torall/started'):
        print_logo()
        print(MARGIN + clr.RED + clr.BOLD + 'TorAll is NOT running!' + clr.END)
        print(MARGIN + clr.BLUE + 'Fetching current IP... ' + clr.RED + ip())
        print(clr.BOLD)
        print(MARGIN + 'You are on the clearnet with your regular ip!')
        print(clr.END)
        exit()


def switch_nameservers():
    print(MARGIN + clr.BLUE + 'Switching nameservers...' + clr.END)
    system('cp /etc/resolv.conf /var/lib/torall/resolv.conf.bak')
    system('cp /var/lib/torall/nameservers.conf /etc/resolv.conf')
    sleep(0.5)


def restore_nameservers():
    print(MARGIN + clr.BLUE + 'Restoring nameservers...' + clr.END)
    system('mv /var/lib/torall/resolv.conf.bak /etc/resolv.conf')
    sleep(0.5)


def spoof_mac_addresses():
    print(MARGIN + clr.BLUE + 'Spoofing mac addresses...' + clr.END)
    for interface in listdir('/sys/class/net/'):
        if interface != 'lo' and interface[0] == 'e':
            system('macchanger -r ' + interface + ' >/dev/null 2>&1')
        elif interface != 'lo' and interface[0] == 'w':
            system('ip link set ' + interface + ' down')
            system('macchanger -r ' + interface + ' >/dev/null 2>&1')
            system('ip link set ' + interface + ' up')
    sleep(1)


def revert_mac_addresses():
    print(MARGIN + clr.BLUE + 'Resetting mac addresses...' + clr.END)
    for interface in listdir('/sys/class/net/'):
        if interface != 'lo' and interface[0] == 'e':
            system('macchanger -p ' + interface + ' >/dev/null 2>&1')
        elif interface != 'lo' and interface[0] == 'w':
            system('ip link set ' + interface + ' down')
            system('macchanger -p ' + interface + ' >/dev/null 2>&1')
            system('ip link set ' + interface + ' up')
    sleep(1)


def start_daemon():
    print(MARGIN + clr.BLUE + 'Starting new tor daemon...' + clr.END)
    system('sudo -u ' + TORUID + ' tor -f /etc/tor/torallrc >/dev/null')
    sleep(0.5)


def stop_daemon():
    print(MARGIN + clr.BLUE + 'Stopping tor daemon...' + clr.END)
    system('systemctl stop tor.service')
    system('fuser -k 9051/tcp >/dev/null 2>&1')
    sleep(0.5)


def disable_firewall():
    if system('command -v ufw >/dev/null') == 0:
        if system('! ufw status | grep -q inactive$') == 0:
            print(MARGIN + clr.BLUE + 'Disabling UFW firewall...')
            system('ufw disable >/dev/null 2>&1')
        else:
            backup_iptables()
    else:
        backup_iptables()
    sleep(0.5)


def enable_firewall():
    if path.exists('/var/lib/torall/iptables.rules.bak'):
        restore_iptables()
        system('rm /var/lib/torall/iptables.rules.bak')
    else:
        print(MARGIN + clr.BLUE + 'Enabling back UFW firewall...')
        system('ufw enable >/dev/null 2>&1')
    sleep(0.5)


def backup_iptables():
    print(MARGIN + clr.BLUE + 'Backing up iptables rules...' + clr.END)
    system('iptables-save >/var/lib/torall/iptables.rules.bak')
    sleep(0.5)


def restore_iptables():
    print(MARGIN + clr.BLUE + 'Restoring iptables rules...' + clr.END)
    system('iptables-restore </var/lib/torall/iptables.rules.bak')
    sleep(0.5)


def set_iptables():
    print(MARGIN + clr.BLUE + 'Setting up iptables rules...' + clr.END)
    iptables_rules = open('/var/lib/torall/iptables.conf').read()
    system(iptables_rules % getoutput('id -ur ' + TORUID))
    sleep(0.5)


def flush_iptables():
    # print(MARGIN + clr.BLUE + 'Flushing iptables...' + clr.END)
    system('iptables -P INPUT ACCEPT')
    system('iptables -P FORWARD ACCEPT')
    system('iptables -P OUTPUT ACCEPT')
    system('iptables -t nat -F')
    system('iptables -t mangle -F')
    system('iptables -F')
    system('iptables -X')
    sleep(0.5)


def restart_network_manager():
    print(MARGIN + clr.BLUE + 'Restarting NetworkManager...' + clr.END)
    system('systemctl restart --now NetworkManager.service')
    sleep(1)


def ip():
    ip = 'unknown'
    try:
        ip = getoutput('curl -s --max-time 10 https://api.ipify.org')
        sleep(1)
    except KeyboardInterrupt:
        return "User interrupted!"
    if ip == 'unknown':
        try:
            ip = getoutput('curl -s --max-time 10 https://ip.me')
            sleep(1)
        except KeyboardInterrupt:
            return "User interrupted!"
    return ip


def check_tor_network(task):
    if task == 'change':
        print(MARGIN + clr.BLUE + 'Requesting new onion circuit...' + clr.END)
    else:
        print(MARGIN + clr.BLUE + 'Checking tor network status...' + clr.END)
    try:
        status = getoutput('curl -s --max-time 30 ' + TORURL)
        sleep(1)
        connected_to_tor = loads(status)['IsTor']
        tor_ip = loads(status)['IP']
    except JSONDecodeError:
        print('JSONDecodeError... TODO!')
        print('status = ' + status)
        # TODO: backtrack!
        exit()
    except KeyboardInterrupt:
        print('user interupted... TODO!')
        # TODO: backtrack!
        exit()
    if task == 'start' and connected_to_tor:
        system('touch /var/lib/torall/started')
        exit_node = clr.GREEN + tor_ip
        print(MARGIN + clr.BLUE + 'Current exit node is: ' + exit_node)
        print(clr.BOLD)
        print(MARGIN + 'All traffic is being redirected through TOR!')
        print(clr.END)
    elif task == 'start' and not connected_to_tor:
        # TODO: backtrack!
        print(clr.RED + clr.BOLD)
        print(MARGIN + 'Huston we have a problem!!')
        print(clr.END)
    elif task == 'stop' and connected_to_tor:
        # TODO: give me something to do!
        print(clr.GREEN + clr.BOLD)
        print(MARGIN + 'Hmmm you are still on the TOR network!')
        print(clr.END)
    elif task == 'stop' and not connected_to_tor:
        system('rm /var/lib/torall/started')
        home_ip = clr.RED + tor_ip
        print(MARGIN + clr.BLUE + 'Fetching current IP... ' + home_ip)
        print(clr.BOLD)
        print(MARGIN + 'You are on the clearnet with your regular ip!')
        print(clr.END)
    elif task == 'change' and connected_to_tor:
        exit_node = clr.GREEN + tor_ip
        print(MARGIN + clr.BLUE + 'Fetching new IP... ' + exit_node)
        print(clr.BOLD)
        print(MARGIN + 'All traffic is being redirected through TOR!')
        print(clr.END)
    elif task == 'change' and not connected_to_tor:
        # TODO: backtrack!
        print(clr.RED + clr.BOLD)
        print(MARGIN + 'Huston we have a problem!!')
        print(clr.END)
    exit()


def start_torall():
    print_logo()
    alert_if_running()
    print(MARGIN + clr.GREEN + clr.BOLD + 'STARTING TorAll...' + clr.END)
    if system('systemctl is-active --quiet tor') == 0:
        stop_daemon()
    set_new_sysctl()
    switch_nameservers()
    spoof_mac_addresses()
    start_daemon()
    disable_firewall()
    set_iptables()
    check_tor_network('start')


def stop_torall():
    print_logo()
    alert_if_clearnet()
    print(MARGIN + clr.RED + clr.BOLD + 'STOPPING TorAll service...' + clr.END)
    stop_daemon()
    restore_nameservers()
    restore_sysctl()
    flush_iptables()
    revert_mac_addresses()
    enable_firewall()
    restart_network_manager()
    check_tor_network('stop')


def change_id():
    print_logo()
    alert_if_clearnet()
    print(MARGIN + clr.GREEN + clr.BOLD + 'Changing tor identity...' + clr.END)
    system('fuser -k 9051/tcp >/dev/null 2>&1')
    sleep(1)
    system('sudo -u ' + TORUID + ' tor -f /etc/tor/torallrc >/dev/null')
    check_tor_network('change')


def check_update():
    print_logo()
    latest = '0'
    interupted = False
    try:
        latest = getoutput('curl -s --max-time 30 ' + LATEST)
        sleep(1)
    except KeyboardInterrupt:
        interupted = True
    if not interupted and latest != '0':
        try:
            latest = loads(latest)["tag_name"][1:]
        except JSONDecodeError:
            # TODO: a better check for github api limit responses...
            print(MARGIN + clr.RED + 'GitHub api limit reached')
            print(MARGIN + 'Try again in a few minutes or with another ip')
            print(clr.END)
    if latest > VER:
        print(MARGIN + clr.GREEN + clr.BOLD + 'New update available!')
        print(clr.END)
        print(MARGIN + 'Your TorAll version: ' + clr.RED + VER + clr.END)
        print(MARGIN + 'Latest TorAll version: ' + clr.GREEN + latest)
        print(clr.END)
        yes = {'yes', 'y', 'ye', ''}
        no = {'no', 'n'}
        user_input = False
        msg = MARGIN + clr.BOLD + "Update to new version? [Y/n] " + clr.END
        while not user_input:
            choice = input(msg).lower()
            if choice in yes:
                print('\n' + MARGIN + clr.GREEN + 'Updating your version...')
                print(clr.END)
                system('mv /usr/bin/torall /tmp/torall.old')
                system('cd /tmp')
                system('git clone https://github.com/bissisoft/torall')
                system('cd /tmp/torall && sudo ./build.sh')
                print('\n' + MARGIN + clr.GREEN + 'Done!' + clr.END + '\n')
                input(MARGIN + clr.BOLD + 'Press any key to restart ^.^  ')
                system('torall')
                exit()
            elif choice in no:
                print('\n' + MARGIN + clr.RED + 'Update aborted by user')
                print(clr.END)
                user_input = True
            else:
                msg = '\n' + MARGIN + "Please respond with 'yes' or 'no' "
    else:
        print(MARGIN + clr.RED + 'No new update available!\n' + clr.END)
        print(MARGIN + 'Your version... ' + clr.GREEN + VER + clr.END)
        print(MARGIN + 'Latest version: ' + clr.GREEN + latest)
        print(clr.END)
        print(MARGIN + clr.BOLD + 'TorAll is up to date!')


def main():
    check_root()
    if len(argv) <= 1:
        check_update()
        usage()
    try:
        (opts, args) = getopt(
            argv[1:], 'sxcuh', [
                'start', 'stop', 'change', 'update', 'help']
        )
        if len(opts) == 0:
            usage()
    except GetoptError:
        usage()
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
