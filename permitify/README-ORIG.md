# NOTICE

THIS README IS FROM THE ORIGINAL REPO AND IS NOT ACCURATE FOR INDY WORLD DEMO.  IT HAS BEEN LEFT FOR REFERENCE ONLY.

# Permitify
A end-to-end demonstration of the VON in action.

Includes a "roadmap" site which the user can follow like a checklist.

Also includes the precursor to the von-connector. The goal is to allow all issuers and verifiers to be declaratively configurable.

## Running in OpenShift

This project uses the scripts found in [openshift-project-tools](https://github.com/BCDevOps/openshift-project-tools) to setup and maintain OpenShift environments (both local and hosted).  Refer to the [OpenShift Scripts](https://github.com/BCDevOps/openshift-project-tools/blob/master/bin/README.md) documentation for details.

## Running Locally

0. An instance of TheOrgBook must be running. By default, Permitify looks for TheOrgBook running on your local machine. Look here for instructions on running TheOrgBook: https://github.com/bcgov/TheOrgBook

1. First, install Docker. Download the installer for your operating system [here](https://store.docker.com/search?type=edition&offering=community). Once it is installed, keep the Docker daemon running in the background.

2. Linux users will also need to [install docker-compose](https://github.com/docker/compose/releases). Mac and Windows users will have this already. 

3. Once Docker has been installed, open a terminal session and clone this repository:

```bash
git clone <repository url> permitify && cd permitify/docker
```

4. Now you can build the Dockerfile into an image which we will use to run containers (this process will take several minutes):

```bash
./manage build
```

5. Once the build process completes, you can test the build to make sure everything works properly:

You will need to choose a unique seed value for development. Use a value that no one else is using. It must be 32 characters long exactly.

```bash
./manage start all seed=my_unique_seed_00000000000000000
```

When you run the services, each service will use a seed derived from the seed you pass in. Currently, it increments the last character value for each service. So for the example above, it will use the follow seeds for each service:

- my_unique_seed_00000000000000001
- my_unique_seed_00000000000000002
- my_unique_seed_00000000000000003
- my_unique_seed_00000000000000004
- my_unique_seed_00000000000000005
- my_unique_seed_00000000000000006

You can see which seed value each service using by looking at the logs like this:

```
----------------------------------------------------------------------------------
No command line parameters were provided to the entry point.
Using the values specified for the environment, or defaults if none are provided.

TEMPLATE_NAME: bc_registries
APPLICATION_IP: 0.0.0.0
APPLICATION_PORT: 8080
INDY_WALLET_SEED: my_seed_000000000000000000000001
----------------------------------------------------------------------------------
```

Each seed, must be authorized on the indy ledger! If you are using the https://github.com/bcgov/von-network network locally, you can visit the webserver running on your local machine to authorize the did for each seed. If you are using the shared development Indy ledger (which is an instance of von-network), you can visit this page to authorize your did: http://138.197.170.136

You should now be able to visit the services on the following urls:

- localhost:5000
- localhost:5001
- localhost:5002
- localhost:5003
- localhost:5004
- localhost:5005

And any other services that are later defined in docker-compose.yml.

Services are defined using config files. See ./site_templates for examples of the existing services.

During development, you can run

```bash
./manage start seed=my_unique_seed_00000000000000000
```

which will only start the first service with the source directory mounted as a volume for quicker development.


## Caveats

### General

You may receive errors that look something like this:

```
Casting error to ErrorCode: Rejected by pool: {"op":"REQNACK","reqId":1513638530415465900,"reason":"client request invalid: ColdNotAuthenticate('Can not find verkey for DID QmaAjcfw2HCgydR1daFg9V',)","identifier":"QmaAjcfw2HCgydR1daFg9V"}
```

This indicates the agent has not been registered and you need to authorize a new DID for the agent.  Use the [VON-Network](http://138.197.170.136) site to do this.  The seeds for the agents are defined in the config.toml file for each site.

Examples:

```
http://138.197.170.136/register?seed=bc_registries_agent_000000000000
http://138.197.170.136/register?seed=worksafe_bc_agent_00000000000000
```

### On dev machines

- If you get WalletNotFoundError when submitting a claim, try incrementing the schema version and fully restarting the server. This will re-publish the schema and related claim definition which should fix this. This can occur if the wallet didn't persist properly from a previous restart and the definition cannot be found in the wallet. **This will also be needed on first run.**

- For Django's hot-reloading to work in development, the src directory needs to mounted as a volume. This only works when one "service" is defined in the docker-compose.yml since multiple services will clobber each other's config files that get copied in.

- The wallet directory must be mounted in an internal volume. See docker-compose.yml for example.