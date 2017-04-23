BGP = {
    'local_as': 1,
    'router_id': '172.16.2.52',
    'neighbors': [
        {
            'address': '172.16.2.51',
            'remote_as': 1,
            'enable_ipv4': True,
            'enable_ipv6': True,
            'enable_vpnv4': True,
            'enable_vpnv6': True
        },
    ],
    'routes': [
        # Example of IPv4 prefix
        {
            'prefix': '10.20.1.0/24',
            'next_hop': '172.16.1.174'
        },
        {
            'prefix': '172.16.1.0/24'
        },
        {
            'prefix': '172.16.2.0/24'    
        }
     ]
}

SSH = {
    'ssh_port': 4990,
    'ssh_host': 'localhost',
    # 'ssh_host_key': '/etc/ssh_host_rsa_key',
    # 'ssh_username': 'ryu',
    # 'ssh_password': 'ryu',
}

