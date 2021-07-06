#AWS Cloudwatch Graphs
Generate an image and html files out from aws cloudwatch

## Prerequisites
You will need to install:
- [Ghost](http://jeanphix.me/Ghost.py/)
- [Plotly](https://plot.ly/python/)

##Config
- Config regions that the script will check our in [create_graph.py](https://github.com/ronendayan/Cloudwatch_Graphs/create_graph.py) under
```python
region_name = ['us-east-1', 'us-west-2', 'eu-west-1', 'eu-central-1', 'ap-southeast-2']
```
- Metrics can be added in [cloudwatch_metrics.json](https://github.com/ronendayan/Cloudwatch_Graphs/cloudwatch_metrics.json) file under `cloudwatch`
- EC2 Tags:  
The script will search for specific EC2 with Tag: Env:Prod, That can be changed in [create_graph.py](https://github.com/ronendayan/Cloudwatch_Graphs/create_graph.py) under function `list_ec2`  
 ```python
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
```
- Edit [config.json](https://github.com/ronendayan/Cloudwatch_Graphs/config.json) to set:
    - AWS Credentials (`aws_credentials`)  
    Need to provide with key and secret for the AWS connection  
    Note that the user need to have permissions to list and describe EC2 and get metrics statistics from Cloudwatch
    - Disk Path (`disk_path`)  
    The disk path contain 3 paths:  
    1\. `html_file_path` - Directory where the htmls file will be saved  
    2\. `image_file_path` - Directory where the image file will be saved  
    3\. `log_file_path` - Full path for log file  
    - URLs (`urls`) - URLs to present the image and the html file

## Case of use
This script use for slack bot automation but can be use for many others.  
For that case this script can run for 2 different jobs depending on the arguments that follow.  
As I said, The script been writen for slack bot and for that I always ask for `user_name` for logging  
1. Listing the possibles servers:
```bash
python create_graph.py #{username}
```
2. Get graphs:  
where `#{metric}` is part of the [cloudwatch_metrics.json](https://github.com/ronendayan/Cloudwatch_Graphs/cloudwatch_metrics.json) file and `#{server}` from the listing
```bash
python create_graph.py #{username} #{metric} #{server}
```
