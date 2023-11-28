#!/bin/bash
set -eo pipefail
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# If $VEILID_SERVER is set, use that, otherwise find a valid Veilid server by looking in the usual places
if [ -z "${VEILID_SERVER}" ]; then
    for VEILID_SERVER_CANDIDATE in ${SCRIPTDIR}/../target/debug/veilid-server; do
        echo -n "Trying Veilid server at ${VEILID_SERVER_CANDIDATE}..."
        if [ -f "${VEILID_SERVER_CANDIDATE}" ]; then
            echo " found!"
            VEILID_SERVER="${VEILID_SERVER_CANDIDATE}"
            break
        else
            echo " not found."
        fi
    done
fi

# If $VEILID_SERVER is still not set, or if it doesn't actually exist, bail
if [[ -z "${VEILID_SERVER}" || ! -f "${VEILID_SERVER}" ]]; then
    echo "No valid in-tree Veilid server was found. Go to the top level directory, run 'cargo build', then change back to this directory and run this script again."
    exit 1
fi

# Produce schema from veilid-server
for SCHEMA in "Request" "RecvMessage"; do
    echo -n "Updating ${SCHEMA}..." && ${VEILID_SERVER} --emit-schema ${SCHEMA} > $SCRIPTDIR/veilid/schema/${SCHEMA}.json && echo " done." || echo " error!"
done
