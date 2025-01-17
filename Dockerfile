FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ARG FACEFUSION_VERSION=2.5.1
ENV GRADIO_SERVER_NAME=0.0.0.0
WORKDIR /facefusion
COPY . .
RUN apt-get update
RUN apt-get install python3.10 -y
RUN apt-get install python-is-python3 -y
RUN apt-get install pip -y
RUN apt-get install git -y
RUN apt-get install curl -y
RUN apt-get install ffmpeg -y

RUN python install.py --onnxruntime default --skip-venv
