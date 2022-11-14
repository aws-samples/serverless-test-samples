# Load Testing

## Perform a load test
Load tests should be executed in the cloud prior to any initial deployment to production environments. Load tests can be useful to discover performance bottlenecks and quota limits. Load tests should be scripted and repeatable. Load tests should simulate your application's expected peak load. 

[Artillery](https://www.artillery.io/) is used for load testing. Load tests scenarios are configured using a yaml configuration file. The configured load tests runs 100 requests / second for 10 minutes to our API endpoints.

To execute the load tests run either the PowerShell or bash scripts under the [load test directory](./loadtest).

```bash
cd loadtest
./run-load-test.sh
```

```powershell
cd loadtest
./run-load-test.ps1
```