# TorAll

🧅 TorAll is an anonymization utility tool that redirects all of the system's internet traffic through the TOR network.
It's an improved fork variation of the good old [TorGhost](https://github.com/SusmithKrishnan/torghost). It redirects all internet traffic through SOCKS5 tor proxy, preventing DNS leaks and unsafe packets exiting the system.

- Auto disables and re-enables IPv6

- Auto disables and re-enables UFW firewall

- Spoofs all ethernet and wireless MAC addresses by default

- Supports GNU/Linux distributions with systemd based on Debian/Ubuntu and Arch Linux

![screenshot](https://bissisoft.com/torall.v2.0.1.png)

## Install on Debian/Ubuntu and Arch Linux distros with systemd!

```sh
git clone https://github.com/bissisoft/torall.git
cd torall
chmod +x build.sh
sudo ./build.sh
```

![screenshot](https://bissisoft.com/torall.v2.0.2.png)

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

![screenshot](https://bissisoft.com/torall.v2.0.3.png)

## Developed and tested on Kali Linux and Black Arch.

### With 🧡 from the [BissiSoft](https://bissisoft.com) team.

#### 🥳 Enjoy! 🎉
