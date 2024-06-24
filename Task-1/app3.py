from flask import Flask
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def hello_world_new():
    for _ in range(100):
        app.logger.info('Hello World')
    return 'HELLO WORLD'

@app.route('/pranjal')
def hello_world():
    for _ in range(100):
        app.logger.info('Hello World from API endpoint')
    return 'HELLO WORLD FROM API ENDPOINT'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=50001)  # Changed the port to 50001