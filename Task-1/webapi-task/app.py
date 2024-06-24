from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'hello world'
    # <script>
    #     console.log("Hello, World!");
    # </script>
    

@app.route('/hello_ten_times')
def hello_ten_times():
    return 'Hello, World\n' 

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
