sudo apt-get update
sudo apt-get upgrade

sudo apt-get install bc
sudo apt autoremove

sudo locale-gen en_GB.UTF-8
sudo dpkg-reconfigure locales
sudo update-locale LANG=en_GB.UTF-8 LC_CTYPE=en_GB.UTF-8 LC_ALL=en_GB.UTF-8

mkdir -p /home/vabarya/.virtualenvs
python3 -m venv /home/vabarya/.virtualenvs/master

pip install lxml pandas requests

mkdir /tmp/vitals/
touch /tmp/vitals/data.txt

mkdir -p ./data/ip/


sudo ln -s /home/vabarya/scripts/service/network_monitor.service /etc/systemd/system/network_monitor.service
#sudo ln -s /home/vabarya/scripts/service/qbittorrent-nox.service /etc/systemd/system/qbittorrent-nox.service
sudo ln -s /home/vabarya/scripts/service/vital_monitor.service /etc/systemd/system/vital_monitor.service

sudo systemctl daemon-reload

sudo systemctl enable network_monitor.service
sudo systemctl enable vital_monitor.service

sudo systemctl start network_monitor.service
sudo systemctl start vital_monitor.service

sudo timedatectl set-timezone Asia/Kolkata

sudo chown -R vabarya:vabarya /var/cache/minidlna
sudo chown -R vabarya:vabarya /run/minidlna/