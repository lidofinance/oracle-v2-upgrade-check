# Oracle v2 upgrade vote check

This test forks the mainnet at its current state and checks that execution of the [vote 63] leads to the expected outcome:

* The oracle is actually upgraded to v2.
* The expected roles and ACL permissions are added.
* The oracle is configured with the expected allowed balance increase and decrease values.
* The first report after the upgrade would pass.
* Other important checks.

[vote 63]: https://mainnet.lido.fi/#/lido-dao/0x2e59a20f205bb85a89c53f1936454680651e618e/vote/63/

## Running the check

Set the key `networks.development.cmd_settings.fork` in the `brownie-config.yml` to the ETH1 node endpoint (in case of any issues try an archival ETH1 node). Then, run:

```
brownie test --network development
```
