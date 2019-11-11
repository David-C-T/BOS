# Bioportal Ontology Selector
BOS is a Python script that uses the Bioportal Annotator software to find either one or a combination of multiple ontologies that are most suitable to annotate a semi-structured biological dataset. It relies on a set of functions and a json configuration file detailing which data, ontologies, and parameters are to be tested and evaluated. It can output a comprehensive report on all obtained annotations, a performance summary of the best annotating ontologies, and an optional barchart of annotated terms per ontology.

##  Configurations.json
Set ontology selection parameters according to necessity:
- __path to data -__ Path to the target data csv
- __plot data -__ True to generate barcharts of annotation results
- __test all ontologies -__ True if using all Bioportal ontologies, false if using specific ontologies
- __ontologies -__ Select specific ontologies to annotate data (optional)
- __apikey -__ A valid Bioportal user API key
- __synonyms -__ True if allowing for annotations from synonyms
- __test multiple ontologies -__ True if selecting combinations of multiple ontologies
- __combinations -__ Combinations of how many multiple ontologies
- __ontologies to select -__ How many top performing ontologies are selected for multiple ontology evaluation
- __single report path -__ Path to save annotation report and single ontology annotation barchart
- __multiple report path -__ Path to save multiple ontology report and annotation barcharts

##  Running through CLI
After setting up configurations, type the command:
```
BOS.py Configuration.json
```
