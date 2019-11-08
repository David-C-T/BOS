import pandas as p
from urllib import parse
import requests
import sys
import re
import progressbar
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from itertools import combinations
import json
plt.rcParams.update({'figure.max_open_warning': 0})

Settings_Path = sys.argv[1]


def GetTable(Report):

    #Get Relevant columns, drop duplicates since only the term matters, group by number of annotated terms per ontology and completeness
    Ontology_Annotations = Report[['Ontology','Completeness','Term']].drop_duplicates().groupby(['Ontology','Completeness']).size().reset_index()
    Barplot_Table = Ontology_Annotations.pivot(index = 'Ontology', columns = 'Completeness')
    Barplot_Table.columns = Barplot_Table.columns.droplevel(0)

    #Order Columns
    column_order = ['Singleword', 'Multiword', 'Complete']
    Barplot_Table = Barplot_Table.reindex(column_order, axis = 1)

    return Barplot_Table

def PlotAnnotation(Barplot_Table,Path):
    

    #Make Stacked Bar Plot
    ax = Barplot_Table.plot.bar(stacked=True,title='Annotated Terms by Ontology', width=0.7,cmap=LinearSegmentedColormap.from_list('mycmap', ["#2B7BBA", "#82BBDB","#CEE0F2"]))
    for p in ax.patches:
        width, height = p.get_width(), p.get_height()
        if height == 0: 
            continue
        x, y = p.get_xy() 
        ax.text(x + width/2, y + height/2, '{:.0f}'.format(height), horizontalalignment='center', verticalalignment='center', size=10)
    
    plt.ylabel('Annotation Count', labelpad=7) 
    plt.xticks(rotation='horizontal')
    plt.xlabel("")

    chartBox = ax.get_position()
    ax.set_position([chartBox.x0, chartBox.y0, chartBox.width*0.7, chartBox.height])
    legend = ax.legend(loc = 'upper center', bbox_to_anchor = (1.3, 0.8), shadow = False, ncol = 1,frameon = False,title = "Completeness")#
    legend._legend_box.align = "left"

    plt.savefig(Path)

def MultiOnto(Ontologies,Report,Combs,Multiple_Report_Path):

    #Ontology Combinations  
    Combinations = [list(map(str, comb)) for comb in combinations(Ontologies.split(','), Combs)]

    #Get a filtered Report with noncommon elements between ontologies
    Group_Results = []
    for group in Combinations:
        SubReport = Report.loc[(Report['Ontology'].isin(group))][['Ontology','Completeness','Term']].drop_duplicates()
        for x in range(0,len(group)-1):
            Ontology = group[x]

            #Filter Complete from other ontologies
            Complete = list(set(SubReport.loc[(SubReport['Ontology'] == Ontology) & (SubReport['Completeness'] =='Complete')]['Term'].tolist()))
            SubReport = SubReport.drop(SubReport[(SubReport['Term'].isin(Complete)) & (SubReport['Ontology'] != Ontology) & (SubReport['Completeness'] == 'Multiword')].index)

            #Filter Multiword from other ontologies
            Multiword = list(set(SubReport.loc[(SubReport['Ontology'] == Ontology) & (SubReport['Completeness'] =='Multiword')]['Term'].tolist()))
            SubReport = SubReport.drop(SubReport[(SubReport['Term'].isin(Multiword)) & (SubReport['Ontology'] != Ontology) & (SubReport['Completeness'] == 'Multiword')].index)

            #Filter Singleword from other ontologies
            Singleword = list(set(SubReport.loc[(SubReport['Ontology'] == Ontology) & (SubReport['Completeness'] =='Singleword')]['Term'].tolist()))
            SubReport = SubReport.drop(SubReport[(SubReport['Term'].isin(Singleword)) & (SubReport['Ontology'] != Ontology) & (SubReport['Completeness']=='Multiword')].index)

        #Plot SubReports      
        Table = GetTable(SubReport) 
        Path = 'C:\\Users\\david\\Desktop\\Multiple_Matches' + '\\' + '_'.join(group) + '.png'
        PlotAnnotation(Table,Path)

        #Get all annotations and make a result file
        Target = SubReport['Completeness'].tolist()
        Group_Results.append([' + '.join(group),Target.count("Complete"),Target.count("Multiword"),Target.count("Singleword")])

    #Compile
    Multiple_Report = p.DataFrame(Group_Results, columns=["Ontologies","Complete","Multiword","Singleword"])
    Multiple_Report.sort_values(["Complete","Multiword","Singleword"], ascending=[False, False,False], inplace=True)
    A = list(Multiple_Report["Ontologies"].loc[(Multiple_Report['Complete'] == Multiple_Report["Complete"].iloc[0])])#Select highest number of completes

    conclusion = 'Best '+ str(Combs) + ' annotating ontologies (with ' +  str(Multiple_Report["Complete"].iloc[0])  + ' complete annotations):\n > ' + '\n > '.join(A)
    print(conclusion)

    #Export
    Path=Multiple_Report_Path + '\\Multiple ('+ str(Combs)+') Ontologies Report.csv'
    Multiple_Report.to_csv(Path)
    output = 'Generated a report at: ' +  Path.replace('\\','/')
    print(output)

