
from charms.reactive import when, when_not, set_state, remove_state
from charms.reactive.helpers import data_changed
from charms.layer import snap
from charmhelpers.core import hookenv
from charmhelpers.core.hookenv import config, status_set
from subprocess import check_output
import string
import random
import os

@when_not('pentaho-data-integration.installed')
def install_pentaho_data_integration():
    channel = config ('channel')
    status_set('maintenance', 'Installing pentaho-data-integration snap ')
    snap.install('pentaho-data-integration-spicule', channel=channel, devmode=True)
    set_state('pentaho-data-integration.installed')
    status_set('active', 'Pentaho Data Integration running')

@when('mysql.available')
def setup(mysql):
    status_set('active', 'Pentaho Data Integration running. Connections:'+mysql.host())
    str = create_connection(mysql.user(), mysql.password(), mysql.database(), mysql.host(), mysql.host(), mysql.port())
    write_a_file("/home/ubuntu/.kettle/", "shared.xml", str)

def create_connection(user, password, database, server, name, port, ):
    str ="""<?xml version="1.0" encoding="UTF-8"?>
<sharedobjects>
  <connection>
    <name>{}</name>
    <server>{}</server>
    <type>MYSQL</type>
    <access>Native</access>
    <database>{}</database>
    <port>{}</port>
    <username>{}</username>
    <password>{}</password>
    <servername/>
    <data_tablespace/>
    <index_tablespace/>
    <attributes>
      <attribute><code>FORCE_IDENTIFIERS_TO_LOWERCASE</code><attribute>N</attribute></attribute>
      <attribute><code>FORCE_IDENTIFIERS_TO_UPPERCASE</code><attribute>N</attribute></attribute>
      <attribute><code>IS_CLUSTERED</code><attribute>N</attribute></attribute>
      <attribute><code>PORT_NUMBER</code><attribute>3306</attribute></attribute>
      <attribute><code>PRESERVE_RESERVED_WORD_CASE</code><attribute>Y</attribute></attribute>
      <attribute><code>QUOTE_ALL_FIELDS</code><attribute>N</attribute></attribute>
      <attribute><code>STREAM_RESULTS</code><attribute>Y</attribute></attribute>
      <attribute><code>SUPPORTS_BOOLEAN_DATA_TYPE</code><attribute>Y</attribute></attribute>
      <attribute><code>SUPPORTS_TIMESTAMP_DATA_TYPE</code><attribute>Y</attribute></attribute>
      <attribute><code>USE_POOLING</code><attribute>N</attribute></attribute>
    </attributes>
  </connection>

</sharedobjects>
""".format(name, server, database, port, user, password)
    return str

def write_a_file(path, file, text):
    
    if not os.path.exists(path):
        os.makedirs(path)
    
    file = open(path+file,"w")
    file.write(text)
    file.close()







@when('pentaho-data-integration.installed')
def restart(java):
    set_state("pdi.restarting")
    status_set('maintenance', 'Configuration has changed, restarting Carte.')
    stop()
    start()
    remove_state("pdi.restarting")
    remove_state('java.updated')
    remove_state('pdi.restart_scheduled')


@when('leadership.is_leader')
def config_leader():
    leader_set(hostname=hookenv.unit_private_ip())
    leader_set(public_ip=hookenv.unit_public_ip())
    leader_set(username='cluster')
    leader_set(password=hookenv.config('carte_password'))
    leader_set(port=hookenv.config('carte_port'))
    render_master_config()


@when_not('leadership.is_leader')
def update_slave_config():
    render_slave_config()


@when('leadership.changed')
def update_master_config():
    log("leadership has changed, scheduling restart")
    status_set('maintenance', 'Leadership changed, restart scheduled.')
    set_state("pdi.restart_scheduled")


def render_slave_config():
    render('carte-config/slave.xml.j2', '/home/etl/carte-config.xml', {
        'carteslaveport': leader_get('port'),
        'carteslavehostname': hookenv.unit_private_ip(),
        'cartemasterhostname': leader_get('hostname'),
        'carteslavepassword': leader_get('password'),
        'cartemasterpassword': leader_get('password'),
        'cartemasterport': leader_get('port')
    })


def render_master_config():
    render('carte-config/master.xml.j2', '/home/etl/carte-config.xml', {
        'carteport': leader_get('port'),
        'cartehostname': hookenv.unit_private_ip()
    })


def start():
    currentenv = dict(os.environ)
    port = hookenv.config('carte_port')
    javaopts = hookenv.config('java_opts')

    if javaopts:
        currentenv['JAVA_OPTS'] = javaopts

    try:
        check_call(['pgrep', '-f', 'org.pentaho.di.www.Carte'])
    except CalledProcessError:
        check_call(['su', 'etl', '-c',
                    '/opt/data-integration/carte.sh '
                    '/home/etl/carte-config.xml &'],
                   env=currentenv, cwd="/opt/data-integration")

    hookenv.open_port(port)
    status_set('active',
               'Carte is ready! Master is:' + leader_get('public_ip'))


def stop():
    call(['pkill', '-f', 'org.pentaho.di.www.Carte'])


def remove():
    rmtree('/opt/data-integration')


def change_carte_password(pword):
    log("altering carte password to: " + pword)
    generate_encypted_password(pword)
    encrpword = process.splitlines()[-1]
    log("encrypted password is: " + encrpword.decode('utf-8'))
    with open("/opt/data-integration/pwd/kettle.pwd", "w") as text_file:
        text_file.write("cluster: " + encrpword.decode('utf-8'))

def generate_encypted_password(password):
    log("altering carte password to: " + pword)
    process = check_output(['su', 'etl', '-c',
                            '/opt/data-integration/encr.sh -carte ' + pword])

#@when('pentaho-data-integration.installed')
#@when_not('pentaho-data-integration.configured')
#def configure_pentaho-data-integration():



#@when('pentaho-data-integration.configured')

#def start_pentaho-data-integration():

