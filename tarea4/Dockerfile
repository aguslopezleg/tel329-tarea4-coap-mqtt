FROM eclipse-temurin:21-jdk-jammy
ENV DEBIAN_FRONTEND=noninteractive
ENV GRADLE_USER_HOME=/work/.cache/gradle
RUN apt-get update && apt-get install -y --no-install-recommends build-essential git unzip libreadline-dev python3 python3-pip mosquitto mosquitto-clients tcpdump tshark iproute2 net-tools nodejs npm && pip3 install aiocoap==0.4.17 && rm -rf /var/lib/apt/lists/*
WORKDIR /work
