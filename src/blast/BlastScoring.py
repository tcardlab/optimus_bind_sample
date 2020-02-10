'''
Last Updated: 02/10/2020 (mm/dd/yyyy)

Description:
    Functions which generate a database to plug into the machine
    learning framework (Needs to be expanded)

Contact: sangyoung123@googlemail.com
'''

import sys
import os
from os import listdir
from os.path import isfile, join
import glob
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import re

# Subprocess modules to make,move, and delete files and directories via shell

import subprocess
from subprocess import call

# Scipy Stack

import numpy as np
import pandas as pd
import scipy
import seaborn as sns
import matplotlib.pyplot as plt

# tqdm

import tqdm as tqdm 

# XML Parser

import xml.etree.ElementTree as ET

try:
    from tqdm import tqdm
    return tqdm(some_iter)
except ModuleNotFoundError:
    return some_iter

#|---------
#|Psi-Blast
#|---------
#|
#|Basic Local Alignment Search Tool (BLAST) is a sequence similarity search program
#|used to compare a user's query to a database of sequences.  Given a DNA
#|or amino acid sequence, the BLAST heuristic algorithm finds short matches 
#|between two sequences and attempts to start alignments from these "hot spots". 
#|BLAST also provides statistical information about an alignment such as the "expectation"
#|value. Note that BLAST is not a single program, but a family of programs. 
#|
#|All BLAST programs search for match between sequences, but there is a specialized 
#|BLAST program for each type of sequence search. BLAST is one of the most widely used 
#|bioinformatics research tools,  since it has several applications, here is a list of typical 
#|BLAST applications.
#|
#|1. Following the discovery of a previously unknown gene in one species, search other genomes 
#|   to see if other species carry a similar gene.
#|
#|2. Finding functinoal and evolutionary relationships between sequences
#|
#|3 Search for consensus regulatory patterns such as promoter signals, splicing sites and transcription
#|  factor binding sites
#|
#|4. Infer protein structure based on previously crystallized proteins
#|
#|5. Help identify members of gene families
#|
#|If you work in bioinformatics, chances are that you will need to run some BLAST queries or face the need to process BLAST queries
#|generated by you or by another person. Biopython proves tools for both tasks.
#|
#|----
#|
#|Blast and its variants searches protein and nucleic acid sequences using the BLAST or FASTA method. Both methods 
#|find similar protein or nucleic aicd chains inthe PDB. psi-blast is used to find more distantly related seuqences
#|
#|Sequences can be search in two ways
#|
#|- By PDB ID and Chain ID. Type in a PDB in the structure ID text box and select a chain ID from the pull-down menu. This is useful
#|  to find all sequences that are similar to the sequence from the specified chain.


