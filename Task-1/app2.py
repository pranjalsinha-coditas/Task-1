# Online Python compiler (interpreter) to run Python online.
# Write Python 3 code in this online editor and run it.
from flask import Flask
import boto3
import logging
import time

app = Flask(__name__)
client = boto3.client('logs', region_name='us-east-1')
log_group_name = 'HelloWorldAPI'
log_stream_name = 'repeatEndpoint'

# Create CloudWatch Logs log group and stream
def create_log_group_stream():
    try:
        client.create_log_group(logGroupName=log_group_name)
    except client.exceptions.ResourceAlreadyExistsException:
        pass

    try:
        client.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)
    except client.exceptions.ResourceAlreadyExistsException:
        pass

create_log_group_stream()

def log_to_cloudwatch(message):
    response = client.describe_log_streams(logGroupName=log_group_name, logStreamNamePrefix=log_stream_name)
    log_stream = response['logStreams'][0]
    sequence_token = log_stream.get('uploadSequenceToken')
    log_event = {
        'logGroupName': log_group_name,
        'logStreamName': log_stream_name,
        'logEvents': [{'timestamp': int(time.time() * 1000), 'message': message}]
    }
    if sequence_token:
        log_event['sequenceToken'] = sequence_token
    client.put_log_events(**log_event)

@app.route('/hello')
def hello_world():
    return 'Hello World', 200

@app.route('/repeat')
def repeat_hello_world():
    messages = []
    for i in range(1, 101):
        message = 'Hello World'
        messages.append(message)
        if i % 5 == 0:
            log_to_cloudwatch(f'Iteration {i}: {message}')
    return '\n'.join(messages), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

#/usr/local/bin/python3 /Users/coditas/Desktop/Task-1/app2.py