FROM python:3.10-slim
#RUN groupadd --gid 1001 sshmnt \
#  && useradd --uid 1001 --gid sshmnt --shell /bin/bash --create-home sshmnt
#ARG UID=1001
#ARG GID=1001
#ENV UID=${UID}
#ENV GID=${GID}
#RUN usermod -u $UID sshmnt \
#  && groupmod -g $GID sshmnt
ENV TOKEN=TOKEN
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY config.py /app/
COPY bot.py /app/
COPY startup.sh /app/
VOLUME /app/data
RUN chmod +x /app/startup.sh && apt update && apt upgrade && apt install -y ffmpeg
CMD ["/bin/bash","-c","./startup.sh"]
