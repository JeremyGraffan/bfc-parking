# Installation

## OS
For the demo, you need to install a `raspbian lite (32-bit)` version.

## Install dependencies
- First install openvino 32-bit version on the raspberry, to do that, follow the guide on the official documentation : https://docs.openvino.ai/2022.3/openvino_docs_install_guides_installing_openvino_raspbian.html
- Add `source /opt/intel/openvino_2022/setupvars.sh` at the end of `~/.bashrc`
- Make sur you have `make`, `git`, `python3.9` and `opencv` installed : `sudo apt udpate && sudo apt install git make python3 python3-opencv`
- Install required python packages : `pip3 install requests psycopg2 numpy`
- Install docker : `curl -fsSL https://get.docker.com -o get-docker.sh` then `sudo sh get-docker.sh`
- Install docker compose : `sudo apt install docker-compose`
- Add your user to the docker group : `sudo usermod -aG docker pi` 

## Automatic cache sync
To sync the authorization cache automaticaly, add the sync script to the crontab :
- Open crontab editing with : `crontab -e`
- Add the line : `* * * * * /home/pi/bfc/app/sync.sh`