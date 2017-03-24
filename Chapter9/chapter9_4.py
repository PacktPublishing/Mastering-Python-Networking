from flask import Flask, url_for

app = Flask(__name__)

@app.route('/<hostname>/list_interfaces')
def device(hostname):
    if hostname in routers:
        return 'Listing interfaces for %s' % hostname
    else: 
        return 'Invalid hostname'

routers = ['r1', 'r2', 'r3']
for router in routers: 
    with app.test_request_context():
        print(url_for('device', hostname=router))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


