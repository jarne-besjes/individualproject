FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt update -y
RUN apt upgrade -y
RUN apt install clang -y

COPY . .

CMD [ "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000" ]

EXPOSE 8000