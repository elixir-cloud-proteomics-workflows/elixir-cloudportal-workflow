import redis
import requests
import os
import datetime
import pause
import time
import zipfile
import boto3
import uuid
import sys
import json
from collections import defaultdict
import daemon
import argparse
import RedisQueue  # TODO move to https://python-rq.org/ (import rq)?

# TODO lifetime expiry of result url ?!
# # add timer in default html, put expiry date into response

def main():
    parser = argparse.ArgumentParser(description='Request PRIDE ObjectStore access for a submission analysis.')
    parser.add_argument('-p', '--pxd', required=True,
            action="store", dest="pxd_acc",
            help="The PRIDE submission accession (usually PXD0...)", default="PXD011124")
    parser.add_argument('-d','--deployment_nr', 
            action="store", dest="deployment_nr", required=True,
            help='Deployment number from (EBI cloud) portal.')
    parser.add_argument('--redis_host', action="store", dest="redis_host",
            help='PRIDE cloud redis host address', default='192.168.0.16')
    parser.add_argument('--redis_port', action="store", dest="redis_port", type=int,
            help='PRIDE cloud redis host address', default=6379)
    parser.add_argument('--redis_db', action="store", dest="redis_db", type=int,
            help='PRIDE cloud redis db for the request channels', default=1)
    parser.add_argument('--timeout', action="store", dest="timeout", type=int,
            help='Seconds to wait for the tickets before timeout)', default=30)
            
    options = parser.parse_args()

    # nb queue name for ticket requests is hardcoded, the response queue is exclusive for the request named after the deployment_nr
    deploymentrequests = RedisQueue.RedisQueue('requests', host=options.redis_host, port=options.redis_port, db=options.redis_db)  
    tickets = RedisQueue.RedisQueue(str(options.deployment_nr), host=options.redis_host, port=options.redis_port, db=options.redis_db)  
    
    #req = '{"PXD": "PXD01234", "deployment_nr": "123verylongstring789"}'
    deploymentrequests.put(json.dumps({"PXD": options.pxd_acc , "deployment_nr": options.deployment_nr }))
    t = tickets.get(timeout=options.timeout)
    
    if t:
        res = json.loads(t)
        if res['deployment_nr'] != options.deployment_nr: 
            sys.exit("Not my request")  # TODO unlikely, but if redis glitches up, this should be caught
        for i,fetched_url in enumerate(res['raw_urls']):
            # with open(urlfilename.format(ext=i), 'a') as the_file:
            with open(fetched_url.split('/')[-1] + '.url', 'a') as the_file:
                the_file.write(fetched_url)
        with open('result_put.res', 'a') as the_file:
            the_file.write(res['signed_result']['put'])
        with open('result_get.res', 'a') as the_file:
            the_file.write(res['signed_result']['get'])
        # TODO write the mzml for added value upload
    else:
        sys.exit("No Raw files or result upload spot available.")
        
        

if __name__ == "__main__":
    main()