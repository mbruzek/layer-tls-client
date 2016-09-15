# Overview

This is a basic tls-client to show how to use the requires/provides interface.

# Usage

Step by step instructions on using the charm:

```bash
juju deploy tls
juju deploy tls-client
juju add-relation tls tls-client
```

## Known Limitations and Issues

This is not a functional layer or charm, it is just to consume the tls 
interface using the requires/provides relation.


# Contact Information

## Upstream Project Name

  - EasyRSA

