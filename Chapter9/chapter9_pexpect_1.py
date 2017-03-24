import pexpect


def show_version(device, prompt, ip, username, password):
    device_prompt = prompt
    child = pexpect.spawn('telnet ' + ip)
    child.expect('Username:')
    child.sendline(username)
    child.expect('Password:')
    child.sendline(password)
    child.expect(device_prompt)
    child.sendline('show version | i V')
    child.expect(device_prompt)
    result = child.before
    child.sendline('exit')
    return device, result

if __name__ == '__main__':
    username = 'cisco'
    password = 'cisco'
    print(show_version('iosv-1', 'iosv-1#', '172.16.1.225', username, password))
    print(show_version('iosv-2', 'iosv-2#', '172.16.1.226', username, password))

