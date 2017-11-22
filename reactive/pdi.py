
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



#@when('pentaho-data-integration.installed')
#@when_not('pentaho-data-integration.configured')
#def configure_pentaho-data-integration():



#@when('pentaho-data-integration.configured')

#def start_pentaho-data-integration():

