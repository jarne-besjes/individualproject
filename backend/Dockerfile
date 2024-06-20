FROM python:3

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt update && apt upgrade -y
RUN apt install clang llvm graphviz -y
RUN apt install opt -y

COPY . .

CMD [ "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload" ]

EXPOSE 8000