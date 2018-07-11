from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

# coding: utf-8

# In[ ]:

from builtins import input
from builtins import open
from builtins import str
from future import standard_library
standard_library.install_aliases()
print("Importing Libraries...\n")

import pandas as pd
import os
import re
from shutil import copyfile
import json
import sys


# In[ ]:

#Get Data Filepath
if (len(sys.argv) == 2):
    project_filepath = str(sys.argv[1]).strip(' ')
else:
    #"Data needs to be in format: \n       Project Filename            \n        /          \\              \n    NIMS_data  BIDS_info.xlsx      \n       /                           \nSub1 Sub2 Sub3                     \n\n                                   \n
    print("NIMS_to_BIDS.py can take the project's file path as an argument\nNo argument detected\nPlease drag in file path from folder")
    project_filepath = input().strip(' ')


#path variables
BIDS= project_filepath + '/BIDS_data/'
NIMS= project_filepath + '/NIMS_data/'


# In[ ]:

#Read files

#Figure out what bids info xlsx is named 
project_file_contents = os.listdir(project_filepath)
BIDS_filename = [x for x in project_file_contents if "BIDS_info" in x]
print(BIDS_filename)

#Make sure there's only one bids file
assert len(BIDS_filename) == 1, 'This folder does not have a BIDS_info file or it has more than one info file' 

xls = pd.ExcelFile(project_filepath + "/" + BIDS_filename[0])

#Make folder if folder doesn't exist function
def makefolder(name):
    if not os.path.exists(name):
        os.makedirs(name)
        
#Log Function


# In[ ]:

#Load and Clean XLS File
participants = xls.parse('participants')
participants.participant_id = participants.participant_id.astype('str')

protocol = xls.parse('protocol', convert_float=False).iloc[1:,:6] #columns 5 on are reference columns
protocol = protocol.dropna(axis=0, thresh=3) #get rid of items that don't have a bids equivalent
protocol.run_number = protocol.run_number.astype('str').str.strip('.0').str.zfill(2) #Convert run int to string


#Create "bold" portion of filename
protocol['bold_filename'] = ''
protocol.loc[protocol['ANAT_or_FUNC'] == 'func', 'bold_filename'] = '_bold'

#Concatanate filepath and clean
protocol["BIDS_scan_title_path"] = BIDS + "sub-###/" + protocol.ANAT_or_FUNC + "/sub-###_" + protocol.BIDS_scan_title + "_run-" + protocol.run_number + protocol.bold_filename + ".nii.gz"
protocol.BIDS_scan_title_path = protocol.BIDS_scan_title_path.str.replace('_run-nan', '') #For items that don't have runs

#Create list for NIMS -> bids conversion
NIMS_protocol_filenames = protocol.NIMS_scan_title.tolist() #Convert protocol scan titles to list
NIMS_BIDS_conversion = protocol[["NIMS_scan_title","BIDS_scan_title_path"]]


# In[ ]:

def check_against_protocol(participants,protocol): 
    
    all_files_correct = True
    
    for index, row in participants.iterrows():

        #If directory is there, try will work
        try:
            #Get all files in participant directory
            NIMS_participant_filenames = os.listdir(NIMS + row.nims_title)
           
            #Delete all non-nii.gz files
            NIMS_participant_filenames = [x for x in NIMS_participant_filenames if ".nii.gz"  in x]

            for item in set(NIMS_protocol_filenames):
                
                directory_filenames = [x for x in NIMS_participant_filenames if item in x]
                protocol_filenames = NIMS_BIDS_conversion[NIMS_BIDS_conversion.NIMS_scan_title.str.contains(item)]
                protocol_filenames = protocol_filenames.iloc[:,1].tolist()

                if len(directory_filenames) < len(protocol_filenames):
                    print('sub-{} : << {} {} files in folder {} files in protocol\n'.                    format(str(row.participant_id), item.rjust(20), len(directory_filenames), len(protocol_filenames)))

                elif len(directory_filenames) > len(protocol_filenames):
                    print('sub-{} : >> {} {} files in folder {} files in protocol\n'.                    format(str(row.participant_id), item.rjust(20), len(directory_filenames), len(protocol_filenames)))
                    all_files_correct = False
                    
                elif len(directory_filenames) == len(protocol_filenames):
                    print('sub-{} : == {} {} files in folder {} files in protocol\n'.                    format(str(row.participant_id), item.rjust(20), len(directory_filenames), len(protocol_filenames)))

            print("------------")
        
        except:
            all_files_correct = False
            print("sub-" + str(row.participant_id) + " : -- ERROR - folder is missing \n------------")

        
        
        
    if all_files_correct:
        print("\nAll your folders match your protocol\n")  
    else:
        print("\nSome folders do not match your protocol, please resolve errors\n")
    
    return all_files_correct


