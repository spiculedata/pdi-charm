charm build .
charm_ref="$(charm push ${JUJU_REPOSITORY}/builds/pentaho-data-integration ~spiculecharms/pentaho-data-integration | grep -m 1 url | awk '{ print $2 }')"

charm release $charm_ref --channel edge
