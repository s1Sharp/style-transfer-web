export PROJECT_ROOT=$PWD
echo $PROJECT_ROOT
# echo "PROJECT_ROOT=$PWD" >> /etc/environment
git submodule update --init --recursive
git pull --recurse-submodules
git submodule update --remote --recursive
chmod a+x -R scripts/ docker/
scripts/decrypt_secret.sh -s config/.env_release.gpg -d config/.env_release -k $ENV_SECRET_PASSPHRASE
python3 -m pip install --upgrade pip
python3 -m pip install -r docker/requirements_py37.txt
