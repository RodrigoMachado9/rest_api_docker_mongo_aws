FROM python:3.6
LABEL maintainer="Rodrigo Machado <rodrigo.machado@hotmail.com>"
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python3 -m spacy download en_core_web_sm
#RUN pip3 install ./en_core_web_sm-2.0.0.tar.gz
EXPOSE 8080
CMD ["python", "app.py"]