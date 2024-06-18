FROM python:3.10

# Set the working directory
WORKDIR /usr/src/app

# Add a user to run the application
RUN adduser --disabled-password --gecos '' api_user

# Copy the requirements file into the container at /usr/src/app
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Create a user for the container
USER api_user

# Run the application when the container launches
CMD alembic upgrade head && uvicorn posts_app.api.main:app --host 0.0.0.0 --port 8000

# Continuously check the health of the application
HEALTHCHECK --interval=60s --timeout=30s \
    CMD curl --fail http://localhost:8000/api/status || exit 1
