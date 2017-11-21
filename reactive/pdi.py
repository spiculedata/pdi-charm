
from charms.reactive import when, when_not, set_state, remove_state
from charms.reactive.helpers import data_changed
from charms.layer import snap
from charmhelpers.core import hookenv
from charmhelpers.core.hookenv import config, status_set
from subprocess import check_output
import string
import random

@when_not('pentaho-data-integration.installed')
def install_pentaho_data_integration():
    channel = config ('channel')
    status_set('maintenance', 'Installing pentaho-data-integration snap ')
    snap.install('pentaho-data-integration-spicule', channel=channel, devmode=True)
    set_state('pentaho-data-integration.installed')


#@when('pentaho-data-integration.installed')
#@when_not('pentaho-data-integration.configured')
#def configure_pentaho-data-integration():



#@when('pentaho-data-integration.configured')

#def start_pentaho-data-integration():

