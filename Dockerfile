
FROM python:3.11

RUN apt-get update && apt-get install -y \
    vim curl wget git zip unzip bash iputils-ping net-tools \
    libatlas3-base awscli && \
    rm -rf /var/lib/apt/lists/*

# TA-Libビルド用依存パッケージ追加
RUN apt-get update && \
    apt-get install -y build-essential wget && \
    wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzvf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    wget -O config.guess https://git.savannah.gnu.org/cgit/config.git/plain/config.guess && \
    wget -O config.sub https://git.savannah.gnu.org/cgit/config.git/plain/config.sub && \
    chmod +x config.guess config.sub && \
    ./configure --prefix=/usr && make && make install && \
    cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

WORKDIR /app
ENV PYTHONPATH=/app/src

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt


COPY . .

CMD ["streamlit", "run", "app.py"]
