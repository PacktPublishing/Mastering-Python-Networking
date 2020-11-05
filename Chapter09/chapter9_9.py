# This example referenced Miguel Grinberg's code on Github:
# https://github.com/miguelgrinberg/oreilly-flask-apis-video
#

from flask import Flask, url_for, jsonify, request,\
    make_response, copy_current_request_context, g
from flask.ext.sqlalchemy import SQLAlchemy
from chapter9_pexpect_1 import show_version
import uuid
import functools
from threading import Thread
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.httpauth import HTTPBasicAuth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///network.db'
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

background_tasks = {}
app.config['AUTO_DELETE_BG_TASKS'] = True


class ValidationError(ValueError):
    pass

# The two password function came with Flask Werkzeug
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        """
        Set the password of the password.

        Args:
            self: (todo): write your description
            password: (str): write your description
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Verifies whether a given password matches.

        Args:
            self: (todo): write your description
            password: (str): write your description
        """
        return check_password_hash(self.password_hash, password)


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


def background(f):
    """Decorator that runs the wrapped function as a background task. It is
    assumed that this function creates a new resource, and takes a long time
    to do so. The response has status code 202 Accepted and includes a Location
    header with the URL of a task resource. Sending a GET request to the task
    will continue to return 202 for as long as the task is running. When the task
    has finished, a status code 303 See Other will be returned, along with a
    Location header that points to the newly created resource. The client then
    needs to send a DELETE request to the task resource to remove it from the
    system."""
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        """
        A decorator toilio. client. background_tasks

        Args:
        """
        # The background task needs to be decorated with Flask's
        # copy_current_request_context to have access to context globals.
        @copy_current_request_context
        def task():
            """
            Create a task : class.

            Args:
            """
            global background_tasks
            try:
                # invoke the wrapped function and record the returned
                # response in the background_tasks dictionary
                background_tasks[id] = make_response(f(*args, **kwargs))
            except:
                # the wrapped function raised an exception, return a 500
                # response
                background_tasks[id] = make_response(internal_server_error())

        # store the background task under a randomly generated identifier
        # and start it
        global background_tasks
        id = uuid.uuid4().hex
        background_tasks[id] = Thread(target=task)
        background_tasks[id].start()

        # return a 202 Accepted response with the location of the task status
        # resource
        return jsonify({}), 202, {'Location': url_for('get_task_status', id=id)}
    return wrapped

# g is the context request object from Flask
@auth.verify_password
def verify_password(username, password):
    """
    Verify a given username

    Args:
        username: (str): write your description
        password: (str): write your description
    """
    g.user = User.query.filter_by(username=username).first()
    if g.user is None:
        return False
    return g.user.verify_password(password)

@app.before_request
@auth.login_required
def before_request():
    """
    Decor function to request.

    Args:
    """
    pass

# from HTTPAuath extension
@auth.error_handler
def unathorized():
    """
    Unath an unath

    Args:
    """
    response = jsonify({'status': 401, 'error': 'unahtorized', 
                        'message': 'please authenticate'})
    response.status_code = 401
    return response


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


@app.route('/devices/<int:id>/version', methods=['GET'])
@background
def get_device_version(id):
    """
    Get device version.

    Args:
        id: (int): write your description
    """
    device = Device.query.get_or_404(id)
    hostname = device.hostname
    ip = device.mgmt_ip
    prompt = hostname+"#"
    result = show_version(hostname, prompt, ip, 'cisco', 'cisco')
    return jsonify({"version": str(result)})

@app.route('/devices/<device_role>/version', methods=['GET'])
@background
def get_role_version(device_role):
    """
    Get role version.

    Args:
        device_role: (todo): write your description
    """
    device_id_list = [device.id for device in Device.query.all() if device.role == device_role]
    result = {}
    for id in device_id_list:
        device = Device.query.get_or_404(id)
        hostname = device.hostname
        ip = device.mgmt_ip
        prompt = hostname + "#"
        device_result = show_version(hostname, prompt, ip, 'cisco', 'cisco')
        result[hostname] = str(device_result)
    return jsonify(result)

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


@app.route('/status/<id>', methods=['GET'])
def get_task_status(id):
    """Query the status of an asynchronous task."""
    # obtain the task and validate it
    global background_tasks
    rv = background_tasks.get(id)
    if rv is None:
        return not_found(None)

    # if the task object is a Thread object that means that the task is still
    # running. In this case return the 202 status message again.
    if isinstance(rv, Thread):
        return jsonify({}), 202, {'Location': url_for('get_task_status', id=id)}

    # If the task object is not a Thread then it is assumed to be the response
    # of the finished task, so that is the response that is returned.
    # If the application is configured to auto-delete task status resources once
    # the task is done then the deletion happens now, if not the client is
    # expected to send a delete request.
    if app.config['AUTO_DELETE_BG_TASKS']:
        del background_tasks[id]
    return rv



if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', debug=True)





