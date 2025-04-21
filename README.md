# BT - BeyondTrust Secrets Retrieval Library

A Python library to retrieve secrets from **BeyondTrust Password Safe**, using either a secret **name** or **ID**.


---

## Must do's

- Please set ***RUNAS*** and ***AUTH_KEY*** in your environment/Pipeline.
- ***RUNAS*** must be set as ***BT_CREDS_Username*** or ***Username***
- ***AUTH_KEY*** must be set as ***BT_CREDS_AUTHKEY*** or ***BT_AUTH_KEY***
- ***BASE_URL*** must be exported as well.

## Features

- Retrieve secrets by **ID** or **Name**
- To retrieve a password using the username, use: "BT.secretname"
- To retrieve a password using the secret ID, use: "BT.secretid"


---

##  Installation

You can install this using:

```bash
pip install git+https://github.com/SarthakChaudhary46/BeyondTrust-Password-Fetch.git
```

## Example

```bash
import  BT as btsecrets

print(btsecrets.secretname("svcacct"))
print(btsecrets.secretid('2f29c'))
```
