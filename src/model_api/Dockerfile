FROM python:3.12-slim

#set up a Working directory in the container
WORKDIR /app

# set env variable for volumes which will be used
ENV MODEL_PATH "/models"
ENV DATA_PATH "/data"

#copy in the needed requirements and files
COPY model_api.py .
COPY requirements.txt .

#installing all necessary requirements
RUN apt-get update && apt-get install python3-pip -y && pip install -r requirements.txt

EXPOSE 8000

#run the application
CMD ["python", "model_api.py"]