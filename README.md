# NIMS_to_BIDS Conversion

## Summary

Takes neuroimaging downloaded from the Neurobiological Image Managament System at Stanford University (https://cni.stanford.edu/nims/) and converts it to BIDS format(http://bids.neuroimaging.io/). 

## NIMS and BIDS Directory Structures
```
NIMS Data Format (must be downloaded from the GUI in legacy format)

|-- ProjectFilename
    |-- NIMS_participants.csv
    |-- NIMS_protocol.csv
    |-- NIMS_data
        |-- 20170101_14000
            |-- 0001_01_3Plane_Loc_fgre.nii.gz
            |-- 0003_01_ASSET_calibration.nii.gz
            |-- 0005_01_BOLD_EPI_29mm_2sec.nii.gz
            |-- 0006_01_BOLD_EPI_29mm_2sec.nii.gz
            |-- 0007_01_BOLD_EPI_29mm_2sec.nii.gz
            |-- 0008_01_BOLD_EPI_29mm_2sec.nii.gz
            |-- 0009_01_T1w_9mm_BRAVO.nii.gz  
            
BIDS Data Format
|-- Project Filename
    |-- BIDS_data
        |-- participants.tsv
        |-- task-empathy_bold.json
        |-- dataset_description.json
        |-- sub-101
            |-- anat
                |-- sub-101_T1w.nii.gz
            |-- func
                |-- sub-101_task-empathy_run-01_bold.nii.gz
                |-- sub-101_task-empathy_run-02_bold.nii.gz
                |-- sub-101_task-empathy_run-03_bold.nii.gz
                |-- sub-101_task-empathy_run-04_bold.nii.gz
```


## File Requirements
* NIMS_data (directory)
    - {participant 1}
    - {participant 2}
    - ...
* NIMS_participants.csv
* NIMS_protocol.csv

## CSV requirements

NIMS_participants.csv: 
  * **nims_id** (the data and a 5 digit id number)
  * **participant_id** (just numbers, no "sub-" is needed for subject number)
  * optional: sex
  * optional: age
    
NIMS_protocol.csv:
  * **NIMS_scan_title**
        - do not include ####\_##\_ proceeding the scan title
        - *ex: 3Plane_Loc_fgre, BOLD_EPI_29mm_2sec, T1w_9mm_BRAVO*
  * **BIDS_scan_title** 
        - follow the bids naming convention on the website
        - *ex: T1w, task-{taskname}*
  * **full_task_name** 
        - taskname will be included in json description file
        - *ex: "balloon analog risk task"*
  * **image_type**
        - "anat" or "func" if anatomical or functional
  * **run_number** 
        - if functional image with > 1 run
  * **repetition_time**
        - if functional
 
## Running NIMStoBIDS
**python NIMStoBIDS.py {project/filepath}**

The script will:
  * check to see if all your participant folders are in NIMS_data
  * check to see if your scans match your protocol
  * create BIDS_data file, renaming volume files and creating .json and .tsv files
 
Error Handling: 
* If you have more scans than listed in your protocol, you will get an error message. Renaming the unneeded file so that it no longer matches with naming pattern in NIMS_scan_title will ignore the file.
        - ex: BOLD_EPI_29mm_2sec -> BOLD_*ignore*_EPI_29mm_2sec
  