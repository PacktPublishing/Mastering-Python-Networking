from flask import Flask
app = Flask(__name__)

@app.route('/routers/<hostname>')
def router(hostname):
    return 'You are at %s' % hostname

@app.route('/routers/<hostname>/interface/<int:interface_number>')
def interface(hostname, interface_number):
    return 'You are at %s interface %d' % (hostname, interface_number)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


