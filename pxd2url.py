#py3.5
import requests
import json
import sys
from collections import defaultdict

pride_projects_url = 'http://wwwdev.ebi.ac.uk/pride/ws/archive/projects'

i = 0
stop_cnd = False
num_pages = sys.maxsize
projects = dict()
while not stop_cnd:
    payload = {'sortDirection': 'ASC', 'pageSize': 15, 'page': i}
    r = requests.get(pride_projects_url, params=payload)
    data = r.json()
    
    if r.status_code == 200 and data.get('page', {}):
        #TODO failsafe with page': {'totalElements': 0,
        num_pages = data['page']['totalPages']
        for prd in data.get('_embedded').get('projects'):
            projects[prd['accession']] = prd
        i += 1
    else:
        stop_cnd = True

len(projects)
import pprint
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(r)
pp.pprint(data)

#############

pride_projectinfo_url = 'http://wwwdev.ebi.ac.uk/pride/ws/archive/projects/{pxd}'
pxd_acc = 'PXD009996'
projectinfo = list()
r = requests.get(pride_projectinfo_url.format(pxd = pxd_acc))
data = r.json()
if r.status_code == 200:
    projectinfo = data
else:
    print("bah!")

pp.pprint(projectinfo)

#############

pride_projectfiles_url = 'http://wwwdev.ebi.ac.uk/pride/ws/archive/projects/{pxd}/files'
pxd_acc = 'PXD009996'
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
            projectfiles[fls['accession']] = fls  # PXF00000770344 -> {info}
        i += 1
        if i >= num_pages:
            stop_cnd = True
    else:
        stop_cnd = True

pp.pprint(projectfiles)

#############

pride_fileinfo_url = 'http://wwwdev.ebi.ac.uk/pride/ws/archive/msruns/{pxf}/'
pxf_acc = 'PXF00000770344'
i = 0
stop_cnd = False
fileinfo = defaultdict(list)
r = requests.get(pride_fileinfo_url.format(pxf = pxf_acc))
data = r.json()
if r.status_code == 200 and pxf_acc in projectfiles:
    fileinfo[pxf_acc].update(data)
    # update overwrites not none with none! params = urllib.urlencode({k: v for k, v in (('orange', orange), ('apple', apple)) if v is not None})
else:
    print("bah!")

pp.pprint(fileinfo)

#############


# get organism, instrument type, experiment type and mzml or raw file

organisms = [ x.get('accession') for x in projectinfo.get('organisms')]
instruments = [ x.get('accession') for x in projectinfo.get('instruments')]

urls = list()
# publicFileLocations - list of dict  get all 'value' where 'accession': 'PRIDE:0000469'
# fileCategory - dict check accession PRIDE:0000404  # 'raw'
                #  or check accession PRIDE:0000409  # 'peak'
for ax,fi  in projectfiles.items():
    if fi.get('fileCategory').get('accession') == "PRIDE:0000404":
        # print(ax)
        # print(fi.get('fileName'))
        # print([ftp.get('value') for ftp in fi.get('publicFileLocations') if ftp.get('accession')== 'PRIDE:0000469'])
        urls.extend([ftp.get('value') for ftp in fi.get('publicFileLocations') if ftp.get('accession')== 'PRIDE:0000469'])

# https://pypi.org/project/pronto/
# Combine two ontos
import pronto
ont = pronto.Ontology('path/to/file.obo')
term = ont['REF:ACCESSION']
ms  = pronto.Ontology('https://raw.githubusercontent.com/HUPO-PSI/psi-ms-CV/master/psi-ms.obo')
ms.merge(nmr)

# Find ontology terms with children
import pronto
ont = pronto.Ontology('../ms-tools/oms-develop/share/OpenMS/CV/psi-ms.obo')
for term in ont:
    if term.children:
        print(term)

# Get all the transitive children of an ontology term
import pronto
ont = pronto.Ontology('path/to/file.obo')
print(ont['RF:XXXXXXX'].rchildren())


############
# pxd based queries in precedence: organism, instrument, #raw
pride_projectfiles_url = 'http://wwwdev.ebi.ac.uk/pride/ws/archive/projects/{pxd}/files'
pride_projectinfo_url = 'http://wwwdev.ebi.ac.uk/pride/ws/archive/projects/{pxd}'

for pxd_acc in sorted(projects.keys())[::-1]:
    projectinfo = list()
    r = requests.get(pride_projectinfo_url.format(pxd = pxd_acc))
    data = r.json()
    if r.status_code == 200:
        projectinfo = data
    else:
        print("bah, {p}!".format(p=pxd_acc))
        continue

    organisms = [ x.get('accession') for x in projectinfo.get('organisms')]  # Human (accesion number 9609 )
    instruments = [ x.get('accession') for x in projectinfo.get('instruments')]  # Q-Exactive (accession number MS:1001911 ) 
    if  '9606' not in organisms or 'MS:1001911' not in instruments:
        continue

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
                projectfiles[fls['accession']] = fls  # PXF00000770344 -> {info}
            i += 1
            if i >= num_pages:
                stop_cnd = True
        else:
            stop_cnd = True

    urls = list()
    # publicFileLocations - list of dict  get all 'value' where 'accession': 'PRIDE:0000469'
    # fileCategory - dict check accession PRIDE:0000404  # 'raw'
                    #  or check accession PRIDE:0000409  # 'peak'
    for ax,fi  in projectfiles.items():
        if fi.get('fileCategory').get('accession') == "PRIDE:0000404":
            # print(ax)
            # print(fi.get('fileName'))
            # print([ftp.get('value') for ftp in fi.get('publicFileLocations') if ftp.get('accession')== 'PRIDE:0000469'])
            urls.extend([ftp.get('value') for ftp in fi.get('publicFileLocations') if ftp.get('accession')== 'PRIDE:0000469'])
    if len(urls) < 6 and len(urls) > 3:
        pp.pprint(pxd_acc)
        pp.pprint(projectfiles)
        break

# >>> pxd_acc
# 'PXD011124'
# >>> urls
# ['ftp://ftp.pride.ebi.ac.uk/pride/data/archive/2018/09/PXD011124/Service_ElAffar_300816_15.raw', 'ftp://ftp.pride.ebi.ac.uk/pride/data/archive/2018/09/PXD011124/Service_ElAffar_300816_14.raw', 'ftp://ftp.pride.ebi.ac.uk/pride/data/archive/2018/09/PXD011124/Service_ElAffar_300816_13.raw', 'ftp://ftp.pride.ebi.ac.uk/pride/data/archive/2018/09/PXD011124/Service_ElAffar_300816_16.raw']