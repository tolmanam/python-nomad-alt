import os

# internal ip of docker
IP = os.environ.get("NOMAD_IP", "127.0.0.1")

# use vagrant PORT if env variable is not specified, generally for local
# testing
NOMAD_PORT = os.environ.get("NOMAD_PORT", 4646)

# Security token
# NOMAD_TOKEN = os.environ.get("NOMAD_TOKEN", None)
NOMAD_TOKEN = os.environ.get("NOMAD_TOKEN", None)

EXAMPLE_JOB_JSON = "example.json"
EXAMPLE_JOB_NAME = "example"
