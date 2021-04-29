# Oracle v2 upgrade vote check

This test forks the mainnet at its current state and checks that execution of the [vote 63] leads to the expected outcome:

* The oracle is actually upgraded to v2.
* The expected roles and ACL permissions are added.
* The oracle is configured with the expected allowed balance increase and decrease values.
* The first report after the upgrade would pass.
* Other important checks.

[vote 63]: https://mainnet.lido.fi/#/lido-dao/0x2e59a20f205bb85a89c53f1936454680651e618e/vote/63/

## Running the test

Edit the `networks.development.cmd_settings.fork` field in the `brownie-config.yml`, setting it to an archival ETH1 node endpoint. Then, run:

```
brownie test --network development
```
