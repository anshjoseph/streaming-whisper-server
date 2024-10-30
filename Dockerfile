FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

RUN apt-get update && apt-get install libgomp1 git -y
RUN apt-get -y update && apt-get -y upgrade && apt-get install -y --no-install-recommends ffmpeg
RUN apt-get -y install python3.11
RUN apt-get -y install python3-pip
RUN apt-get -y install build-essential
RUN apt-get -y install portaudio19-dev
RUN pip install ctranslate2==4.1.0 ffmpeg_python==0.2.0 kaldialign==0.9.1 numpy==1.26.4 onnxruntime==1.17.3 openai_whisper==20231117 PyAudio==0.2.14  scipy==1.13.0  soundfile==0.12.1 tokenizers==0.15  torch==2.1.2 torchaudio==2.1.2 websocket_client==1.7.0 websockets==12.0 faster-whisper==1.0.1

COPY readme.md .
RUN git clone https://github.com/anshjoseph/streaming-whisper-server
WORKDIR streaming-whisper-server
RUN python3 -m pip install --upgrade pip
RUN pip install setuptools
RUN pip install -e .
RUN pip install faster-whisper==1.0.1
RUN pip install transformers

RUN ct2-transformers-converter --model openai/whisper-tiny --copy_files preprocessor_config.json --output_dir ./Server/ASR/whisper_tiny --quantization float16
WORKDIR Server
EXPOSE 9000
CMD ["python3", "Server.py", "-p", "9000"]