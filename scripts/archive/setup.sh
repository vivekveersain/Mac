sudo apt-get update
sudo apt-get upgrade

sudo locale-gen en_GB.UTF-8
sudo dpkg-reconfigure locales
sudo update-locale LANG=en_GB.UTF-8 LC_CTYPE=en_GB.UTF-8 LC_ALL=en_GB.UTF-8

mkdir -p /home/vabarya/.virtualenvs
python3 -m venv /home/vabarya/.virtualenvs/master

pip install lxml pandas requests

mkdir /tmp/vitals/
touch /tmp/vitals/data.txt