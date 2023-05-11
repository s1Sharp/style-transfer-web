add-apt-repository ppa:deadsnakes/ppa
apt-get update
apt list | grep python3.10
apt-get install python3.10
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 2
update-alternatives --config python3
python3 -V