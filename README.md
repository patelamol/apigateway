# apigateway

A command line tool to route api calls to backend application containers.

## Requirements
Requires following library to be installed.
- `docker desktop`: To test backend application running on container. OS specific installation instructions available at [here](https://docs.docker.com/desktop/).
- `poetry`: To manage python package dependencies. OS specific installation instructions available [here](https://python-poetry.org/docs/)

## Getting started
- Clone the repo using git or copy the `apigateway` files to a desired destination.
- Installing dev dependencies: 
  - On a Terminal/ shell/ command prompt navigate to the folder containing `apigateway`.
  - Run following commands;
    ```bash
    # virtualenv
    poetry shell

    # install dependencies
    poetry install
    ```
- Run backend container for local testing, run following `docker-compose` command.
    ```bash
    docker-compose -f tests/test_backend_applications.yml up -d
    ```
- Config file: To run the command line gateway you will need a config YAML, an example of which is available under tests/example/test_payload.yml. 
  This config file has information related to api path and its relevant backend application container.
  The containers are identified by labels attached to them.
- Run the following command without any arguments, and it should pick up the example configuration file mentioned above.
  ```bash
  # execute with example config file. 
  rgate
  # execute with a different config file.
  rgate --config <relative path to the file>
  ```

## Assumption:
- All the backend containers are running locally in the same environment.
- No landing page (`/`) that needs to be served.
- No load balance logic is required.
- No security checks are necessary.
