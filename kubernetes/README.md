# Kubernetes Deployment

## Prereqs:

- [Docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-ce)
- [Bluemix Commandline](https://console.bluemix.net/docs/cli/reference/bluemix_cli/get_started.html)
- [docker-compose](https://docs.docker.com/compose/install/)
- [s2i](https://github.com/openshift/source-to-image/releases/tag/v1.1.9a)
- Bluemix Container Service Plugin (`bx plugin install container-service`)
- Bluemix Container Registry Plugin (`bx plugin install container-registry`)

## Image namespace

Images are very similar but have critical detailed differences. They share a lot of similar diskdiffs as well which can make it tricky to know their interrelationship.  For this reason, we recommend creating and using a IBM Cloud Container Registry namespace.  Make one like this:

```
$ bx cr namespace-add bankkyc
```

And use it when you push images (see below).

## Produce Images

- Build the images as you normally would (see instructions elsewhere).
- There are many images you need for this demo to work:
  - `django`
  - `solr`
  - `permitify`
  - `schema-spy`
  - `angular-on-nginx`
  - `von-base`
- There are other images that are produced as a byproduct of the build but
  they do not need to exist in the registry for the deployments to work.
- Configure docker with bx cli so that you can push images:
  ```
  $ bx cr login
  ```
- For each of the above images, tag them to belong in the Bluemix registry,
  and then push (this is just for django; do it for the others too):
  ```
  $ docker tag django registry.ng.bluemix.net/bankkyc/django
  $ docker push registry.ng.bluemix.net/bankkyc/django
  ```

## Kubernetes Namespace

To help keep deployments separate, we recommend creating and then setting the context for a kubernetes namespace.

Create the namespace like so:
```
$ kubectl create namespace bankkyc
```

Then set it as the default namespace like this:
```
$ kubectl config set-context $(kubectl config current-context) --namespace=indyworld
```

## Deployments

Should be able to deploy each of the separate deployments in this folder
using kubectl without issue. The order *does matter*. For each of them just do `kubectl apply -f <deployment file>`.
- von-network.yml
- theorgbook.yml
- permitify.yml

## Ingress Setup
- Clear old/current ingresses:
  ```
  $ kubectl delete ingress --all
  ```
- Apply setup ingress ingress...
  ```
  $ kubectl apply -f ingress-setup.yml
  ```
- Wait a bit for that to go into effect. You can test
  whether it's working by browsing to some of the domains.  If you get
  redirected to https, it's not working. If you get a problem with a backend
  that's fine, because you may not have stood up services. If you get a 404,
  that's not working (unless you typed the domain wrong).
- Get into the ingress setup container/pod:
  ```
  $ kubectl exec -it ingress-setup<push tab>
  ```
- Run the certbot inside the pod:
  ```
  $ certbot certonly
  ```
- Answer the prompts, agree to the terms, do not let them use your email.
- Enter this domain list when they ask:
  ```
  indyworld.vcreds.org indyworld-von-web.vcreds.org indyworld-api.vcreds.org indyworld-schema-spy.vcreds.org indyworld-person.vcreds.org indyworld-faber.vcreds.org indyworld-acme-corp.vcreds.org indyworld-acme-corp-apply.vcreds.org indyworld-thrift.vcreds.org
  ```
- Wait; they will check that you own all these domains and give you a cert.
- The cert is located in/at:
  ```
  $ cd /etc/letsencrypt/live
  ```
- Go into the directory named after your first domain.
- Grab `cert.pem` and `privkey.pem`
- Make local copies of them.
- Exit out of the container with `Ctrl-D`.
- On local laptop, create the certificate secret in kubernetes:
  ```
  $ kubectl create secret tls bankkyc-vcreds-cert --key ./privkey.pem --cert ./cert.pem
  ```
- Delete the existing ingress:
  ```
  $ kubectl delete ingress --all
  ```
- Deploy the new ingress:
  ```
  $ kubectl apply -f ingress.yml
  ```