# In[ ]:

def write_text_files(participants, protocol): 
    
    def to_file(filename, content): 
        with open(BIDS + filename + ".json", "w") as text_file:
            text_file.write(content)
    
    #Data Description
    dataset_description = json.dumps({"BIDSVersion": "1.0.0",                                    "License": "",                                    "Name": "dummy task name",                                   "ReferencesAndLinks": ""})
    to_file(str("dataset_description"), str(dataset_description))
    

    #Task Description
    for item in set(protocol.loc[protocol.ANAT_or_FUNC == "func", 'BIDS_scan_title']):
        full_task_name = protocol.loc[protocol.BIDS_scan_title == item, 'full_task_name']
        full_task_name = full_task_name.reset_index(drop=True)[0] #Gets first instance of RT
        
        repetition_time = protocol.loc[protocol.BIDS_scan_title == item, 'repetition_time']
        repetition_time = repetition_time.reset_index(drop=True)[0] #Gets first instance of RT
        task_json = json.dumps({"RepetitionTime": repetition_time, "TaskName" : full_task_name})

        to_file(str(item + "_bold"), str(task_json))

    #TSV
    participant_tsv = participants.loc[:, ['participant_id', 'sex', 'age']]
    participant_tsv.loc[:, 'participant_id'] = "sub-" + participant_tsv.loc[:, 'participant_id'].apply(str)
    #Had to write csv and then change it due to python 2/3 incompatability
    participant_tsv.to_csv(BIDS + 'participants.tsv', index=False)
    # Read in the file
    with open(BIDS + 'participants.tsv', 'r') as file :
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace(',', '\t')

    # Write the file out again
    with open(BIDS + 'participants.tsv', 'w') as file:
        file.write(filedata)
    
    
    


# In[ ]:

def convert_to_bids(participants, protocol):
    
    print("Comparing Folders to Protocol...\n")
    
    if check_against_protocol(participants,protocol): #Function returns true is everything matches
        
        print("Creating BIDS_data folder\n")
        #Make BIDS Folder
        makefolder(BIDS)
        participants.participant_id.apply(lambda x: makefolder(BIDS + 'sub-' + str(x) + "/anat"))
        participants.participant_id.apply(lambda x: makefolder(BIDS + 'sub-' + str(x) + "/func"))
        
        for index, row in participants.iterrows():
            #Get files
            NIMS_participant_filenames = os.listdir(NIMS + row.nims_title)

            #Delete all non-nii.gz files from list
            NIMS_participant_filenames = [x for x in NIMS_participant_filenames if ".nii.gz"  in x]

            for item in set(NIMS_protocol_filenames):
                directory_filenames = [x for x in NIMS_participant_filenames if item in x]
                protocol_filenames = NIMS_BIDS_conversion[NIMS_BIDS_conversion.NIMS_scan_title.str.contains(item)]
                protocol_filenames = protocol_filenames.iloc[:,1].tolist()

                for index, item in enumerate(directory_filenames):
                    oldpath = (NIMS + row.nims_title + "/" + directory_filenames[index])
                    newpath = (protocol_filenames[index].replace("###", str(row.participant_id)))
                    copyfile(oldpath, newpath)

                    print("sub-" + str(row.participant_id) + ": ++ "+ os.path.basename(newpath).rjust(20))
            print("------------")

        print("\nCreating JSON and .tsv Files")
        
        write_text_files(participants, protocol)
       
        print("\nDone!")


# In[ ]:

convert_to_bids(participants, protocol)


# In[ ]:




# In[ ]:



