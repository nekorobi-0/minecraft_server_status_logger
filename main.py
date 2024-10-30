import requests
import json
import schedule
import time
import influxdb_client,os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

if False:
    URL = os.environ["INFLUXDB_ADDRESS"]
    TOKEN = os.environ["INFLUXDB_TOKEN"]
    ORG = os.environ["INFLUXDB_ORG"]
    BUCKET = os.environ["INFLUXDB_BUCKET"]
else:
    URL = "http://192.168.0.101:8086"
    TOKEN = "gVnYoNuSMkya3NUWMTjYmB0XE3sWwlotwSQP5TVItr7RxMOVUvws69xlxwiB8diZBbh1cbHFc5XqrCMjWrpLRQ=="
    ORG = "minecraft_status"
    BUCKET = "minecraft"
with open('servers.json') as f:
    SERVERS: dict = json.load(f)
write_client = influxdb_client.InfluxDBClient(url=URL, token=TOKEN, org=ORG)
write_api = write_client.write_api(write_options=SYNCHRONOUS)
def get_info(servers):
    for server in [servers[key] for key in servers]:
        #https://api.mcsrvstat.us/
        url = f"https://api.mcsrvstat.us/3/{server}"
        response = requests.get(url)
        data = json.loads(response.text)
        yield data

def write_to_influxdb(data, server_name):
    point = Point("player_count").tag("name", server_name).field("player_count", data["players"]["online"]).time(time.time_ns(), WritePrecision.NS)
    write_api.write(bucket=BUCKET, org=ORG, record=point)
def is_server_online(data):
    return data["online"]
def task():
    datas = get_info(SERVERS)
    for data, server in zip(datas, SERVERS.keys()):
        time.sleep(1)
        print(data)
        if not is_server_online(data):
            continue
        write_to_influxdb(data, server)
task()
schedule.every(120).seconds.do(task)
while True:
    schedule.run_pending()
    time.sleep(1)