# TorAll
TorAll is an anonymization utility tool that redirects all of the system's internet traffic through the TOR network.
It's an improved fork variation of the old [TorGhost](https://github.com/SusmithKrishnan/torghost)

![screenshot](https://bissisoft.com/torall_2.png)
## Install on Debian and/or Arch Linux distributions!
```sh
git clone https://github.com/bissisoft/torall.git
cd torall
chmod +x build.sh
sudo ./build.sh
```

![screenshot](https://bissisoft.com/torall_1.png)
## Usage
```sh
sudo torall [option]
```
### options
```sh
-s    --start     Start TorAll and redirect all traffic through TOR
-x    --stop      Stop TorAll and resume all traffic through clearnet
-c    --change    Change identity -- Change exit node and ip address
-u    --update    Check for updated version with option to upgrade
-h    --help      Print this help and exit
```

![screenshot](https://bissisoft.com/torall_3.png)
