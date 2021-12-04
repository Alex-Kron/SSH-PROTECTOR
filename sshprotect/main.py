import paramiko as pm
import getpass
import click as cl


@cl.command()
@cl.option('-i', '--ip', prompt='Host IP:', type=str, help='Enter the IP of the connected server')
@cl.option('-u', '--username', prompt='Username:', type=str, help='Enter the username on the server')
@cl.option('-p', '--port', default=22, nargs=1, type=int, prompt='SSH port:', help='Enter the SSH port')
@cl.option('--auto/--no-auto', default=False, help='Automatic configuration of full server protection')
def connect(ip, username, port, auto):
    """Utility for server protection according to SSH"""

    client = pm.SSHClient()
    client.set_missing_host_key_policy(pm.AutoAddPolicy())
    password = getpass.getpass(prompt='Enter user password: ')

    try:
        client.connect(hostname=ip, username=username, password=password, port=port)

        if auto:
            pass
        else:
            chooser(client)

    except pm.AuthenticationException:
        cl.echo('Authentication error. Invalid connection parameters.')
    except pm.SSHException:
        cl.echo('The SSH connection was interrupted.')
    except cl.ClickException:
        print('CLI Error')
    finally:
        cli_exit(client)


def status(client):
    cl.secho('\n___STATUS___', bg='blue', bold=True)
    port = get_ssh_port(client)
    if port == 'Port 22\n':
        cl.secho('[problem]', bg='red', fg='black', nl=False)
    else:
        cl.secho('[protected]', bg='green', fg='black', nl=False)
    cl.echo('\tSSH port:\t', nl=False)
    cl.echo(port)


def chooser(client):
    function_list = [('Scanning defence', scanning),
                     ('Bruteforce defence', bruteforce),
                     ('Make file system with LUKS', make_luks),
                     ('User settings', user_set),
                     ('SSH settings', ssh_set)]
    while True:
        cl.clear()
        status(client)
        cl.secho('\n___SETTINGS___', bg='blue', bold=True)
        for i in range(len(function_list)):
            cl.secho('[' + str(i) + ']', bold=True, bg='blue', nl=False)
            cl.echo(':\t' + function_list[i][0])
        ex = str(len(function_list))
        cl.secho('[' + ex + ']', bold=True, bg='blue', nl=False)
        cl.echo(':\tExit')
        num = cl.prompt('Enter the action number', type=int)
        while num < 0 or num > int(ex):
            cl.secho('Error: Invalid action number', fg='red')
            num = cl.prompt('Enter the action number', type=int)
        if num == int(ex):
            break
        else:
            function_list[num][1](client)


def change_ssh_port(client):
    cl.clear()
    cl.secho('___CHANGE_SSH_PORT___', bg='blue', bold=True)
    cl.echo('Current SSH port:\t', nl=False)
    cl.echo(get_ssh_port(client))
    port = cl.prompt('Enter the new SSH port', type=int)
    while port < 1024 or port > 65535:
        cl.secho('Warning: The selected port is insecure', fg='yellow')
        port = cl.prompt('Please re-select the port', type=int)
    if is_port_busy(client, port):
        cl.secho('Error: Port is busy with one of the services', fg='red')
    else:
        if cl.confirm('Are you sure you want to change the SSH port?'):
            stdin, stdout, stderr = client.exec_command('grep -e \'^#\{0,1\}Port\s[0-9]\{1,5\}\' /etc/ssh/sshd_config '
                                '&& sudo sed -i \'s/^#\{0,1\}Port\s[0-9]\{1,5\}/Port ' + str(port) + '/g\' /etc/ssh/sshd_config '
                                '|| sudo sh -c \"echo \'Port ' + str(port) + '\' >> /etc/ssh/sshd_config\"', get_pty=True)
            err = stderr.readlines()
            cl.echo(err)
            client.exec_command('sudo service ssh restart')
            cl.echo('Current SSH port:\t' + get_ssh_port(client))
    return_to_chooser(client)


def get_ssh_port(client):
    stdin, stdout, stderr = client.exec_command('grep -e \'^Port\s[0-9]\{1,5\}$\' /etc/ssh/sshd_config')
    line = stdout.readline()
    if not line:
        return 'Port 22\n'
    else:
        return line


def is_port_busy(client, port):
    stdin, stdout, stderr = client.exec_command('grep -e \'\s' + str(port) + '/\' /etc/services')
    lines = stdout.readlines()
    if lines:
        return True
    else:
        return False


def scanning(client):
    pass

def bruteforce(client):
    pass


def make_luks(client):
    pass


def user_set(client):
    pass


def cli_exit(client):
    cl.echo('Closing SSH connection...')
    client.close()


def ssh_set(client):
    change_ssh_port(client)


def return_to_chooser(client):
    cl.pause('\nPress any key to return to the SETTINGS')


if __name__ == '__main__':
    connect()
