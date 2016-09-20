import os
import socket

from subprocess import check_call

from charms.reactive import when, when_not, set_state
from charmhelpers.core import hookenv


@when_not('tls-client.installed')
def install_tls_client():
    '''Install'''
    print('install_tls_client')
    set_state('tls-client.installed')


@when('certificates.ca.available')
def store_ca(tls):
    '''Read the certificate authority from the relation object and install it
    on this system.'''
    # Get the CA from the relationship object.
    certificate_authority = tls.get_ca()
    if certificate_authority:
        # Update /etc/ssl/certs and generate ca-certificates.crt
        install_ca(certificate_authority)

        # The final location of the CA should be in /srv/kubernetes directory.
        kubernetes_dir = '/srv/kubernetes'
        if not os.path.isdir(kubernetes_dir):
            os.makedirs(kubernetes_dir)
        destination = os.path.join(kubernetes_dir, 'ca.crt')
        hookenv.log('Writing the CA to {0}'.format(destination))
        with open(destination, 'w') as fp:
            fp.write(certificate_authority)


@when('certificates.available')
def send_data(tls):
    '''Send the data that is required to create a server certificate for this
    server.'''
    # Use the public ip of this unit as the Common Name for the certificate.
    common_name = hookenv.unit_public_ip()
    # Get a list of Subject Alt Names for the certificate.
    sans = []
    sans.append(hookenv.unit_public_ip())
    sans.append(hookenv.unit_private_ip())
    sans.append(socket.gethostname())
    # Create a path safe name by removing path characters from the unit name.
    certificate_name = hookenv.local_unit().replace('/', '_')
    tls.request_server_cert(common_name, sans, certificate_name)


@when('certificates.server.cert.available')
def store_server(tls):
    '''Read the server certificate from the relation object and install it on
    this system.'''
    server_cert, server_key = tls.get_server_cert()
    if server_cert and server_key:
        kubernetes_dir = '/srv/kubernetes'
        if not os.path.isdir(kubernetes_dir):
            os.makedirs(kubernetes_dir)
        cert_file = os.path.join(kubernetes_dir, 'server.cert')
        hookenv.log('Writing the server certificate to {0}'.format(cert_file))
        with open(cert_file, 'w') as stream:
            stream.write(server_cert)
        key_file = os.path.join(kubernetes_dir, 'server.key')
        hookenv.log('Writing the server key to {0}'.format(key_file))
        with open(key_file, 'w') as stream:
            stream.write(server_key)


@when('certificates.client.cert.available')
def store_client(tls):
    '''Read the client certificate from the relation object and install it on
    this system.'''
    client_cert, client_key = tls.get_client_cert()
    if client_cert and client_key:
        kubernetes_dir = '/srv/kubernetes'
        if not os.path.isdir(kubernetes_dir):
            os.makedirs(kubernetes_dir)
        cert_file = os.path.join(kubernetes_dir, 'client.cert')
        hookenv.log('Writing the server certificate to {0}'.format(cert_file))
        with open(cert_file, 'w') as stream:
            stream.write(client_cert)
        key_file = os.path.join(kubernetes_dir, 'client.key')
        hookenv.log('Writing the server key to {0}'.format(key_file))
        with open(key_file, 'w') as stream:
            stream.write(client_key)


def install_ca(certificate_authority):
    '''Install a certificiate authority on the system by calling the
    update-ca-certificates command.'''
    if certificate_authority:
        name = hookenv.service_name()
        ca_file = '/usr/local/share/ca-certificates/{0}.crt'.format(name)
        hookenv.log('Writing CA to {0}'.format(ca_file))
        # Write the contents of certificate authority to the file.
        with open(ca_file, 'w') as fp:
            fp.write(certificate_authority)
        # Update the trusted CAs on this system.
        check_call(['update-ca-certificates'])
        message = 'Generated ca-certificates.crt for {0}'.format(name)
        hookenv.log(message)
