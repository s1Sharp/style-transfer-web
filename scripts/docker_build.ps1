git submodule foreach git pull origin master
docker build -f ./Dockerfile -t s1sharp/style_web_app .
docker run --env-file config/.env -it -v ${PWD}:/home s1sharp/style_web_app
