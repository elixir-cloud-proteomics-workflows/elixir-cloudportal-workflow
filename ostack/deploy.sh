#!/usr/bin/env bash
set -euoEx pipefail

echo "＼(＾O＾)／ Setting up convenience OS_ENV"

export APP="${PORTAL_APP_REPO_FOLDER}"
export DEPLOYMENTSFOLDER="${PORTAL_DEPLOYMENTS_ROOT}/${PORTAL_DEPLOYMENT_REFERENCE}/"
export DPL="${PORTAL_DEPLOYMENTS_ROOT}/${PORTAL_DEPLOYMENT_REFERENCE}/"

export NETWORK=$OS_NETWORK  # Elixir-Proteomics_private

export PRIVATE_KEYPATH="${DPL}${PORTAL_DEPLOYMENT_REFERENCE}"
chmod 600 "${PRIVATE_KEYPATH}"
export KEYPATH="${DPL}${PORTAL_DEPLOYMENT_REFERENCE}.pub"
export BASTION_KEY=$(echo -e $BASTION_KEY_VALUE)
echo "${BASTION_KEY}" >> "${DEPLOYMENTSFOLDER}.letmein"
chmod 600 "${DEPLOYMENTSFOLDER}.letmein"
export BASTION_KEY="${DEPLOYMENTSFOLDER}.letmein"

echo "KEYPATH ${KEYPATH}"
echo "PRIVATE_KEYPATH ${PRIVATE_KEYPATH}"

#$TF_VAR_BASTION_KEY  # /home/user/.ssh/id_rsa

export BASTION_IP=$TF_VAR_BASTION_IP  # 193.62.55.220
export BASTION_USER=$TF_VAR_BASTION_USER  # sshuser
export IMAGE=$TF_VAR_IMAGE  # slurm-glusterfs-nextflow-ubuntu-16.04
export FLAVOR=$TF_VAR_FLAVOR  # s1.small
export REDIS_HOST=$TF_VAR_REDIS_HOST  #192.168.0.16
export REDIS_PORT=$TF_VAR_REDIS_PORT  # 6379
export REDIS_DB=$TF_VAR_REDIS_DB  # 1

export CLUSTER_NAME=$PORTAL_DEPLOYMENT_REFERENCE  #cluster-deployment-1

echo "＼(＾O＾)／ Applying workflow playbooks"
printf '%(%Y%m%d-%H:%M:%S)T\n'
cd $DPL
echo "cwd=$PWD"

echo "PXD=$PXD"

# Deploy cluster
ansible-playbook --flush-cache $APP/ansible-slurm-cluster/playbook.yml -e "{'host_key_checking':false }"

# Provide input
ansible-playbook --flush-cache -b --become-user=root -i $DEPLOYMENTSFOLDER/auto.ini \
    $APP/ansible-digest-portalinput/prideclient-playbook.yml -e "{'host_key_checking':false }" \
    -e "{'PXD':$PXD}"

# Extract the result url
URL=$(cat $DEPLOYMENTSFOLDER/result_get.res)
OUTPUT_URL=$PORTAL_BASE_URL/deployment/$PORTAL_DEPLOYMENT_REFERENCE/outputs
echo "OUTPUTS_URL ${OUTPUT_URL}"

curl --insecure -i -X PUT -H "Content-Type: application/json" \
 -H "Deployment-Secret: ${PORTAL_CALLBACK_SECRET}" \
 -d "[{\"outputName\":\"URL\",\"generatedValue\":\"${URL}\"}]" "${OUTPUT_URL}"

ansible-playbook --flush-cache -b --become-user=root -i $DEPLOYMENTSFOLDER/auto.ini \
    $APP/ansible-nf-fileinfo/nextflow-playbook.yml -e "{'host_key_checking':false }" \
    -e "{'PXD':$PXD}"

echo "＼(＾O＾)／ All done. Tearing down deployment"
printf '%(%Y%m%d-%H:%M:%S)T\n'


# killme