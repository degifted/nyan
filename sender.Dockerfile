FROM python:3.11
WORKDIR /
COPY . .
RUN pip3 install -r requirements.txt
RUN bash download_models.sh
ENTRYPOINT /send.sh
#CMD [ "python", "-m", "nyan.send", "--channels-info-path",  "channels.json",        "--client-config-path",        "configs/client_config.json",        "--mongo-config-path",        "configs/mongo_config.json",        "--annotator-config-path",        "configs/annotator_config.json",        "--renderer-config-path",        "configs/renderer_config.json",        "--daemon-config-path",        "configs/daemon_config.json"]
