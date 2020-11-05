#!/usr/bin/env python3

from ncclient import manager
from ncclient.xml_ import new_ele, sub_ele

# make a connection object
def connect(host, port, user, password):
    """
    Connect to a redis server.

    Args:
        host: (str): write your description
        port: (int): write your description
        user: (todo): write your description
        password: (str): write your description
    """
    connection = manager.connect(host=host, port=port, username=user,
            password=password, timeout=10, device_params={'name':'junos'},
            hostkey_verify=False)
    return connection

# execute show commands 
def show_cmds(conn, cmd):
    """
    Execute a command.

    Args:
        conn: (todo): write your description
        cmd: (str): write your description
    """
    result = conn.command(cmd, format='text')
    return result

# push out configuration
def config_cmds(conn, config):
    """
    Return configuration ::

    Args:
        conn: (todo): write your description
        config: (dict): write your description
    """
    conn.lock()
    conn.load_configuration(config=config)
    commit_config = conn.commit()
    return commit_config.tostring


if __name__ == '__main__':
    conn = connect('192.168.24.252', '830', 'netconf', 'juniper!')
    result = show_cmds(conn, 'show version')
    print('show version: ' + str(result))
    new_config = new_ele('system')
    sub_ele(new_config, 'host-name').text = 'foo'
    sub_ele(new_config, 'domain-name').text = 'bar'
    result = config_cmds(conn, new_config)
    print('change id: ' + str(result))
    conn.close_session()


