# Bioportal Ontology Selector
BOS is a Python script tool that uses the Bioportal API to find either one or a combination of multiple ontologies that are most suitable to annotate a semi-structured biological dataset. It relies on a set of functions and a .json setup file detailing which data, ontologies, and parameters are to be tested or evaluated. It can output a comprehensive report on all obtained annotations, a performance summary of the best annotating ontologies, and an optional barchart of annotated terms per ontology.

### BOS.py
The script itself can be extracted and used as a runnable through CLI. It requires installation of the python modules: matplotlib, pandas, itertools, progressbar, and requests. It only takes as input the Configurations.json file. 

###  Configurations.json
Used to setup custom ontology selection parameters, by filling in the following variables:

- __apikey -__ A valid Bioportal user API key
- __path to data -__ Path to the target data csv
- __single report path -__ Path to save annotation report and single ontology annotation barchart
- __multiple report path -__ Path to save multiple ontology report and annotation barcharts
- __test all ontologies -__ True if using all Bioportal ontologies, false if using specific ontologies (see below)
- __ontologies -__ Select specific ontologies to annotate data (optional)
- __plot data -__ True to generate barcharts of annotation results
- __synonyms -__ True if allowing for annotations from synonyms
- __test multiple ontologies -__ True if selecting combinations of multiple ontologies
- __ontologies to select -__ How many top performing ontologies are selected for multiple ontology evaluation
- __combinations -__ Combinations of how many multiple ontologies

###  Test Data
We provide in the repository two .csv data files detailing patient symptomatic and disease data. Both are adapted from a dataset taken from https://github.com/yaleemmlc/admissionprediction. The setup file offers a preset test run that can be completed by adding the users's Bioportal API key and the full directories.

###  Running through CLI
After setting up configurations, type the command:
```
BOS.py Configurations.json
```
