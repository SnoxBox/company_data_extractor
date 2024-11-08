FROM python:3.10.0

WORKDIR /company_data_extactor

# Copy the requirements.txt file into the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN python3 -m pip install -r requirements.txt

# Copy the entire project into the container
COPY . .

# Make port 8800 available to the world outside this container
EXPOSE 5500

# Set environment variables for Flask
ENV FLASK_APP=app.py

# run the application
CMD [ "flask", "run", "-h", "0.0.0.0", "-p", "5500"]