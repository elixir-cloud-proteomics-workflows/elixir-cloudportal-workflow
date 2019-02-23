# ELIXIR cloudportal workflow
aka *Elixir QC EBI Qcloud TSI Cloud Portal*

[![Docker Repository on Quay](https://quay.io/repository/mwalzer/prideapiclient/status "Docker Repository on Quay")](https://quay.io/repository/mwalzer/prideapiclient)
[![Nextflow version](https://img.shields.io/badge/nextflow-%E2%89%A50.31.0-brightgreen.svg)](https://www.nextflow.io/)
[![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/elixir_proteomics_QC/community)

-----

## Using nextflow 
The workflow uses nextflow and makes ample use of the container feature.
Example use:
```
../nextflow/nextflow run pxd2qc.nf -c ../nextflow/mynextflow.config -profile local --input PXD011124
```
based on [the generic server Portal app](https://github.com/EMBL-EBI-TSI/cpa-instance.git)

## Input from [PRIDE](https://www.ebi.ac.uk/pride/archive/)
Workflow inputs are PRIDE submission accessions (PXD).
For starters, we will restrict ourselves to Q exactive thermo raw files.