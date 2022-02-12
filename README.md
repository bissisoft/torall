# TorAll -- WIP (work in progress... not ready yet!)
TorAll is an anonymization utility tool that redirects all of the system's internet traffic through the TOR network.
It is a fork variation of [TorGhost](https://github.com/SusmithKrishnan/torghost)
## Install for Debian and Arch Linux distributions!
```sh
git clone https://github.com/bissisoft/torall.git
cd torall
chmod +x build.sh
./build.sh
```

## Usage
```sh
sudo torall [option]
```
### options
```sh
-s    --start      Start TorAll
-c    --change     Change the exit node and get a new ip address
-x    --stop       Stop TorAll & reset normal network
-u    --update     Checks for updates
-h    --help       Print this help and exit
```
