# use a python 3.8 base image
FROM python:3.8

# set the working directory to /techtrends
WORKDIR /app

# copy all the files from the techtrends directory to the container working directory
COPY /techtrends /app

# Install packages defined in the requirements.txt file
RUN pip install -r requirements.txt
# Ensure that the database is initialized with the pre-defined posts in the init_db.py file
RUN python init_db.py

# expose the port 3111
EXPOSE 3111

# execute the techtrends application
CMD ["python", "app.py"]
