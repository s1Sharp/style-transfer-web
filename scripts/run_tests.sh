rm -f /etc/apt/sources.list.d/*.list

# Install some basic utilities.
apt-get update && apt-get install -y \
    curl \
    git \
    bzip2 \
    wget

export PYTHONPATH="$PYTHONPATH:/home:home/src"
export PROJECT_ROOT="/home"

pip install -r requirements.txt

pytest -s -v -x tests/