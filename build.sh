#!/bin/bash

RED=""
REDB=""
YELLOW=""
YELLOWB=""
GREEN=""
GREENB=""
BLUE=""
BLUEB=""
RESET=""

if [ -t 1 ]; then
    if tput setaf 0 &>/dev/null; then
        RED="$(tput setaf 1)"
        GREEN="$(tput setaf 2)"
        YELLOW="$(tput setaf 3)"
        BLUE="$(tput setaf 4)"
        RESET="$(tput sgr0)"
        BOLD="$(tput bold)"
    else
        RED="\e[31m"
        GREEN="\e[32m"
        YELLOW="\e[33m"
        BLUE="\e[34m"
        RESET="\e[0m"
        BOLD="\e[1m"
    fi
    GREENB="${BOLD}${GREEN}"
    REDB="${BOLD}${RED}"
    YELLOWB="${BOLD}${YELLOW}"
    BLUEB="${BOLD}${BLUE}"
fi

BACKUPDIR="/var/lib/torall"
NAMESRVS="${BACKUPDIR}/nameservers.conf"
IPTABLES="${BACKUPDIR}/iptables.conf"
TORALLRC="/etc/tor/torallrc"

err() {
    echo "${REDB}[ERROR]${RESET} --> ${@}"
    exit 1
}

warn() {
    echo "${YELLOWB}[WARNING]${RESET} --> ${@}"
}

info() {
    echo "${BLUEB}[INFO]${RESET} --> ${@}"
}

success() {
    echo "${GREENB}[SUCCESS]${RESET} --> ${@}"
}

check_root() {
    if [ $(id -u) -ne 0 ]; then
        err "Run as root or with 'sudo' ^.^"
    fi
}

backup_dir() {
    if [ ! -d $BACKUPDIR ]; then
        mkdir -p $BACKUPDIR
    fi
}

prerequisites() {
    info "Starting TorAll Installer v1.5"
    info "Installing prerequisites "
    if command -v pacman > /dev/null; then
        pacman -S --quiet --noconfirm --needed tor python-pip cython gcc
        info "Installing dependencies "
        pip3 install requests
    elif command -v apt > /dev/null; then
        apt -y --quiet install tor python3-pip cython3 gcc
        info "Installing dependencies "
        pip3 install requests
    else
        err "Unknown distro! TorAll currently supports only Arch and Debian based distros."
    fi
}

create_torallrc() {
    info "Creating torallrc file"
    cat >$TORALLRC <<EOF
# generated by TorAll
VirtualAddrNetwork 10.0.0.0/10
AutomapHostsOnResolve 1
TransPort 9040
DNSPort 5353
ControlPort 9051
RunAsDaemon 1
EOF
    if [ $? -eq 0 ]; then
        success "Created torallrc file"
        chmod 644 $TORALLRC
    else
        err "Could not create torallrc file"
    fi
}

create_nameservers() {
    info "Creating nameservers file"
    cat >$NAMESRVS <<EOF
# generated by TorAll
nameserver 127.0.0.1
nameserver 1.1.1.1
nameserver 1.0.0.1
EOF
    if [ $? -eq 0 ]; then
        success "Created nameservers file"
        chmod 644 $NAMESRVS
    else
        err "Could not create torallrc file"
    fi
}

create_iptables_rules() {
    info "Creating iptables rules file"
    cat >$IPTABLES <<EOF
TORUID=%s
TRANSPORT="9040"
NONTOR="192.168.1.0/24 192.168.0.0/24"

iptables -F
iptables -t nat -F
iptables -t nat -A OUTPUT -m owner --uid-owner \$TORUID -j RETURN
iptables -t nat -A OUTPUT -p udp --dport 53 -j REDIRECT --to-ports 5353
for NET in \$NONTOR 127.0.0.0/9 127.128.0.0/10; do
    iptables -t nat -A OUTPUT -d \$NET -j RETURN
done
iptables -t nat -A OUTPUT -p tcp --syn -j REDIRECT --to-ports \$TRANSPORT
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
for NET in \$NONTOR 127.0.0.0/8; do
    iptables -A OUTPUT -d \$NET -j ACCEPT
done
iptables -A OUTPUT -m owner --uid-owner \$TORUID -j ACCEPT
iptables -A OUTPUT -j REJECT
EOF
    if [ $? -eq 0 ]; then
        success "Created iptables rules file"
        chmod 644 $IPTABLES
    else
        err "Could not create iptables rules file"
    fi
}

generate_c_file() {
    info "Generating C code from the python scrypt file"
    mkdir build
    cd build
    cython3 ../torall.py --embed -o torall.c --verbose
    if [ $? -eq 0 ]; then
        success "Generated C code"
    else
        err "Unable to generate C code using cython3"
    fi
}

compile_it() {
    info "Compiling the C code to a static binary file"
    PY3VER=$(python3 --version | awk '{print$2}' | cut -f 1,2 -d .)
    gcc -Os -I /usr/include/python${PY3VER} -o torall torall.c -lpython${PY3VER} -lpthread -lm -lutil -ldl
    if [ $? -eq 0 ]; then
        success "Compiled to a static binary file"
    else
        err "Compilation failed"
    fi
}

install() {
    info "Copying the binary file to /usr/bin"
    sudo cp -r torall /usr/bin/
    if [ $? -eq 0 ]; then
        success "Copied the binary to /usr/bin"
    else
        err "Unable to copy binary to /usr/bin"
    fi
}

main() {
    check_root
    backup_dir
    prerequisites
    create_torallrc
    create_nameservers
    create_iptables_rules
    generate_c_file
    compile_it
    install
}

main
