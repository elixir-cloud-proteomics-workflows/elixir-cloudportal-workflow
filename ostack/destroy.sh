#!/usr/bin/env bash
set -e

echo "\(^O^)/ Setting up convenience OS_ENV"
# Git cloned application folder
export APP="${PORTAL_APP_REPO_FOLDER}"
echo "export APP=${APP}"
# Deployment folder
export DEPLOYMENTSFOLDER="${PORTAL_DEPLOYMENTS_ROOT}/${PORTAL_DEPLOYMENT_REFERENCE}/"
export DPL="${PORTAL_DEPLOYMENTS_ROOT}/${PORTAL_DEPLOYMENT_REFERENCE}/"
echo "export DPL=${DPL}"

export NETWORK=$OS_NETWORK
export CLUSTER_NAME=$PORTAL_DEPLOYMENT_REFERENCE

echo "\(^O^)/ Will destroy the following"


# Destroys a virtual machine instance by ansible

ansible-playbook --flush-cache $APP/ansible-remove-cluster/playbook.yml
