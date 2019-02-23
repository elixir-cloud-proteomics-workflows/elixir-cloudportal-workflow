#!/usr/bin/env python
import requests
import json
import sys
from collections import defaultdict
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='Retrieve raw file urls from PRIDE accession.')
    parser.add_argument('-p', '--pxd', required=True,
            action="store", dest="pxd_acc",
            help="The PRIDE submission accession (usually PXD0...)", default="PXD011124")
    parser.add_argument('-d','--dest', 
            action="store", dest="wd",
            help='Destination directory', default=os.getcwd())

    options = parser.parse_args()
    
    if not os.path.exists(options.wd):
        os.makedirs(options.wd)
    os.chdir(options.wd)

    fetched_urls = list()
    pride_projectfiles_url = 'http://wwwdev.ebi.ac.uk/pride/ws/archive/projects/{pxd}/files'
    pxd_acc = options.pxd_acc
    i = 0
    stop_cnd = False
    num_pages = sys.maxsize
    projectfiles = defaultdict(list)
    payload_template = {'sortDirection': 'ASC', 'pageSize': 15}  # , 'filter': 'fileName=regex=mzML'  #remove filter to avoid 0 result
    while not stop_cnd:
        payload = {'page': i}.update(payload_template)
        r = requests.get(pride_projectfiles_url.format(pxd = pxd_acc), params=payload)
        data = r.json()
    
        if r.status_code == 200 and data.get('page', {}) and data.get('_embedded', {}).get('files', {}):
            num_pages = data['page']['totalPages']
            #TODO failsafe with page': {'totalElements': 0,
            for fls in data.get('_embedded').get('files'):
                projectfiles[fls['accession']] = fls
            i += 1
            if i >= num_pages:
                stop_cnd = True
        else:
            stop_cnd = True
    if r.status_code == 410 or not projectfiles:
        sys.exit("Pride submission {pxd} not found!".format(pxd=pxd_acc))
        # TODO http://wwwdev.ebi.ac.uk/pride/ws/archive/projects/SAD/files returns 200, should be 410

    for ax,fi  in projectfiles.items():
        if fi.get('fileCategory').get('accession') == "PRIDE:0000404":
            fetched_urls.extend([ftp.get('value') for ftp in fi.get('publicFileLocations') if ftp.get('accession')== 'PRIDE:0000469'])

    for i,fetched_url in enumerate(fetched_urls):
        # with open(urlfilename.format(ext=i), 'a') as the_file:
        with open(fetched_url.split('/')[-1] + '.url', 'a') as the_file:
            the_file.write(fetched_url)

if __name__ == "__main__":
    main()