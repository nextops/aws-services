# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 7687 available to the world outside this container
EXPOSE 7687

COPY src/listServices.py listServices.py

# Set the entrypoint for the Docker container
ENTRYPOINT ["python", "listServices.py"]
