from flask import Flask
app = Flask(__name__)

@app.route('/routers/<hostname>')
def router(hostname):
    """
    Return a router name.

    Args:
        hostname: (str): write your description
    """
    return 'You are at %s' % hostname

@app.route('/routers/<hostname>/interface/<int:interface_number>')
def interface(hostname, interface_number):
    """
    Return the hostname from the given hostname.

    Args:
        hostname: (str): write your description
        interface_number: (int): write your description
    """
    return 'You are at %s interface %d' % (hostname, interface_number)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


