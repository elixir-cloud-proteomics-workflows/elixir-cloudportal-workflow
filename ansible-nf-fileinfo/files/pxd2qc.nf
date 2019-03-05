#!/usr/bin/env nextflow
 
params.input = "/root/*.url"
params.out = "./result.txt"

urls = Channel.fromPath(params.input)

process downloadFiles {
    container 'quay.io/mwalzer/prideapiclient:latest'
    input:
    file myurl from urls.flatten()

    output:
    file '*.raw' into rawFiles
   
    script: 
    """
    #!/usr/bin/env python
    import wget
    with open('${myurl}') as f:
        urls = f.readlines()
    [wget.download(url) for url in urls]
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
 * Collects all the fileinfos into a single file
 * and prints the resulting file content when complete
 */
fileinfo_results
    .collectFile(name: params.out)
    .println { file -> "FileInfo for the given files:\n ${file.text}" }

