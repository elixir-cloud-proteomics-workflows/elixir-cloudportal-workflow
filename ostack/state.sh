#!/usr/bin/env bash
# Get the status of an OpenLava deployment in OpenStack
# For details about expected inputs and outputs, refer to https://github.com/EMBL-EBI-TSI/openlava
# The script assumes that env vars for authentication with OpenStack are present.

cat $PORTAL_DEPLOYMENTS_ROOT'/'$PORTAL_DEPLOYMENT_REFERENCE'/terraform.tfstate'
