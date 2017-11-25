
from charms.reactive import when, when_not, set_state, remove_state
from charms.reactive.helpers import data_changed
from charms.layer import snap
from charmhelpers.core import hookenv
from charmhelpers.core.hookenv import config, status_set
from subprocess import check_output
import string
import random
import os
import xml.etree.ElementTree as ET

kettlepropsdir = '/home/ubuntu/.kettle/'
sharedfile = 'shared.xml'
@when_not('pentaho-data-integration.installed')
def install_pentaho_data_integration():
    channel = config ('channel')
    status_set('maintenance', 'Installing pentaho-data-integration snap ')
    snap.install('pentaho-data-integration-spicule', channel=channel, devmode=True)
    set_state('pentaho-data-integration.installed')
    status_set('active', 'Pentaho Data Integration running')

@when('mysql.available')
def setup(mysql):
    id = ''
      for relation_id in hookenv.relation_ids('mysql'):
        id = relation_id

    status_set('active', 'Pentaho Data Integration running. Connections:'+id)
    add_data_source(mysql.user(), mysql.password(), mysql.database(), mysql.host(), mysql.host(), mysql.port())

def add_data_source(user, password, database, server, name, port):
    password = generate_encrypted_password(password)
    #Check if the file exists
    #If it doesnt exist create file with wrapping tags
    if not os.path.isfile(kettlepropsdir):
        write_a_file(kettlepropsdir, sharedfile, create_shared_objects_template())

    #read the file
    st=read_file(kettlepropsdir+sharedfile)
    #convert to xml
    tree = ET.ElementTree(ET.fromstring(st))
    #inject new connection
    conn = create_connection(user, password, database, server, name, port)
    conntree = ET.ElementTree(ET.fromstring(conn)).getroot()
    root_node = tree.getroot()
    child = root_node.append(conntree)
    #write the file
    xmlstr = ET.tostring(root_node, encoding='utf8', method='xml')
    write_a_file(kettlepropsdir,sharedfile,str(xmlstr, 'utf-8'))


def remove_data_source(name):
    #Read string to xml
    st=read_file(kettlepropsdir+sharedfile)
    #Find the connection node by name
    tree = ET.ElementTree(ET.fromstring(st)).getroot()

    #Remove node and all subelements
    for child in tree.findall("connection"):
       for connname in child.findall("name"):
         if name == connname.text:
          tree.remove(child) 
    #Write back to file 
    xmlstr = ET.tostring(tree, encoding='utf8', method='xml')
    write_a_file(kettlepropsdir,sharedfile,str(xmlstr, 'utf-8'))


def create_shared_objects_template():
    
    return """<?xml version="1.0" encoding="UTF-8"?>
<sharedobjects>

</sharedobjects>"""
    

def create_connection(user, password, database, server, name, port):
    st ="""
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
""".format(name, server, database, port, user, password)
    return st

def read_file(filename):
    #read a file
    with open(filename) as f:
        return ''.join(line.rstrip() for line in f)
    
def write_a_file(path, file, text):
    
    if not os.path.exists(path):
        os.makedirs(path)
    
    file = open(path+file,"w")
    file.write(text)
    file.close()







# @when('pentaho-data-integration.installed')
# def restart(java):
#     set_state("pdi.restarting")
#     status_set('maintenance', 'Configuration has changed, restarting Carte.')
#     stop()
#     start()
#     remove_state("pdi.restarting")
#     remove_state('java.updated')

#     remove_state('pdi.restart_scheduled')


# @when('leadership.is_leader')
# def config_leader():
#     leader_set(hostname=hookenv.unit_private_ip())
#     leader_set(public_ip=hookenv.unit_public_ip())
#     leader_set(username='cluster')
#     leader_set(password=hookenv.config('carte_password'))
#     leader_set(port=hookenv.config('carte_port'))
#     render_master_config()


# @when_not('leadership.is_leader')
# def update_slave_config():
#     render_slave_config()


# @when('leadership.changed')
# def update_master_config():
#     log("leadership has changed, scheduling restart")
#     status_set('maintenance', 'Leadership changed, restart scheduled.')
#     set_state("pdi.restart_scheduled")


# def render_slave_config():
#     render('carte-config/slave.xml.j2', '/home/etl/carte-config.xml', {
#         'carteslaveport': leader_get('port'),
#         'carteslavehostname': hookenv.unit_private_ip(),
#         'cartemasterhostname': leader_get('hostname'),
#         'carteslavepassword': leader_get('password'),
#         'cartemasterpassword': leader_get('password'),
#         'cartemasterport': leader_get('port')
#     })


# def render_master_config():
#     render('carte-config/master.xml.j2', '/home/etl/carte-config.xml', {
#         'carteport': leader_get('port'),
#         'cartehostname': hookenv.unit_private_ip()
#     })


# def start():
#     currentenv = dict(os.environ)
#     port = hookenv.config('carte_port')
#     javaopts = hookenv.config('java_opts')

#     if javaopts:
#         currentenv['JAVA_OPTS'] = javaopts

#     try:
#         check_call(['pgrep', '-f', 'org.pentaho.di.www.Carte'])
#     except CalledProcessError:
#         check_call(['su', 'etl', '-c',
#                     '/opt/data-integration/carte.sh '
#                     '/home/etl/carte-config.xml &'],
#                    env=currentenv, cwd="/opt/data-integration")

#     hookenv.open_port(port)
#     status_set('active',
#                'Carte is ready! Master is:' + leader_get('public_ip'))


# def stop():
#     call(['pkill', '-f', 'org.pentaho.di.www.Carte'])


# def remove():
#     rmtree('/opt/data-integration')


# def change_carte_password(pword):
#     log("altering carte password to: " + pword)
#     generate_encrypted_password(pword)
#     encrpword = process.splitlines()[-1]
#     log("encrypted password is: " + encrpword.decode('utf-8'))
#     with open("/opt/data-integration/pwd/kettle.pwd", "w") as text_file:
#         text_file.write("cluster: " + encrpword.decode('utf-8'))

def generate_encrypted_password(password):
    #run check output
    
    output = check_output(['pentaho-data-integration-spicule.encrypt', '-kettle', password])
    
    arr = output.splitlines()

    for a in arr:
        
        a = a.decode('utf-8')
        if a.startswith("Encrypted"): 
            return a
#@when('pentaho-data-integration.installed')
#@when_not('pentaho-data-integration.configured')
#def configure_pentaho-data-integration():



#@when('pentaho-data-integration.configured')

#def start_pentaho-data-integration():

