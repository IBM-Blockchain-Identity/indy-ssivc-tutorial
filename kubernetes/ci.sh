buildImages() {

  echo Logging into Bluemix...
  bx api api.ng.bluemix.net
  bx login --apikey ${BLUEMIX_APIKEY}

  OUT=$(bx cr)
  if [ $? -ne 0 ]; then
   echo "We need the container registry plugin to do this stuff. Grabbing it..."
   bx plugin install -f container-registry
  else
    echo "Container registry plugin is installed."
  fi

  echo Configuring Docker for the IBM Container Registry...
  bx cr login

  export NAMESPACE=indyworld

  echo ---------------------------------
  echo VON-NETWORK IMAGE
  echo ---------------------------------

  bx cr build -t registry.ng.bluemix.net/$NAMESPACE/von-base ./von-network

  echo ---------------------------------
  echo THE ORG BOOK IMAGES
  echo ---------------------------------

  echo ** SOLR **

  echo Start with the solr base image...

  docker build \
    https://github.com/bcgov/openshift-solr.git \
    -t $NAMESPACE/solr-base

  echo Building solr deployable image...
  s2i build ./TheOrgBook/tob-solr/cores $NAMESPACE/solr-base registry.ng.bluemix.net/$NAMESPACE/solr

  echo Pushing solr image...
  docker push registry.ng.bluemix.net/$NAMESPACE/solr

  echo ** SCHEMA SPY **

  echo Building schema-spy image...
  docker build -t registry.ng.bluemix.net/$NAMESPACE/schema-spy \
    https://github.com/bcgov/SchemaSpy.git

  echo Pushing the schema-spy image...
  docker push registry.ng.bluemix.net/$NAMESPACE/schema-spy

  echo ** TOB WEB **

  echo First the nginx-runtime image...
  docker build -t $NAMESPACE/nginx-runtime \
    -f TheOrgBook/tob-web/openshift/templates/nginx-runtime/Dockerfile \
    TheOrgBook/tob-web/openshift/templates/nginx-runtime/

  echo Then the angular app image...
  s2i build -e "NG_BASE_HREF=/" \
    -e "TOB_THEME=indy-world" \
    TheOrgBook/tob-web centos/nodejs-6-centos7:6 \
    $NAMESPACE/angular-app

  echo And finally the angular-on-nginx image...
  docker build --build-arg imagenamespace=$NAMESPACE/ \
    -t registry.ng.bluemix.net/$NAMESPACE/angular-on-nginx \
    -f TheOrgBook/tob-web/openshift/templates/angular-on-nginx/Dockerfile \
    TheOrgBook/tob-web/openshift/templates/angular-on-nginx

  echo And pushing that out...
  docker push registry.ng.bluemix.net/$NAMESPACE/angular-on-nginx

  echo ** TOB API **

  echo Building the libindy image...

  docker build -t $NAMESPACE/libindy \
    -f TheOrgBook/tob-api/openshift/templates/libindy/Dockerfile \
    TheOrgBook/tob-api/openshift/templates/libindy/

  echo Building the python-libindy image...
  docker build -t $NAMESPACE/python-libindy \
    --build-arg imagenamespace=$NAMESPACE/ \
    -f TheOrgBook/tob-api/openshift/templates/python-libindy/Dockerfile \
    TheOrgBook/tob-api/openshift/templates/python-libindy/

  echo Building the tob-api deployable image...
  s2i build TheOrgBook/tob-api \
    $NAMESPACE/python-libindy \
    registry.ng.bluemix.net/$NAMESPACE/django

  echo Pushing out the tob-api image...

  docker push registry.ng.bluemix.net/$NAMESPACE/django


  echo ---------------------------------
  echo PERMITIFY IMAGES
  echo ---------------------------------

  echo Building libindy...

  docker build -t $NAMESPACE/libindy \
    -f permitify/docker/libindy/Dockerfile \
    permitify/docker/libindy/

  echo Building libindy-python...

  docker build -t $NAMESPACE/python-libindy \
    --build-arg imagenamespace=$NAMESPACE/ \
    -f permitify/docker/python-libindy/Dockerfile \
    permitify/docker/python-libindy/

  echo Building permitify-dmv image...

  docker build -t registry.ng.bluemix.net/$NAMESPACE/permitify \
    --build-arg imagenamespace=$NAMESPACE/ \
    -f permitify/docker/permitify/Dockerfile \
    permitify/

  echo And pushing it out...
  docker push registry.ng.bluemix.net/$NAMESPACE/permitify
}

deployLatest() {
  echo Logging into Bluemix ...

  bx api api.ng.bluemix.net
  bx login --apikey ${BLUEMIX_APIKEY}

  echo Setting up Kubernetes client to use indy world cluster...
  $(bx cs cluster-config new-indy-world --export)

  echo Using bankkyc namespace...
  kubectl config set-context $(kubectl config current-context) --namespace=bankkyc

  echo The currently running pods are...
  kubectl get pods

  cd kubernetes

  echo Taking out all existing deployments...
  kubectl delete deployments --all

  echo Deploying von-network...
  kubectl apply -f von-network.yml
  sleep 30

  echo Deploying theorgbook...
  kubectl apply -f theorgbook.yml
  sleep 45

  echo Deploying permitify...
  kubectl apply -f permitify.yml
}

certs() {
  echo "Not yet implemented."
  exit 1
}


usage() {
  cat <<-EOF

  Usage: $0 {build|deploy|certs}

  build   Logs into Bluemix using BLUEMIX_APIKEY environment variable
          and builds all the images in this project. Where possible, it
          uses the bx cr command instead of docker build, so as to limit
          the amount of disk space used (bx cr images get built on ICS servers)

          When finished, everything in the namespace for this project should
          be the latest images built based on master.

  deploy  Connects to the new-indy-world cluster in IBM Container Service,
          switches to the namespace for this project, rips down the current
          deployment, and proceeds to redeploy with latest images.

  certs   For renewing the public https certificates. Not implemented yet.

EOF
exit 1

case "$1" in
  build)
    buildImages
    ;;
  deploy)
    deployLatest
    ;;
  certs)
    certs
    ;;
  *)
    usage
esac
