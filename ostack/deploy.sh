#!/usr/bin/env bash
set -euoEx pipefail

echo "＼(＾O＾)／ Setting up convenience OS_ENV"

export APP="${PORTAL_APP_REPO_FOLDER}"
export DEPLOYMENTSFOLDER="${PORTAL_DEPLOYMENTS_ROOT}/${PORTAL_DEPLOYMENT_REFERENCE}/"
export KEY_PATH=$PUBLIC_KEY
export PRIV_KEY_PATH=$PRIVATE_KEY

export NETWORK=$OS_NETWORK  # Elixir-Proteomics_private

echo $(echo $BASTION_KEY_VALUE | base64 -d) > "${DEPLOYMENTSFOLDER}/.letmein"
export BASTION_KEY="${DEPLOYMENTSFOLDER}/.letmein"         #$TF_VAR_BASTION_KEY  # /home/user/.ssh/id_rsa

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
ansible-playbook --flush-cache -b --become-user=root \
    $APP/ansible-slurm-cluster/playbook.yml -e "{'host_key_checking':false }"

# Provide input
ansible-playbook --flush-cache -b --become-user=root -i $DEPLOYMENTSFOLDER/auto.ini \
    $APP/ansible-digest-portalinput/prideclient-playbook.yml -e "{'host_key_checking':false }" \
    -e "{'PXD':$PXD}"

# Extract the result url
URL=$(cat $DEPLOYMENTSFOLDER/result_get.res)

ansible-playbook --flush-cache -b --become-user=root -i $DEPLOYMENTSFOLDER/auto.ini \
    $APP/ansible-nf-fileinfo/nextflow-playbook.yml -e "{'host_key_checking':false }" \
    -e "{'PXD':$PXD}"

echo "＼(＾O＾)／ All done. Tearing down deployment"
printf '%(%Y%m%d-%H:%M:%S)T\n'


# killme
