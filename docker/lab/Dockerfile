FROM python:3.11-alpine

WORKDIR /lab
RUN apk add --no-cache curl iproute2 busybox-extras
COPY service.py /lab/service.py
EXPOSE 8080
CMD ["python", "/lab/service.py"]
