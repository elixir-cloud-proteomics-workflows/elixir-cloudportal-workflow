#!/usr/bin/env nextflow
 
params.input = "PXD011124"
params.out = "./result.txt"
// fileinfo_datasets = Channel.fromPath(params.input)
// myURL = Channel.create()
// myFILENAME = Channel.create()

process fetchURLS {
    // container 'docker://quay.io/mwalzer/prideapicrawler:master'

    output:
    file "*" into urls

    script:
    """
    #!/usr/bin/env python
    import requests
    import json
    import sys
    from collections import defaultdict
    
    fetched_urls = list()
    pride_projectfiles_url = 'http://wwwdev.ebi.ac.uk/pride/ws/archive/projects/{pxd}/files'
    pxd_acc = '${params.input}'
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


    for ax,fi  in projectfiles.items():
        if fi.get('fileCategory').get('accession') == "PRIDE:0000404":
            fetched_urls.extend([ftp.get('value') for ftp in fi.get('publicFileLocations') if ftp.get('accession')== 'PRIDE:0000469'])

    urlfilename = "pxf_url_{ext}.url"
 
    for i,fetched_url in enumerate(fetched_urls):
        # with open(urlfilename.format(ext=i), 'a') as the_file:
        with open(fetched_url.split('/')[-1] + '.url', 'a') as the_file:
            the_file.write(fetched_url)
            #myURL.bind(fetched_url)
            #myFILENAME.bind(fetched_url.split('/')[-1])
    """
}

process downloadFiles {
    // container 'alpine'
    input:
    file myurl from urls.flatten()

    output:
    file '*.raw' into rawFiles
   
    script: 
    """
    wget -i $myurl 
    """
}

process convertRawFile {
    container 'quay.io/mwalzer/thermorawfileparser:master' 
     
    input:
    file rawFile from rawFiles
    
    output: 
    file '*.json' into metaResults
    file '*.mzML' into fileinfo_datasets
    
    script:
    """
    mono /src/bin/x64/Debug/ThermoRawFileParser.exe -i=${rawFile} -m=0 -f=1 -o=./
    """
}

/*
 * mzml to tsv
 */
process openmsFileInfo {
 
    container 'mwalzer/openms-batteries-included:V2.3.0_pepxmlpatch'
    cpus 1
    
    input:
    file new_mzML from fileinfo_datasets

    output:
    file "${new_mzML.baseName}.txt" into fileinfo_results
    
    """
    FileInfo  \
        -in $new_mzML \
        -out ${new_mzML.baseName}.txt
    """
 
}

/*
 * Collects all the sequences files into a single file
 * and prints the resulting file content when complete
 */
fileinfo_results
    .collectFile(name: params.out)
    .println { file -> "FileInfo for the given files:\n ${file.text}" }

