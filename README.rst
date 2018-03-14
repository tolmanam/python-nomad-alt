Alternative Python client for `HashiCorp Nomad <http://www.nomadproject.io/>`_
======================================================

The python-nomad (https://github.com/jrxFive/python-nomad) module is great, but I wanted a python client for Nomad that would play nicely with Tornado.  Had had some experiance using python-consul (https://github.com/cablehead/python-consul) and was really impressed with what they had done to abstract the HTTP client out of the way so I forked their code base and replaced the Consul API code with the Nomad functions.

TODO 
----
* [ ] Code up the rest of the Nomad API (only wrote the few that I needed to start with)
* [ ] Unit testing
* [ ] Documentation
* [ ] Talk to python-consul project manager and see if it makes sence to share a common code base


Example
-------
.. code:: python

    #!/bin/env python
    
    from nomad_alt import Nomad
    from nomad_alt.tornado import Nomad as tormad
    import os
    import pprint
    import json
    
    IP = os.environ.get("NOMAD_IP", "localhost")
    NOMAD_PORT = os.environ.get("NOMAD_PORT", 4646)
    NOMAD_TOKEN = os.environ.get("NOMAD_TOKEN", None)
    
    test = Nomad(host=IP, port=NOMAD_PORT, verify=False, token=NOMAD_TOKEN)
    
    print "\nList jobs\n"
    for job in test.jobs.list():
        pprint.pprint(job)
    
    job = {
        "Job": {
            "ID": "example",
            "Name": "example",
            "Type": "service",
            "Priority": 50,
            "Datacenters": [
                "dc1"
            ],
            "TaskGroups": [{
                "Name": "cache",
                "Count": 1,
                "Tasks": [{
                    "Name": "redis",
                    "Driver": "docker",
                    "User": "",
                    "Config": {
                        "image": "redis:3.2",
                        "port_map": [{
                            "db": 6379
                        }]
                    },
                    "Services": [{
                        "Id": "",
                        "Name": "global-redis-check",
                        "Tags": [
                            "global",
                            "cache"
                        ],
                        "PortLabel": "db",
                        "AddressMode": "",
                        "Checks": [{
                            "Id": "",
                            "Name": "alive",
                            "Type": "tcp",
                            "Command": "",
                            "Args": None,
                            "Path": "",
                            "Protocol": "",
                            "PortLabel": "",
                            "Interval": 10000000000,
                            "Timeout": 2000000000,
                            "InitialStatus": "",
                            "TLSSkipVerify": False
                        }]
                    }],
                    "Resources": {
                        "CPU": 500,
                        "MemoryMB": 256,
                        "Networks": [{
                            "Device": "",
                            "CIDR": "",
                            "IP": "",
                            "MBits": 10,
                            "DynamicPorts": [{
                                "Label": "db",
                                "Value": 0
                            }]
                        }]
                    },
                    "Leader": False
                }],
                "RestartPolicy": {
                    "Interval": 300000000000,
                    "Attempts": 10,
                    "Delay": 25000000000,
                    "Mode": "delay"
                },
                "EphemeralDisk": {
                    "SizeMB": 300
                }
            }],
            "Update": {
                "MaxParallel": 1,
                "MinHealthyTime": 10000000000,
                "HealthyDeadline": 180000000000,
                "AutoRevert": False,
                "Canary": 0
            }
        }
    }
    
    print "\nCreate job %(ID)s\n" % job["Job"]
    pprint.pprint(test.jobs.create(json.dumps(job)))
    
    print "\nLook up job %(ID)s\n" % job["Job"]
    pprint.pprint(test.jobs.read(job["Job"]["ID"]))
    
    print "Start Testing Tornado interface....\n"
    from tornado import ioloop
    from tornado import gen
    
    loop = ioloop.IOLoop()
    loop.make_current()
    
    @gen.coroutine
    def main():
        c = tormad(host=IP, port=NOMAD_PORT, verify=False, token=NOMAD_TOKEN)
        res = yield c.jobs.list()
        pprint.pprint(res)
        loop.stop()
    loop.run_sync(main)
    
    print "Done Testing Tornado interface....\n"
    
    print "\nStop job %(ID)s\n" % job["Job"]
    pprint.pprint(test.jobs.stop(job["Job"]["ID"], purge=True))
    
    print "\nList jobs\n"
    for job in test.jobs.list():
        pprint.pprint(job)
    
