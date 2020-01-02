FROM python:3.6
LABEL maintainer="Rodrigo Machado <rodrigo.machado@hotmail.com>"
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "app.py"]