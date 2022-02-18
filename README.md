# TorAll
🧅 TorAll is an anonymization utility tool that redirects all of the system's internet traffic through the TOR network. 🥸
It's an improved fork variation of the good old [TorGhost](https://github.com/SusmithKrishnan/torghost) 👻 It redirects all internet traffic through SOCKS5 tor proxy, preventing DNS leaks, and unsafe packets exiting the system.

- First of all we wanted to fix some bugs 🐞 and maintain a repo with the latest updates and bug fixes.

- We also wanted to make it compatible with and support Arch Linux distributions for the "BTW I use Arch" crowd 😜

- And last but not least; We wanted to add some enhancements and extra features such as:

  - [x] [Auto disable IPv6](https://github.com/bissisoft/torall/issues/7) on start and re-enabling it back after stop (if it was enabled before the start).
  - [ ] [Integrate MAC address spoofing by default](https://github.com/bissisoft/torall/issues/9)
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
