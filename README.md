# Installation cloud
## OS
For the demo cloud, you need to have an os with `docker` and `docker-compose` installed.

## Configuration
- Clone this repo.
- Build the licence plate fake api docker image : `cd LicencePlateApi` then `docker build -t neicureuil/plate-api:latest /LicencePlateApi/Dockerfile` 
- First deploy all the cloud with docker compose : `docker-compose -f docker-orchrator.yaml up -d`
- Open nodered : `http://localhost:1880`
- Import the flow `orchestrator-flow.json` inside nodered
- Open the database web ui : `http://localhost:8080`
- Login to the bdd with type : `postgres`, username : `user`, password : `password`, database : `bfc`, host: `database`
- Launch the script `sql_init.sql` from the web ui in the `Import` tab.

# Installation raspberry

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
- Create working directory : `mkdir /home/pi/bfc && cd /home/pi/bfc` 
- Clone the sdk in the work folder : `git clone https://github.com/DoubangoTelecom/ultimateALPR-SDK/tree/master --depth=1`
- Create symbolic link : `ln -s ultimateALPR-SDK-master/samples/python/recognizer app`
- Add execution perms to lib : `sudo chmod +x ultimateALPR-SDK-master/binaries/raspbian/armv7l/libultimate_alpr-sdk.so`
- Add execution perms to setup : `sudo chmod +x ultimateALPR-SDK-master/binaries/raspbian/armv7l/python_setup.sh` and `sudo chmod +x ultimateALPR-SDK-master/python/recognizer/run_rpi_armv7l.sh`
- Build sdk : `cd /home/pi/bfc/app` and `./run_rpi_armv7l.sh`

## Install app
- To install the app copy the content of the folder `Raspberry` of this repository to the folder `/home/pi/bfc/app`
- Go to the app folder `cd /home/pi/bfc/app`
- Update the cloud ip in the file : `recognizer2.py` and `sync.py`
- Add rights to files : `sudo chmod +x run_detect.sh run_verba.sh sync.sh`
- Start the cache database : `docker-compose -f docker-compose.yml up -d`
- Start the first sync manually : `./sync.sh` 

## Automatic cache sync
To sync the authorization cache automaticaly, add the sync script to the crontab :
- Open crontab editing with : `crontab -e`
- Add the line : `* * * * * /home/pi/bfc/app/sync.sh`

# Start demos
## Demo information sign
- Start the script `run_detect.sh` in `/home/pi/bfc/app`

## Demo verbalization
- Start the script `run_verba.sh` in `/home/pi/bfc/app`