# This example referenced Miguel Grinberg's code on Github:
# https://github.com/miguelgrinberg/oreilly-flask-apis-video/commit/98855d48f52f4dc0f9728c841bdd0645810d708e
#

from flask import Flask, url_for, jsonify, request
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///network.db'
db = SQLAlchemy(app)

class ValidationError(ValueError):
    pass


class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(64), unique=True)
    loopback = db.Column(db.String(120), unique=True)
    mgmt_ip = db.Column(db.String(120), unique=True)
    role = db.Column(db.String(64))
    vendor = db.Column(db.String(64))
    os = db.Column(db.String(64))

    def get_url(self):
        """
        Returns the url of the resource.

        Args:
            self: (todo): write your description
        """
        return url_for('get_device', id=self.id, _external=True)

    def export_data(self):
        """
        Exports data to json.

        Args:
            self: (todo): write your description
        """
        return {
            'self_url': self.get_url(),
            'hostname': self.hostname,
            'loopback': self.loopback,
            'mgmt_ip': self.mgmt_ip,
            'role': self.role,
            'vendor': self.vendor,
            'os': self.os
        }

    def import_data(self, data):
        """
        Import data

        Args:
            self: (todo): write your description
            data: (array): write your description
        """
        try:
            self.hostname = data['hostname']
            self.loopback = data['loopback']
            self.mgmt_ip = data['mgmt_ip']
            self.role = data['role']
            self.vendor = data['vendor']
            self.os = data['os']
        except KeyError as e:
            raise ValidationError('Invalid device: missing ' + e.args[0])
        return self


@app.route('/devices/', methods=['GET'])
def get_devices():
    """
    Get all devices.

    Args:
    """
    return jsonify({'device': [device.get_url() 
                               for device in Device.query.all()]})

@app.route('/devices/<int:id>', methods=['GET'])
def get_device(id):
    """
    Get device.

    Args:
        id: (int): write your description
    """
    return jsonify(Device.query.get_or_404(id).export_data())

@app.route('/devices/', methods=['POST'])
def new_device():
    """
    Create new device.

    Args:
    """
    device = Device()
    device.import_data(request.json)
    db.session.add(device)
    db.session.commit()
    return jsonify({}), 201, {'Location': device.get_url()}

@app.route('/devices/<int:id>', methods=['PUT'])
def edit_device(id):
    """
    Edit device.

    Args:
        id: (int): write your description
    """
    device = Device.query.get_or_404(id)
    device.import_data(request.json)
    db.session.add(device)
    db.session.commit()
    return jsonify({})


if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', debug=True)





