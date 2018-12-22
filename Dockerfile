FROM ubuntu:18.04
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git
RUN git clone https://github.com/SwiftLaTeX/docstore.git /app && \
    pip3 install -r /app/requirements.txt

WORKDIR /app
CMD ["python3", "WSGI.py"]