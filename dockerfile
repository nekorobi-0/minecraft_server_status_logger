FROM python:3.11-slim
WORKDIR /usr/src/python
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
CMD python main.py