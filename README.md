# Overview

This charm provides Pentaho Data Intergration (PDI, which is also know as 
Kettle) PDI is the component od Pentaho that is responsible for the Extract, 
Transform and Load (ETL) processes. ETL tools are most frequently used in 
data warehouse environments, PDI can also be used for other purposes such as
Migrating data between applications or databases.

# Usage

Deploying the charm is as simple as:

    juju deploy ~spiculecharms/pentaho-data-integration

To interact with PDI you can run one of the following:
    
    pentaho-data-integration-spicule.pan
    pentaho-data-integration-spicule.spoon
    pentaho-data-integration-spicule.kitchen

## Relations

The charm has been built with relations to Mysql and telegraf so that metrics
can be easily extracted to Grafana. Grafana is the open platform for analytics 
and dashboards

## Known Limitations and Issues

Currently doesn't scale.
Limited database connections.

# Configuration

Configuration options coming soon

# Contact Information

Tom Barber - tom@spicule.co.uk
Stephen Downie - stephen@spicule.co.uk
info@spicule.co.uk

