# Use an official lightweight Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Prevent python from writing .pyc files and buffer output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy the dependencies file and install them
# Using --no-cache-dir makes the image smaller
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entrypoint script that will run on container start
COPY entrypoint.sh .
# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

# Copy the rest of the application code into the container
COPY . .

# Expose the port that Gunicorn will run on
EXPOSE 8000

# Define the command that will run when the container starts
ENTRYPOINT ["./entrypoint.sh"]
