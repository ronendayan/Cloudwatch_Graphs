import json
import boto3
import os
import sys
import datetime
import urllib
import plotly
from plotly.graph_objs import *
import ghost


def create_graph(region, server_id):

    def get_data_from_cloudwatch(region, server_id):
        cloudwatch = boto3.client(
            'cloudwatch',
            region_name=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName=metric,
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': server_id
                },
            ],
            StartTime=datetime.datetime.utcnow() - datetime.timedelta(hours=5),
            EndTime=datetime.datetime.utcnow(),
            Period=60,
            Statistics=[
                'Average',
            ],
            Unit=unit
        )

        timestamp = []
        data = []

        for i in response['Datapoints']:
            timestamp.append(i['Timestamp'])
            data.append(i['Average'])

        dictionary = dict(zip(timestamp, data))
        timestamp = []
        data = []

        for key in sorted(dictionary.iterkeys()):
            timestamp.append(key)
            data.append(dictionary[key])


        return data, timestamp

    data, timestamp = get_data_from_cloudwatch(region, server_id)

    plotly.offline.plot({
        "data": [Scatter(x=timestamp, y=data), ],
        "layout": Layout(title=server + ' - ' + metric, xaxis=XAxis(title='Date and Time'), yaxis=YAxis(title=metric)),
    }, filename=full_file_name)

    html_link = cfg["urls"]["graph_url"] + file_name

    return html_link


def list_ec2(region, job):
    ec2_client = boto3.client(
            'ec2',
            region_name=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': [
                    'running',
                ],
                'Name': 'tag:Env',
                'Values': [
                    'Prod',
                ]
            },
        ],
    )

    def get_server_info():
        for i in response['Reservations']:
            for x in i['Instances'][0]['Tags']:
                dict1 = x
                lst = []
                for v in dict1.itervalues():
                    lst.append(v)
                    if 'Name' in lst:
                        lst.remove('Name')
                        if lst[0] == server:
                            return i

    def server_list():
        for i in response['Reservations']:
            for x in i['Instances'][0]['Tags']:
                dict1 = x
                lst = []
                for v in dict1.itervalues():
                    lst.append(v)
                    if 'Name' in lst:
                        lst.remove('Name')
                        list_servers.append(lst[0])

    if job == 'list':
        server_list()
        return

    info = get_server_info()
    if info:
        server_id = info['Instances'][0]['InstanceId']
        return server_id


def find_server():
    for region in region_name:
        server_id = list_ec2(region, job)
        if server_id is not None:
            return server_id, region


def create_image(web_link):
    g = ghost.Ghost()
    with g.start() as session:
        page, extra_resources = session.open(web_link)
        if page.http_status == 200 and \
                        'The Universal Operating System' in page.content:
            pass
        session.capture_to(full_image_file_name)

    image_link = cfg["urls"]["image_url"] + image_file_name

    return image_link


def log_request(html_link_value, image_link_value):
    log_file = cfg["disk_path"]["log_file_path"]
    entry = {
        "timestamp": today,
        "user_id": username,
        "server": server,
        "metric": metric,
        "html_link": urllib.quote(html_link_value),
        "image_link": urllib.quote(image_link_value),
        "level": 'INFO'
    }
    with open(log_file, 'a') as outfile:
        json.dump(entry, outfile, indent=4, sort_keys=True)


def main():
    if job == 'list':
        global list_servers
        list_servers = []
        for region in region_name:
            list_ec2(region, job)
        print '```' + '\n'.join(sorted(list_servers)) + '```'
        exit(0)
    try:
        server_id, region = find_server()
    except TypeError:
        print """Couldn't find server name"""
        exit(1)
    html_link = create_graph(region, server_id)
    image_link = create_image(html_link)
    log_request(html_link, image_link)

    print html_link
    print image_link


base_dir = os.path.dirname(os.path.realpath(__file__))

with open(base_dir + '/config.json') as json_config_file:
    cfg = json.load(json_config_file)
with open(base_dir + '/cloudwatch_metrics.json') as cloudwatch_metrics_file:
    cw_cfg = json.load(cloudwatch_metrics_file)

aws_access_key_id = cfg["aws_credentials"]["aws_access_key_id"]
aws_secret_access_key = cfg["aws_credentials"]["aws_secret_access_key"]

region_name = ['us-east-1', 'us-west-2', 'eu-west-1', 'eu-central-1', 'ap-southeast-2']

if len(sys.argv) == 2:
    job = 'list'
elif len(sys.argv) < 4 or len(sys.argv) > 4:
    raise ValueError("Arguments")
    exit(1)
elif len(sys.argv) == 4:
    username = sys.argv[1]
    metricType = sys.argv[2]
    server = sys.argv[3]
    try:
        metric = cw_cfg["cloudwatch"][metricType]
    except KeyError:
        list_metrics = "```\n"
        for metric_key, metric_value in sorted(cw_cfg["cloudwatch"].iteritems()):
            list_metrics = "{0}{1}\t\t- {2}\n".format(list_metrics, metric_key, metric_value)
        list_metrics += "```"
        print "I don't know what kind of metric is `" + metricType + "`\nPlease use one of the following options:\n" + list_metrics
        exit(1)
    unit = cw_cfg["cloudwatch_unit"][metricType]
    job = 'getGraph'

    timestamp_format = "%Y-%m-%d_%H-%M-%S"
    today_timestamp = datetime.datetime.now().strftime(timestamp_format)
    html_file_path = cfg["disk_path"]["html_file_path"]
    image_file_path = cfg["disk_path"]["image_file_path"]
    file_name = server + '_' + today_timestamp + '.html'
    full_file_name = html_file_path + server + '_' + today_timestamp + '.html'
    image_file_name = server + '_' + today_timestamp + '.jpeg'
    full_image_file_name = image_file_path + server + '_' + today_timestamp + '.jpeg'

# Building dates
date_format = "%Y-%m-%d %H:%M:%S"
today_datetime = datetime.datetime.today()
today = today_datetime.strftime(date_format)

if __name__ == '__main__':
    main()
