# Start from a Python base image with CUDA support
FROM nvidia/cuda:12.3.1-base-ubuntu22.04
CMD nvidia-smi

# Install Python and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-dev && \
    ln -s /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy the application source code
COPY . /app

# Expose the port the app runs on
EXPOSE 8000

# Set the environment variable to indicate Gunicorn usage
ENV USE_GUNICORN=true

# Set the entry point to your CLI
ENTRYPOINT ["python", "-m", "gonk_diffusers_api.cli"]

# Set default arguments to the entry point
CMD ["-H", "0.0.0.0", "-p", "8000"]
