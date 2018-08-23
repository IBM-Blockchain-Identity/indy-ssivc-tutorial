buildImages() {

  echo Logging into Bluemix...
  ibmcloud api api.$API_REGION.bluemix.net
  ibmcloud login --apikey ${BLUEMIX_API_KEY}

  OUT=$(ibmcloud cr)
  if [ $? -ne 0 ]; then
   echo "We need the container registry plugin to do this stuff. Grabbing it..."
   ibmcloud plugin install -f container-registry
  else
    echo "Container registry plugin is installed."
  fi

  echo Configuring Docker for the IBM Container Registry...
  ibmcloud cr login

  echo ---------------------------------
  echo VON-NETWORK IMAGE
  echo ---------------------------------

  ${DOCKER_BUILDER} -t $REGISTRY/von-base ./von-network
  docker push $REGISTRY/von-base

  echo ---------------------------------
  echo THE ORG BOOK IMAGES
  echo ---------------------------------

  echo ** SOLR **

  echo Start with the solr base image...

  docker build \
    https://github.com/bcgov/openshift-solr.git \
    -t $REG_NAMESPACE/solr-base

  echo Building solr deployable image...
  s2i build ./TheOrgBook/tob-solr/cores $REG_NAMESPACE/solr-base $REGISTRY/solr

  echo Pushing solr image...
  docker push $REGISTRY/solr

  echo ** SCHEMA SPY **

  echo Building schema-spy image...
  docker build -t $REGISTRY/schema-spy \
    https://github.com/bcgov/SchemaSpy.git

  echo Pushing the schema-spy image...
  docker push $REGISTRY/schema-spy

  echo ** TOB WEB **

  echo First the nginx-runtime image...
  docker build -t $REG_NAMESPACE/nginx-runtime \
    -f TheOrgBook/tob-web/openshift/templates/nginx-runtime/Dockerfile \
    TheOrgBook/tob-web/openshift/templates/nginx-runtime/

  echo Then the angular app image...
  s2i build -e "NG_BASE_HREF=/" \
    -e "TOB_THEME=indy-world" \
    TheOrgBook/tob-web centos/nodejs-6-centos7:6 \
    $REG_NAMESPACE/angular-app

  echo And finally the angular-on-nginx image...
  docker build --build-arg imagenamespace=$REG_NAMESPACE/ \
    -t $REGISTRY/angular-on-nginx \
    -f TheOrgBook/tob-web/openshift/templates/angular-on-nginx/Dockerfile \
    TheOrgBook/tob-web/openshift/templates/angular-on-nginx

  echo And pushing that out...
  docker push $REGISTRY/angular-on-nginx

  echo ** TOB API **

  echo Building the libindy image...

  docker build -t $REG_NAMESPACE/libindy \
    -f TheOrgBook/tob-api/openshift/templates/libindy/Dockerfile \
    TheOrgBook/tob-api/openshift/templates/libindy/

  echo Building the python-libindy image...
  docker build -t $REG_NAMESPACE/python-libindy \
    --build-arg imagenamespace=$REG_NAMESPACE/ \
    -f TheOrgBook/tob-api/openshift/templates/python-libindy/Dockerfile \
    TheOrgBook/tob-api/openshift/templates/python-libindy/

  echo Building the tob-api deployable image...
  s2i build TheOrgBook/tob-api \
    $REG_NAMESPACE/python-libindy \
    $REGISTRY/django

  echo Pushing out the tob-api image...

  docker push $REGISTRY/django


  echo ---------------------------------
  echo PERMITIFY IMAGES
  echo ---------------------------------

  echo Building libindy...

  docker build -t $REG_NAMESPACE/libindy \
    -f permitify/docker/libindy/Dockerfile \
    permitify/docker/libindy/

  echo Building libindy-python...

  docker build -t $REG_NAMESPACE/python-libindy \
    --build-arg imagenamespace=$REG_NAMESPACE/ \
    -f permitify/docker/python-libindy/Dockerfile \
    permitify/docker/python-libindy/

  echo Building permitify-dmv image...

  docker build -t $REGISTRY/permitify \
    --build-arg imagenamespace=$REG_NAMESPACE/ \
    -f permitify/docker/permitify/Dockerfile \
    permitify/

  echo And pushing it out...
  docker push $REGISTRY/permitify
}

