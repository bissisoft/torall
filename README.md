# TorAll
🧅 TorAll is an anonymization utility tool that redirects all of the system's internet traffic through the TOR network. 🥸
It's an improved fork variation of the good old [TorGhost](https://github.com/SusmithKrishnan/torghost) 👻 It redirects all internet traffic through SOCKS5 tor proxy, preventing DNS leaks, and unsafe packets exiting the system.

- 1st we wanted to fix some bugs 🐞

- Then we also wanted to make it compatible with Arch Linux distros for the "BTW I use Arch" crowd 😜

- And lastly we wanted to add some enhancements and extra features such as:

  - [x] #7 Auto disabling IPv6 on start and re-enabling it back after stop (if it was enabled before the start).

  - [ ] https://github.com/bissisoft/torall/issues/9 - Integrate MAC address spoofing by default.

  - [ ] Other extra enhancements, feature requests, and good ideas by users like you. So, don't hesitate to open an issue with feature requests, ideas, questions, bug reports etc.


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

## 🥳 Enjoy! 🎉

### With 🧡 from the [BissiSoft](https://bissisoft.com) team.
