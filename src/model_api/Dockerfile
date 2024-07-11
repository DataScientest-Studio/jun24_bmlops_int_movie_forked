FROM python:3.12-slim

RUN apt-get update && apt-get install python3-pip -y

#set up a Working directory in the container
WORKDIR /app

#copy in the needed requirements and files
COPY model_api.py .
COPY requirements.txt .

#installing all necessary requirements
RUN pip install -r requirements.txt

EXPOSE 8000

#run the application
CMD ["python", "model_api.py"]