def Annotator(Ontologies,Terms,API_KEY,Synonyms):

    #Get Parameters
    site = 'http://data.bioontology.org/annotator?'
    parms = '&format=json&include=prefLabel&exclude_synonyms='
    ontologies = str('&ontologies=' + Ontologies)

    #Progress Bar
    bar = progressbar.ProgressBar(maxval=len(Terms), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    Term_Annotations = []
    for term in Terms:
        bar.update(Terms.index(term))

        #Use Bioportal API Annotator
        text = '&text=' +  str(parse.quote(term))    
        URL = site + API_KEY + ontologies + parms + Synonyms + text
        data = requests.get(URL)

        if data.status_code == 200:
            Results = data.json()

            if Results == []:
                continue
            for Annotation in Results:

                #Get Annotation Information
                IRI = Annotation['annotatedClass']["@id"]
                UsedOntology = Annotation['annotatedClass']['links']['ontology'].replace('http://data.bioontology.org/ontologies/','')
                Label = Annotation["annotations"][0]['text']
                Synonym = Annotation['annotations'][0]['matchType']
                
                #Get Annotation Completeness
                term = term.lower()
                Label = Label.lower()
                if term == Label:
                    Completeness = 'Complete'
                elif Label in term:
                    if len(Label.split(' '))>1:
                        Completeness = 'Multiword'
                    else:
                        Completeness = 'Singleword'
                
                Term_Annotations.append([Label,term,Completeness,UsedOntology,IRI,Synonym])
    
    bar.finish()
    return Term_Annotations

def Select_Ontologies(Path_to_Data,Ontologies,Synonyms,MultipleOntologies,MakePlots,Comb,API_KEY,Single_Report_Path,Multiple_Report_Path):

    #Load and Clean Files
    print('\nLoading Data...')
    try:
        TargetData = p.read_csv(Path_to_Data,sep=',',index_col=[0],header=[0],encoding="ISO-8859-1",error_bad_lines=False)
    except Exception:
        print('Something is wrong with the file:')
        print(str(Exception))

    TargetData = TargetData.fillna('')

    #Get unique terms from a DataFrame
    Terms = set(sum([TargetData[x].unique().tolist() for x in TargetData.columns.values],[]))
    Terms = [x.strip() for x in list(Terms) if not isinstance(x, (float,int))]#remove numbers and trim spaces
    Terms = Terms[:15]


    #Annotate
    print('Annotating...')
    Term_Annotations = Annotator(Ontologies,Terms,API_KEY,Synonyms)

    #Write Report    
    Columns = ['Match','Term','Completeness','Ontology','IRI','Synonym']
    Report = p.DataFrame(Term_Annotations,columns=Columns)
    Report_Path = Single_Report_Path + "\\RESULTS.csv"
    Report.to_csv(Report_Path)
    output = 'Generated a report at: ' +  Report_Path.replace('\\','/')
    print(output)
    
    #Get bartable and find best annotating ontology
    Barplot_Table = GetTable(Report)
    
    A = '\n > '.join(Barplot_Table[Barplot_Table['Complete'] == Barplot_Table['Complete'].max()].to_records()['Ontology'])#Best Ontology
    conclusion = 'Complete annotations were maximized by:\n > ' +  A + ' ('+str(int(Barplot_Table['Complete'].max()))+' complete annotations)'
    print(conclusion)

    #Plot Barplot
    if MakePlots:
        Path = Single_Report_Path + '\\Figure.png'
        PlotAnnotation(Barplot_Table,Path)

    if MultipleOntologies:
        print('\nTesting multiple ontologies...\n')
        for sets in Comb:
            MultiOnto(Ontologies,Report,sets,Multiple_Report_Path)
    
    print('\nFinished!')



if __name__ == '__main__':
   
    with open(Settings_Path) as data:
        Settings = json.loads(data.read())
        data.close()
    Path_to_Data = Settings['Path to Data']
    Ontologies = Settings['Ontologies']

    Synonyms=Settings['Synonyms']
    if Synonyms:
        Synonyms = 'true'
    else:
        Synonyms = 'false'

    MultipleOntologies = Settings['MultipleOntologies']
    MakePlots = Settings['Plot Data']
    Comb = Settings['Comb']
    API_KEY = Settings['API_KEY']
    Single_Report_Path = Settings['Single_Report_Path']
    Multiple_Report_Path = Settings["Multiple_Report_Path"]


    Select_Ontologies(Path_to_Data,Ontologies,Synonyms,MultipleOntologies,MakePlots,Comb,API_KEY,Single_Report_Path,Multiple_Report_Path)
    