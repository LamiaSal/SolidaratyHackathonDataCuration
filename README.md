# SolidaratyHackathonDataCuration
data curation project for Solidarity hackathon at MILA institute for Moroccan Earthquake

the objective of the project was to contribute to the improvement of the interactive map https://huggingface.co/spaces/nt3awnou/Nt3awnou-rescue-map.

For that, we focused on 3 main tasks on this repository :
- data cleaning, and analysis of the 3 open sourced forms
- Standardizing data of locations in the forms
- translation darija to english, for the form standardization
- speech to Text, for the people who sen information through whatsapp and not via the forms
- 

## Data cleaning and analysis

data gathering and cleaning of data to target the most urgent request.

code may be found under notebooks/tabular_data_curation/jules.ipynb ad well as src/filter_data.py

## Standardizing data of locations

https://github.com/vict0rsch/morocco-hackathon-gps

## Darija to english 
the code may be found under notebooks/audio_project_Darija2Eng.ipynb

You'll find a code to compare results on sample of data, and code to translate the csv forms.

## Speech-to-text
For the Speech To Text, the idea was to use a pretrained model such as SeamlessM4T and to tune it on a dataset for darija, here Dvoice.

### Dataset used

- Dvoice v2.0 downloaded from : https://zenodo.org/record/6342622

Please Download the dataset v2 into the folder data

### Repository used

- seamlessM4T
Please clone the following repository https://github.com/facebookresearch/seamless_communication.git


## Other
### Datasets :
Biggeer dataset : https://github.com/AIOXLABS/DBert
Other darija datasets: https://github.com/nainiayoub/moroccan-darija-datasets
Darija Bert: https://github.com/AIOXLABS/DBert/blob/main/Data/MTCD.csv