def psiBlastScoring(PATH, PSIBLASTPATHBIN ='/home/oohnohnoh1/Desktop/ACADEMIA/Papermaking/OPTIMUS_BIND/ncbi-blast-2.9.0+/bin/psiblast'):

	"""
	Biopython has a wrapper for each BLAST executable, so you can run a blast program from inside your 
	script. The wrapper for blastn 
	
	NcbiblastnCommandline(blast executable, program name, database, input file, ) .. 

	This function returns a tuple with two file objects. The first one is the actual result 
	the second one is the blast error message.

	The output is in XML format. This information can be parsed using the tools learned or with 
	the tools provided by Biopython. There is also a way to avoid dealing with the XML 
	output by forcing NCbiblastncommandline to use plain text as output. This is done by using 
		
	 ---------------------------------------------------------------
	| Links for resources I have been looking at to make this code: |
	 ---------------------------------------------------------------

	-> https://www.rcsb.org/pages/help/advancedsearch/sequence

	-> https://www.biostars.org/p/10419/

	-> https://biopython.org/DIST/docs/api/Bio.PDB.Polypeptide-module.html

	-> https://www.ncbi.nlm.nih.gov/books/NBK2590/ - Good Psiblast explanation

	--------------------------------------------------------------

	------------------------------
	JB's instructions on psi-blast
	------------------------------

	1. We find all similar interfaces.
	
	2. Make a MSA of structurally aligned sequences (multiple sequence alignment). 

	3. Form a score from the probability of a particular mutation showing up in the 
	   MSA. 

	4. Evaluate the mutation with this score  - This is where we need the mutation.

	---------------------------------------------    
	| What to extract from each PSIBLAST record |
	---------------------------------------------

	Information required to build the blast tables according to  JB 
	
	1. The aligned sequences.

	2. the statistics for the alignment <Statistics set>.

	3. The species name for each.

	4. Hsp_evalue.

	Notes:
	------

	-> Should not require an HPC to run each blast computation

	-> The ialign work is run on the biowulf cluster in the NIH, from what I know

	Some biopython options for blast:
	---------------------------------------------------------
	blastn -> nucleotide vs nucleotide
	blastp -> protein vs protein 
	blastx -> translated nucleotide vs protein
	tblastn -> protein vs translcated nucleotide
	tblastx -> translated nucelotide vs translated nucleotide
	---------------------------------------------------------
	Parameters
	----------
	PATH: 
      Path to where the wild type PDBs are found 
	PSIBLASTPATH:
	  Path to where the psiblast binary is 
	"""
	try:
		from Bio import AlignIO
		from Bio.PDB.PDBIO import PDBIO
		from Bio.PDB.PDBParser import PDBParser 
		from Bio.Data.IUPACData import protein_letters
		from Bio.SeqUtils.ProtParam import ProteinAnalysis
		from Bio.PDB.Polypeptide import PPBuilder  
		from Bio.PDB.Polypeptide import standard_aa_names 
		from Bio.PDB.Polypeptide import aa1 #  aa1 = 'ACDEFGHIKLMNPQRSTVWY'
		from Bio.PDB.Polypeptide import aa3 #  aa3 = ['ALA', 'CYS', 'ASP', 'GLU', 'PHE', 'GLY', 'HIS', 'ILE',... ]
		from Bio.Blast.Applications import NcbipsiblastCommandline as psiblastn  # psiblast reader
		from Bio.Blast import NCBIXML # For reading the BLAST output 
		from Bio.Seq import Seq
		from Bio.Seq import translate, transcribe, back_transcribe
		from Bio.PDB.Polypeptide import PPBuilder
		from Bio.Alphabet import IUPAC
		from Bio.Align import MultipleSeqAlignment
		from Bio.SeqRecord import SeqRecord
		from Bio.Alphabet import generic_protein
		import pandas as pd
		from pandas import DataFrame
		import tqdm
		from tqdm import tqdm
	except ImportError:
		print ("Error - cannot imoort BLAST python modules")	
	# psiblast executable (bin) 
	BLASTEXE = PSIBLASTPATHBIN
	WTArray = []
	nameArray = []
	FoldxPath = "/home/oohnohnoh1/Desktop/ACADEMIA/Papermaking/OPTIMUS_BIND/FoldX/foldx"
	TotalDict = {} # Dictionary to store each vlaue 
	FULL = [] # List to append to in the end which we will convert into a pandas table 
	for file in tqdm(os.listdir(PATH)): # List the fxout files in the directory, and store them in the array 
		if file.endswith(".pdb"):
			if file[0] == '.':
				pass
			else:
				FileLocation = os.path.join(PATH, file)
				WTArray.append(FileLocation) # Array with the appended path and the pdb file
				Parser = PDBParser(PERMISSIVE=1)
				strandName = file.split('.')
				structure = Parser.get_structure(str(strandName[0]), FileLocation)
				model = structure[0] # PDB loader 
				ppb = PPBuilder()  # PDB builder 
				hspNumList = [] 
				subprocess.Popen("mkdir {}_fasta".format(strandName[0]), shell = True) # Make a directory to store the fasta files and the xml files				
				# General top-down explanation for this loop - TODO 
				
				for index, pp in enumerate(ppb.build_peptides(structure)):
					try:
						sequenceCreator = SeqRecord(Seq(str(pp.get_sequence()), generic_protein), id = str(model.get_list()[index].id))
						align = MultipleSeqAlignment([sequenceCreator])
						pdbName = "{}_{}".format(strandName[0], str(model.get_list()[index].id))
						AlignIO.write(align,'{}_{}.fasta'.format(strandName[0], str(model.get_list()[index].id)), 'fasta')
						HspStatistics = ['Hsp_evalue', 'Hsp_qseq', 'Hsp_hseq'] # xml tabs for Hsp 
						blastStatistics = ['Statistics_db-num', 'Statistics_db-len', 'Statistics_hsp-len', 'Statistics_eff-space', 'Statistics_kappa', 'Statistics_lambda', 'Statistics_entropy'] # xml tabs for statistics
						subprocess.Popen("mv {}_{}.fasta {}_fasta/.".format(strandName[0], str(model.get_list()[index].id), strandName[0]), shell = True)
						# Call psiblast on the generated fasta files
						psiblastnCline = psiblastn(cmd = BLASTEXE, query = '{}_fasta/{}_{}.fasta'.format(strandName[0], strandName[0], str(model.get_list()[index].id)), db = "/home/oohnohnoh1/Desktop/ACADEMIA/Papermaking/OPTIMUS_BIND/PANDAS_TABLE/db/cdd_delta", evalue = .0005, outfmt=5, out="{}_fasta/{}_{}.xml".format(strandName[0], strandName[0], str(model.get_list()[index].id) ))

						rh,eh = psiblastnCline()
						tree = ET.parse('{}_fasta/{}_{}.xml'.format(strandName[0], strandName[0], str(model.get_list()[index].id))) # READ XML file
						root = tree.getroot() # 
						uniqueHIT = 0  # Default index 
						strandInformation = [] 
						TotalDict[pdbName] = []
						for ind in root.iter(): # Append all hsp_num values 
							if ind.tag == 'Hit_num':
								uniqueHIT = ind.text
							for stat in HspStatistics:
								if ind.tag == stat:
									strandInformation.append([strandName[0], uniqueHIT, str(model.get_list()[index].id), ind.tag, ind.text])
							for stat in blastStatistics:
								if ind.tag == stat:
									strandInformation.append([strandName[0], uniqueHIT, str(model.get_list()[index].id), ind.tag, ind.text])
						TotalDict[pdbName] = strandInformation # Store list into the 
						# Get a set of the indices of the HIT and use to loop over each Hsp set of values 
						numList = [int(row[1]) for row in TotalDict[pdbName]]
						numList = list(set(numList))
						numList.sort()
						if len(numList) == 0: # I havent made the code to deal with 
							#D_1 = [row[4] for row in TotalDict[NAME] if row[3] in blastStatistics]
							#D_1.insert(0, "{}_{}".format(strandName[0], str(model.get_list()[index].id)))
							#print (D_1)
							#FULL.append(D_1)
							print ("Placeholder")
						else:
							for hitIndex in numList:
								pdRow = []
								if hitIndex == 0: # 0 is micelleneous part in the xml file - ignore
									print ("Ignoring the top of the xml output of psiblast...")
									pass
								else:
									for row in TotalDict[pdbName]:
										if int(row[1]) == hitIndex: # Find the Hsp depending on specific Hit 
											for stat in HspStatistics:
												if row[3] == stat: # If the xml matches the Hsp statistics tags, we append
													pdRow.append(row[4])
											for stat in blastStatistics:
												if row[3] == stat: # If the xml matches the Hsp statistics tags, we append
													pdRow.append(row[4])
								pdRow.insert(0,hitIndex)
								pdRow.insert(0, "{}_{}".format(strandName[0], str(model.get_list()[index].id)))
								if len(pdRow) == 12: # There is an issue that some have multiple hits.. so will									              # have more then 5 for the length, so need to take that into account 
									FULL.append(pdRow)
					except IndexError:
						print ("Error for {}!".format(file))
	subprocess.Popen("rm -r *_fasta", shell = True) # Remove all the files that was formed in the psiblast analysis
	df = pd.DataFrame(FULL, columns = ['PDB_res', 'Index', 'Hsp_evalue', 'Hsp_qseq', 'Hsp_hseq','Statistics_db-num', 'Statistics_db-len', 'Statistics_hsp-len', 'Statistics_eff-space', 'Statistics_kappa', 'Statistics_lambda', 'Statistics_entropy'])  # Column names for the pandas table
	df.to_csv("psiblastData.csv", sep = ',')
	return df

