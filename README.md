# TorAll
🧅 TorAll is an anonymization utility tool that redirects all of the system's internet traffic through the TOR network. 🥸
It's an improved fork variation of the good old [TorGhost](https://github.com/SusmithKrishnan/torghost) 👻 It redirects all internet traffic through SOCKS5 tor proxy, preventing DNS leaks, and unsafe packets exiting the system.

## Features
- **TorAll installs on and supports:**
  - GNU/Linux distributions based on **Arch Linux**.
  - GNU/Linux distributions based on **Debian/Ubuntu**.
- [Auto disable/re-enable IPv6](https://github.com/bissisoft/torall/issues/7)
  - TorAll will auto disable IPv6 when it starts in order to prevent IPv6 leaks.
  - IPv6 will be re-enabled when it stops (if it was active before the start).
- [MAC address spoofing by default](https://github.com/bissisoft/torall/issues/9)
  - TorAll will spoof all network interface mac addresses when it starts.
  - Reset the spoofed interfaces to the original, permanent hardware MAC when it stops.
- [Auto disables/re-enables UFW firewall](https://github.com/bissisoft/torall/issues/5) (if it's status is active) as it conflicts with the iptables manipulations; However, it is recommended to manually disable any firewall that is active.
- **Other extra enhancements...** From feature requests and ideas by users like you. So, don't hesitate to open issues with feature requests, ideas, questions, bug reports etc.

![screenshot](https://bissisoft.com/torall.v1.0.1.png)

## Install on Debian and/or Arch Linux distributions!
```sh
git clone https://github.com/bissisoft/torall.git
cd torall
chmod +x build.sh
sudo ./build.sh
```

![screenshot](https://bissisoft.com/torall.v1.0.2.png)

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

![screenshot](https://bissisoft.com/torall.v1.0.3.png)

## Developed and tested on Kali Linux and Black Arch.

### With 🧡 from the [BissiSoft](https://bissisoft.com) team.

#### 🥳 Enjoy! 🎉
