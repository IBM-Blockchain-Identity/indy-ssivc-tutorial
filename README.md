# Indy World Demo

The Indy World Demo implements the **Alice Demo** described in [Getting Started with Indy](https://github.com/hyperledger/indy-node/blob/stable/getting-started.md). The demo shows how a self-sovereign identity ("SSI") can be used to obtain credentials from an issuer and supply these credentials to a verifier in response to a proof request thus providing a verifiable proof.

This repo provides a hands on tutorial as well as a [narrated video recording](../../raw/master/docs/video/IndyWorldVideo2.mp4).  

## Acknowledgments

As part of an initiative to manage [Verifiable Organizations with Self-Sovereign Identities](https://von.pathfinder.gov.bc.ca), the  Government for the [Province of British Columbia](https://www2.gov.bc.ca) ("BC-Gov") has contributed several [open-source projects](https://github.com/bcgov) that are helpful in bootstrapping new applications that make use of [Hyperledger Indy](https://wiki.hyperledger.org/projects/indy) ("Indy") and [Verifiable Credentials](https://www.w3.org/TR/verifiable-claims-data-model/). This Indy World Demo is derived from the [permitify](https://github.com/bcgov/permitify) and [von-network](https://github.com/bcgov/von-network) repositories. 

## Overview

The Indy World Demo is intended to serve as a complimentary tutorial for anyone interested in learning how verifiable credentials are exchanged within a Hyperledger Indy environment. 

### Alice's Digital Credential Story

Know your customer ("KYC") is a business process associated with the regulatory activities used by banks and other institutions to identify and verify the identity of their clients. After graduating from college Alice desires to open a new account with Thrift Bank. The bank has a new self-service offering whereby new clients can quickly and seamlessly use digital credentials to satisfy the bank's KYC requirements. 

As luck would have it, Alice recently took advantage of a new digital transcript offering from her alma mater, Faber College. This digital transcript came in handy during her application process with her new employer, Acme Corporation ("Acme"). Upon being hired, Acme issued Alice a digital Job Credential.  Using her digital wallet which contains education and employment credentials, Alice is confident she can take advantage of Thrift Bank's new self-service offering.

### Verifiable Credential Roles

Given the roles and responsibilities outlined in the [Verifiable Credentials](https://www.w3.org/TR/verifiable-claims-data-model/) specification, Alice's KYC story can be described using the following abstract concepts:

| Role | Description | Examples |
| --- | --- | --- | 
| *Holder* | An entity that is in control of one or more verifiable credentials. | A holder can be a person, organization or a connected device. Alice is a holder.|
| *Issuer* | An entity that creates a verifiable credential, associates it with a particular subject, and transmits it to a holder.| Issuers include corporations, governments, and individuals. Faber College and Acme are issuers.|  
| *Inspector-Verifier* | An entity that receives one or more verifiable credentials (specified by a proof request) for processing. | Verifiers include employers, security personnel, and websites. Acme and Thrift Bank are verifiers.|
| *Identifier Registry* |Mediates the creation and verification of subject identifiers.| Identifier registries include corporate employee databases, government ID databases, and distributed ledgers. For demonstration purposes we use a distributed ledger comprised of a pool of Indy nodes. |

![vc-roles](https://w3c.github.io/vc-data-model/diagrams/ecosystem.svg)

## Architecture

This Indy World Demo leverages three repositories contributed by BC-Gov to enable a person to register for a ficticious Government ID, and then use that ID to obtain a college transcript, apply for and get hired by a company, and apply for a loan.

The repositories are:

[VON Network](https://github.com/bcgov/von-network):  The VON Network creates a 4-node Indy node pool.  Each node contains a blockchain ledger.  These ledgers are kept in sync and verified using a consensus algorithm.  

[The Org Book](https://github.com/bcgov/TheOrgBook): The Org Book is a repository of businesses and their associated credentials and permits.  It was modified to hold verifiable credentials for individuals.  These credentials are issued by Issuers such as colleges, companies and banks.

[Permitify](https://github.com/bcgov/permitify):  Permitify instantiates the Issuers for the demo.  There are four Permitify-Issuer services:

* Government SSI App, which issues a *Gov ID*
* Faber College SSI App, which issues a *Student Transcript*
* Acme SSI App, which issues a *Credential of Employment*
* Thrift Bank SSI App, which issues a *Bank Account*

Each one of these Issuers creates a verifiable credential for an individual that is described by a credential schema definition.  Before issuing a credential, a proof request must be filled out using the individual's currently held credentials and verified by the institution.

The figure below shows the various components for the demo.

![demo architecture](../../raw/master/docs/images/architecture.png)


[Indy SDK](https://github.com/hyperledger/indy-sdk):  Indy is an implementation of a self-sovereign identity ecosystem on top of a distributed ledger.

[Wallet](https://sovrin.org/wp-content/uploads/2018/03/Sovrin-Provisional-Trust-Framework-2017-06-28.pdf): Secure storage for keys, credentials, and other private data used by holder, issuer, inspector-verifier or identifer registry.

[Indy Node](https://sovrin.org/wp-content/uploads/2018/03/Sovrin-Provisional-Trust-Framework-2017-06-28.pdf):  A computer network server running an instance of the Sovrin Open Source Code (Indy) to maintain the Sovrin Ledger.

[VON Agent](https://github.com/PSPC-SPAC-buyandsell/von_agent): A higher-level API created by BC-Gov that wraps the Indy SDK.

## Using Indy World

### Installing

This project includes three git repositories from BC-Gov (VON Network, TheOrgBook and Permitify) as described under the architecture section.

Cloning the indy-world repo will fetch all of the code for our customized versions of the BC-Gov repos need to build and run the Indy World demo.

```
$ git clone https://github.com/IBM-Blockchain-Identity/indy-ssivc-tutorial.git
$ cd indy-ssivc-tutorial
```

### Building

You need to build the components VON Network, TheOrgBook and Permitify.

To build VON Network:

```
$ cd von-network
$ ./manage build
```

To build TheOrgBook:

```
$ cd TheOrgBook/docker
$ ./manage.sh build
```
To build Permitify:

```
$ cd permitify/docker
$ ./manage build
```

You can rebuild the docker images using the 'rebuild' option.

### Running

VON Network needs to be started first.

To start VON Network, open a new terminal and enter the commands:

```
$ cd von-network
$ ./manage start
```
Wait until all the nodes have completely started before starting TheOrgBook.

TheOrgBook needs to be started next.

To start TheOrgBook, open a new terminal and enter the commands:

```
$ cd TheOrgBook/docker
$ ./manage.sh start
```

Wait until TheOrgBook has completely started before starting Permitify.

To start Permitify, open a new terminal and enter the commands:

```
$ cd permitify/docker
$ ./manage start all
```

Once all containers are started, you can view the node pool and ledger by visiting the following web page in your browser:

To view the node pool (VON Network):

```
http://localhost:9000/
```

The VON Network web UI enables the ledgers to be inspected.  The genesis file can also be viewed.

![von-network](../../raw/master/docs/images/von-network.png)

You can run the demo by visiting the following web page in your browser:

To run the demo:

```
http://localhost:8080/
```

### Stopping

To stop an application, press Ctrl-C.  This should stop all docker containers that the command started.

If there are still containers running, you can use the following command to stop them:

VON Network:

```
$ cd von-network
$ ./manage stop
```

TheOrgBook:

```
$ cd TheOrgBook/docker
$ ./manage.sh stop
```

Permitify:

```
$ cd permitify/docker
$ ./manage stop
```

### Cleaning Up

The docker containers and volumes created when running the demo can be removed using the **manage rm** parameter.  If you are having problems adding a user or veriying credentials, this command can also be called to reset the data used for the demo.

VON Network:

```
$ cd von-network
$ ./manage rm
```

TheOrgBook:

```
$ cd TheOrgBook/docker
$ ./manage.sh rm
```

Permitify:

```
$ cd permitify/docker
$ ./manage rm
```

## Demo

To run the demo, load the homepage in your browser:

```
http://localhost:8080/
```

The homepage shows an outline of the demo steps in an order that is enforced by verifiable credentials.  For example, a person can't be hired for a job and obtain a job credential until they can prove that they hold a degree.  The verification of a degree is accomplished by filling out a proof request (Acme Corp) with information from a previously obtained and verified credential (Faber College).

The demo consists of 5 steps:

1. Register a person
2. Obtain a college transcript
3. Apply for a job
4. Get hired
5. Apply for a loan

![homepage](../../raw/master/docs/images/homepage.png)

To register a person and create a new online government identity, click on the **Register Person** button.

After registering a new person, a list of credential issuers is shown.  To obtain a credential from one of these issuers, click on the corresponding button.  Note that only those issuers that have all dependencies met can be successfully called.

### Register a Person

Alice can obtain a government ID by clicking on the **Register Person** button.  This displays a form hosted on the Gov ID website that could have been filled out by a government employee after vetting Alice in person, or filled out by Alice after logging in to the Gov ID website with credentials she already uses to access other government services.  Either way, this is Alice's on-ramp to using verifiable credentials.

![gov_id](../../raw/master/docs/images/gov_id.png)

When the **Submit** button is pressed, a credential is generated by Gov ID and downloaded into Alice's wallet.  Note that Alice's credential is also saved in the issuers (Gov ID) wallet.

![list_gov](../../raw/master/docs/images/list_gov.png)

Now that Alice has a credential, she can use that credential to prove who she is to other issuers.

The demo now shows which credentials Alice has obtained and which ones she needs before requesting a new credential from a particular issuer.  

The webpage shows that Alice has a Gov ID credential, and can now request a transcript from Faber College since she holds all **Depends on** credentials in her wallet.  Note that she cannot apply for a job yet, since the transcript dependency isn't met, as indicated by a red X.

Before Alice requests her transcript from Faber College, she wants to view her credential from Gov ID.  Clicking on **View Certificate** in the Gov ID section, Alice's credential is displayed.  This credential can be verified by clicking on the **Verify Credential** button.

![alice_gov_id](../../raw/master/docs/images/alice_gov_id.png)

This creates a proof request from Alice, which is filled in using information from the Gov ID credential in Alice's wallet.  It is cryptographically verified and determined to be valid.  The content below the **Verify Credential** button shows the details of the proof request.  This is only for demo purposes, and would not be normally revealed to a user.

Clicking the **Back to Person Info** link shows the various credentials that Alice has collected in her wallet.  At this point, there's only one - the Gov ID credential.

![alice_gov_id](../../raw/master/docs/images/alice_one.png)

Click **Back** to return to the list of issuers.

### Obtain College Transcript

From the credentials list Alice now clicks on **Get college transcript**.  This operation may take 20 seconds or more.  Under the covers Alice obtains a proof request definition from Faber College, automatically fills in with her ID credential, sends it to Faber College, and then Faber College cryptographically validates the contents of the proof.  Once this process has completed, a form is displayed from the Faber College website.  Normally, this form would be filled in by the registrars office; however, for demo purposes, we are filling it out now. 

Notice the claim data displayed at the bottom of the form.  This is the verified data provided by Alice's Gov ID credential from her wallet in response to a proof request from Faber College. 

When **Submit** is pressed, Faber College creates the transcript credential and sends it to Alice.  Alice then saves it in her wallet.

![faber_college](../../raw/master/docs/images/faber_college.png)

### Apply for a Job

To apply for a job at Acme Corp, Alice clicks on **Apply for a job**.  This displays the Job Application form with most of the information filled in from credentials that Alice holds in her wallet.

Clicking on **Submit** will create a job application credential, which is saved in both Alice's and Acme Corp's wallet.  Acme will use this verified credential information as part of the interviewing process to decide if they want to hire Alice.

![acme_application](../../raw/master/docs/images/acme_application.png)

### Get Hired

Good news!  Alice has been hired by Acme Corp.  Someone from the human resources department at Acme will click on the **Issue certificate for a job** button to create a credential for Alice attesting to her employment.

Alice might be notified that a job credential is available from Acme via e-mail or on their employee website.  Either way, Alice can add this credential to her wallet to validate her employment status.  For this demo, the job credential is added to Alice's wallet by clicking on the **Submit** button.

![acme_hired](../../raw/master/docs/images/acme_hired.png)

### Apply for a Loan

Now that Alice has a job, she can apply for a loan from Thrift Bank.  She clicks on **Apply for a loan** to display the loan application from Thrift Bank.

The loan application form is completely pre-populated with verified information from multiple credentials in Alice's wallet.  

Note that Alice has the opportunity to edit and disclose only the information that she wants Thrift Bank to know.  In a real application, each of these input boxes would allow Alice to pick which credential to use for that particular data.

Alice clicks the **Submit** button to apply for the loan.

![thrift_bank](../../raw/master/docs/images/thrift_bank.png)

### View all Credentials

Alice has obtained all credentials from the list of issuers in the demo.  She can view any of the credentials by clicking on the **View certificate** button. 

![list_all](../../raw/master/docs/images/list_all.png)

All of the credentials that Alice has in her wallet can be viewed by clicking on the **View record of person** button.

The individual credentials can be viewed and verified if desired.

![list_alice](../../raw/master/docs/images/alice_all.png)


## Known Issues

- Creating more than 1 person fails.  You must stop and rm VON Network, TheOrgBook and Permitify before running again.

## Code Repos

### BC-Gov Code Repos

- [Permitify](https://github.com/bcgov/permitify)
- [TheOrgBook](https://github.com/bcgov/TheOrgBook)
- [VON Network](https://github.com/bcgov/von-network)

### Indy Code Repos

- [Indy Node](https://github.com/hyperledger/indy-node)
- [Indy SDK](https://github.com/hyperledger/indy-sdk)
- [Indy Plenum](https://github.com/hyperledger/indy-plenum)
- [Indy Crypto](https://github.com/hyperledger/indy-crypto)
- [Indy AnonCreds](https://github.com/hyperledger/indy-anoncreds)