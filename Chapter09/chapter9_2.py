from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    """
    Returns the index of the index.

    Args:
    """
    return 'You are at index()'

@app.route('/routers/')
def routers():
    """
    Return a list of all the router methods.

    Args:
    """
    return 'You are at routers()'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


