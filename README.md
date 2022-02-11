# TorAll
TorAll is an anonymization utility tool that redirects all of the system's internet traffic through the TOR network.
It is a fork variation of [TorGhost](https://github.com/SusmithKrishnan/torghost)
##### Made for Debian and Arch Linux distributions!
## Install dependencies
### Debian/Ubuntu
```sh
sudo apt install tor python3-pip cython3
pip3 install stem requests
```
### Arch
```sh
sudo pacman -S tor python3-pip cython3
pip3 install stem requests
```
## Build C binary and install
### Debian/Ubuntu
```sh
git clone https://github.com/bissisoft/torall.git
cd torall
chmod +x build-deb.sh
sudo ./build-deb.sh
```
### Arch Linux
```sh
git clone https://github.com/bissisoft/torall.git
cd torall
chmod +x build-pac.sh
sudo ./build-pac.sh
```
## Usage
```sh
sudo torall [option]
```
### options
```sh
-s    --start      Start TorAll
-c    --change     Change the exit node and get a new ip address
-x    --stop       Stop TorAll
-u    --update     Checks for updates
-h    --help       Print this help and exit
```
