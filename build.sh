echo "TorAll installer v1.0"
echo "Installing prerequisites "
# Support for Debian and ArchLinux.
if command -v pacman > /dev/null; then
    TORUID="tor"
    sudo pacman -S --quiet --noconfirm --needed tor python-pip cython
    echo "Installing dependencies "
    sudo pip3 install stem requests
elif command -v apt > /dev/null; then
    TORUID="debian-tor"
    sudo apt -y install tor python3-pip cython3
    echo "Installing dependencies "
    pip3 install stem requests
else
    echo "Unknown distro! TorAll currently supports only Arch and Debian based distros."
    exit
fi
# Get the exact python3 version
PY3VER=$(python3 --version | awk '{print$2}' | cut -f 1,2 -d .)
# Generate C code from the python scrypt file
mkdir build
cd build
# TODO
