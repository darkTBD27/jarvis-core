FROM nvidia/cuda:12.3.2-devel-ubuntu22.04

WORKDIR /app

RUN apt update && apt install -y \
python3 \
python3-pip \
git \
build-essential \
cmake \
curl \
ninja-build \
&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python3 -m pip install --upgrade pip setuptools wheel

ENV CMAKE_ARGS="-DGGML_CUDA=on"
ENV FORCE_CMAKE=1
ENV LLAMA_CPP_FORCE_CMAKE=1

RUN ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/libcuda.so.1

RUN python3 -m pip install --no-cache-dir llama-cpp-python==0.2.90

RUN rm /usr/local/cuda/lib64/libcuda.so.1

RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY app /app
COPY models /app/models

CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000","--no-access-log","--log-level","warning"]
