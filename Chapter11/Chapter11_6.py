BGP = {
    'local_as': 65000,
    'router_id': '172.16.1.174',
    'neighbors': [
        {
            'address': '172.16.1.175',
            'remote_as': 1,
            'enable_ipv4': True,
            'enable_ipv6': True,
            'enable_vpnv4': True,
            'enable_vpnv6': True
        },
    ]
}

SSH = {
    'ssh_port': 4990,
    'ssh_host': 'localhost',
    # 'ssh_host_key': '/etc/ssh_host_rsa_key',
    # 'ssh_username': 'ryu',
    # 'ssh_password': 'ryu',
}