deployLatest() {
  echo Logging into Bluemix ...

  ibmcloud api api.$API_REGION.bluemix.net
  ibmcloud login --apikey ${BLUEMIX_API_KEY}
  ibmcloud cs region-set ${IKS_REGION}

  echo Setting up Kubernetes client to use $IKS_CLUSTER_NAME cluster for indy world demo...
  $(ibmcloud cs cluster-config ${IKS_CLUSTER_NAME} --export)

  echo Using $KUBE_NAMESPACE namespace...
  kubectl config set-context $(kubectl config current-context) --namespace=$KUBE_NAMESPACE

  echo The currently running pods are...
  kubectl get pods

  cd kubernetes

  echo Taking out all existing deployments...
  kubectl delete deployments --all

  echo Deploying von-network...
  # Substitute image registry
  sed -e s/\$REGISTRY/$REGISTRY/g \
    von-network.yml | \
    kubectl --namespace $KUBE_NAMESPACE apply -f -
  sleep 120

  echo Deploying theorgbook...
  sed -e s/\$REGISTRY/$REGISTRY/g \
    theorgbook.yml | \
    kubectl --namespace $KUBE_NAMESPACE apply -f -
  sleep 120

  echo Deploying permitify...
  sed -e s/\$REGISTRY/$REGISTRY/g \
    -e s/\$INGRESS_SUBDOMAIN/${INGRESS_SUBDOMAIN}/g \
    permitify.yml | \
    kubectl --namespace $KUBE_NAMESPACE apply -f -

  echo Deploying ingress
  sed -e s/\$INGRESS_SUBDOMAIN/${INGRESS_SUBDOMAIN}/g \
    -e s/\$TLS_SECRET_NAME/${TLS_SECRET_NAME}/g \
    iks-ingress.yml | \
    kubectl -n bankkyc apply -f -
}

deployIngress() {

  echo Deploying ingress
  sed -e s/\$INGRESS_SUBDOMAIN/${INGRESS_SUBDOMAIN}/g \
    iks-ingress.yml | \
    kubectl -n bankkyc apply -f -

}

certs() {
  echo "Not yet implemented."
  exit 1
}


usage() {
  cat <<-EOF

  Usage: $0 {build|deploy|certs}

  build   Logs into Bluemix using BLUEMIX_API_KEY environment variable
          and builds all the images in this project. Where possible, it
          uses the ibmcloud cr command instead of docker build, so as to
          limit the amount of disk space used (ibmcloud cr images get built
          on IKS servers)

          When finished, everything in the namespace for this project should
          be the latest images built based on master.

  deploy  Connects to the new-indy-world cluster in IBM Container Service,
          switches to the namespace for this project, rips down the current
          deployment, and proceeds to redeploy with latest images.

  certs   For renewing the public https certificates. Not implemented yet.

EOF
exit 1
}

# if Using IBM Container Registry service
#export REG_REGION=au-syd
#export REG_NAMESPACE=iwinoto_ibm
#export REGISTRY=registry.$REG_REGION.bluemix.net/$REG_NAMESPACE
#export DOCKER_BUILDER="ibmcloud cr build"

# If using Docker hub as image registry
export REG_NAMESPACE=iwinoto
export REGISTRY=$REG_NAMESPACE
export DOCKER_BUILDER="docker build"

# Region for IBM Cloud api endpoint
export API_REGION=au-syd

# Parameters for IBM Cloud Kubernetes Service (IKS)
export IKS_REGION=us-east
export IKS_CLUSTER_NAME=wcp-tech-workshop-mz
export KUBE_NAMESPACE=bankkyc
export INGRESS_SUBDOMAIN=wcp-tech-workshop-mz.us-east.containers.appdomain.cloud
export TLS_SECRET_NAME=wcp-tech-workshop-mz

case "$1" in
  build)
    buildImages
    ;;
  deploy)
    deployLatest
    ;;
  ingress)
    deployIngress
    ;;
  certs)
    certs
    ;;
  *)
    usage
esac
