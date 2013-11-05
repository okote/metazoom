#!/usr/bin/env python
# encoding: utf-8
"""
pathtastictoolbox.py

Created by Nicolas Loira on 2010-12-18.
Copyright (c) 2010 LaBRI, Univ.Bordeaux I, France. All rights reserved.
"""

import sys
import os
from xml.etree.ElementTree import *
from collections import defaultdict
# import re

def log(m):
	print >>sys.stderr, m


class SBMLmodel():
	def __init__(self, filename=None):

		if filename:
			self.parseXML(filename)
			
		self.toRemove=None	
		self.lockedReactions=[]

	def parseXML(self, modelFile):
		assert modelFile
		
		if modelFile=="-":
			modelfd=sys.stdin
		else:
			modelfd=open(modelFile)

		# parse file
		result = parse(modelfd)
		root=result.getroot()
		self.xmlTree=result
		self.root=root
		self.URI,self.tag= root.tag[1:].split("}",1)
		assert self.URI, "URI was not set correctly."

		# shortcut for list of reaction nodes
		self.reacNodes = root.findall("*/{%s}listOfReactions/{%s}reaction" % (self.URI,self.URI))
		self.speciesNodes=root.findall("*/{%s}listOfSpecies/{%s}species" % (self.URI, self.URI))
		self.compNodes=root.findall("*/{%s}listOfCompartments/{%s}compartment" % (self.URI, self.URI))


		for r in self.reacNodes:
			speciesInReaction=set()
			speciesInReaction.update([sr.get('species') for sr in r.findall("{%s}listOfReactants/{%s}speciesReference" % (self.URI, self.URI))  ])
			speciesInReaction.update([sr.get('species') for sr in r.findall("{%s}listOfProducts/{%s}speciesReference" % (self.URI, self.URI))  ])
			speciesInReaction.update([sr.get('species') for sr in r.findall("{%s}listOfModifiers/{%s}modifierSpeciesReference" % (self.URI, self.URI))  ])

		
		# map of all parents (useful for removing nodes)
		self.parentMap = dict((c, p) for p in root.getiterator() for c in p)

	def write(self, outFD):
		#self.xmlTree.write(outFD)

		# COBRA doesn't like the extra namespaces added by ElementTree,
		# so we'll parse the output
		assert self.root is not None
		xmlstr=tostring(self.root)
		
		cleanxml=xmlstr		
		#cleanxml=re.sub("<ns\d+:", "<", xmlstr)
		# cleanxml=re.sub("</ns\d+:", "</", cleanxml)
		
		
		print '<?xml version="1.0" encoding="UTF-8"?>'
		print cleanxml
	


	def getGeneAssociations(self, reset=False):
		
		if not reset and hasattr(self, 'r2formula'):
			return self.r2loci,self.r2formula
			
		assert self.root is not None and self.URI is not None
		
		r2loci=dict()
		r2formula=dict()
		r2formulaNode=dict()
		rid2node=dict()
		
		# look for reactions

		for r in self.reacNodes:
			reacId = r.get('id','INVALID')
			rid2node[reacId]=r
			notes  = r.find("{%s}notes" %(self.URI))	
			geneFormula=None

			body=notes.find("{http://www.w3.org/1999/xhtml}body")
			if body is not None:
				notes=body

			
			for line in notes:
				text = line.text
				if text.startswith("GENE ASSOCIATION:") or text.startswith("GENE_ASSOCIATION:"): 
					geneFormula=text[17:].strip()
					lineWithGA=line


			# skip reactions without gene association
			if not geneFormula:
				continue
			r2formula[reacId]=geneFormula
			r2formulaNode[reacId]=lineWithGA
			
			loci=frozenset(geneFormula.replace("(","").replace(")", "").replace("and", "").replace("or", "").split())
			# $loci is now a set of locus for this reactions
			r2loci[reacId]=loci
		
		self.r2loci=r2loci
		self.r2formula=r2formula
		self.r2formulaNode=r2formulaNode
		self.rid2node=rid2node
		
		return r2loci,r2formula
		
	def getGAGroup(self, excludeLocked=False):
		"""generate a GAGroup object with the existing GeneAssociations"""
		r2loci,r2formula = self.getGeneAssociations()
		
		ridWithFormula=r2formula.keys()
		reactionsWithFormula = [r for r in self.reacNodes if r.get('id') in ridWithFormula]
		
		if excludeLocked:
			reactionsWithFormula = [r for r in reactionsWithFormula if r not in self.lockedReactions]
		
		GAs=GAGroup()
		for reac in reactionsWithFormula:
			ga=GeneAssociation(reac, self)
			GAs.add(ga)
			
		return GAs
			


class GeneAssociation():
	"""Store a gene association"""
	def __init__(self, reactionNode, model):
		# super(GeneAssociation, self).__init__()
		self.reactionNode = reactionNode
		self.rid=reactionNode.get('id','INVALID')
		self.formula=model.r2formula.get(self.rid,None)
		self.loci=model.r2loci.get(self.rid,None)

	def getReactionName(self):
		assert self.reactionNode
		return self.reactionNode.get('name', 'INVALID')

class GAGroup(set):
	"""store a set of gene associations"""
	def __init__(self):
		super(GAGroup, self).__init__()


def main():
	pass

if __name__ == '__main__':
	main()

