from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_networkers():
    """
    Return the number of networkers locations

    Args:
    """
    return 'Hello Networkers!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


