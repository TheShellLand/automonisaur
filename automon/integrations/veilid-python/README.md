# Veilid Bindings for Python
Create an application in Python using the distributed [Veilid](https://veilid.com) framework for app-to-app communication.

## Prerequisites
* A headless Veilid node must be installed on the same host as the Python application. Install instructions can be found [here](https://gitlab.com/veilid/veilid/-/blob/main/INSTALL.md)
* Veilid Python makes heavy use of async and other bleeding edge functions requiring Python version >= 3.11.4

## Usage

To use:
```
poetry add veilid
```
or 
```
pip3 install veilid
```


## Development

To run tests:
```
poetry run pytest
```

To update schema for validation with the latest copy from a running `veilid-server`:
```
./update_schema.sh
```

## Basic Veilid App Setup
A demo chat application is available to review [here](https://gitlab.com/veilid/python-demo).