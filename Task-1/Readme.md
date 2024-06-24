# Building a Scalable "Hello World" API with Jenkins, CloudWatch Logs, and High Availability

This document outlines the process of creating a scalable "Hello World" API with two functionalities:

- `/hello`: Returns "Hello World" once.
- `/repeat`: Returns "Hello World" 100 times, interspersed with CloudWatch logs every 5 iterations.

The implementation leverages Jenkins for continuous integration and deployment (CI/CD), containerization with Docker, and utilizes AWS services for infrastructure and logging.

## 1. Development and Local Testing

### Develop the API
Choose your preferred language (e.g., Python with Flask). Implement logic for the two endpoints:

- `/hello`: Returns a simple string "Hello World".
- `/repeat`: Iterates 100 times, printing "Hello World" to standard output (stdout) for each iteration. Within the loop, insert CloudWatch log messages every 5th iteration using the AWS SDK for your chosen language.

Example implementation in Python with Flask:

```python
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
```

## 2. Dockerfile Creation

Create a Dockerfile that defines the base image (e.g., python:3.9), copies your code, exposes the port the API runs on (e.g., 5000), and includes:

1. Installation of required dependencies (e.g., AWS SDK for CloudWatch logging).
2. Configuration for logging to CloudWatch logs within the container using environment variables for log group name and log stream name.

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install flask boto3

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "app.py"]
```

### Requirements File

Create a file named requirements.txt to list your dependencies.

``` text 
flask
boto3

```

## 3. Jenkins Pipeline Setup

### Set Up Jenkins Server

Follow the Jenkins installation guide to install Jenkins on your server.

### Create a Jenkins Pipeline

Open Jenkins in your browser and create a new pipeline job. Configure the pipeline to use a script that performs the following steps:

1. Clone the repository containing your API code.
2. Build the Docker image using the Dockerfile.
3. Push the built Docker image to an Amazon ECR repository.
4. Deploy the Docker image to EC2 instances.

## 4. Infrastructure with High Availability

### Amazon VPC

Create a Virtual Private Cloud (VPC) using the AWS CLI to provide network isolation for your resources. Set up subnets and security groups to control access.

### EC2 Instances

Launch EC2 instances within the VPC using a user data script that pulls the container image from ECR and runs the containerized API using Docker.

## 5. Network Load Balancer (NLB)

Create an NLB using the AWS CLI to distribute traffic across your EC2 instances running the containerized API. This ensures scalability and fault tolerance.

## 6. CloudWatch Logs Configuration

### Create a CloudWatch Log Group

Use the AWS CLI to create a CloudWatch log group for your API logs. Configure your API code to send logs to this log group.

## 7. Route 53 Integration (Optional)

### Create a Hosted Zone and Record

Use the AWS CLI to create a hosted zone in Route 53 for your desired domain name. Create a record pointing to the NLB's DNS name, allowing users to access your API through a public domain.

## 8. Security Groups

Configure security groups to allow inbound traffic on the API port (e.g., 5000) for the NLB and outbound traffic for the EC2 instances to access CloudWatch Logs.

### Overall Workflow

1. Developers commit code changes to the version control system.
2. Jenkins detects the changes and triggers the pipeline.
3. The pipeline builds the Docker image, pushes it to ECR, and launches EC2  instances with the user data script to run the containerized API.
4. The NLB distributes traffic across the EC2 instances.
5. Users access the API through the Route 53 domain name (if configured) or the NLB's DNS name.
6. The API logic returns "Hello World" for /hello and iterates 100 times with "Hello World" messages and CloudWatch logs for /repeat, all logged to CloudWatch for monitoring and troubleshooting.

This approach provides a scalable and maintainable solution for your "Hello World" API with CI/CD, containerization, high availability, and logging capabilities.

Assignment: 

Implement webapi-task-2 for a number of users with the same concept. App users should keep increasing. This should be evident with a good scaling group of instances.
