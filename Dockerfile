FROM nexus.opentech.local:8082/aevitas/python_pip:18.0 as builder
WORKDIR /opt
COPY . .
RUN pip install -r requirements.txt

FROM nexus.opentech.local:8082/aevitas/python:3.7.0
COPY --from=builder /usr/lib/python3.7 /usr/lib/python3.7
COPY --from=builder /usr/bin /usr/bin
RUN pacman -Sy libsm libxext libxrender --noconfirm
WORKDIR /opt
COPY . .
ENV PYTHONUNBUFFERED 1
CMD ["paperclip/paperclip.py"]