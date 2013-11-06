#!/usr/bin/env python
# encoding: utf-8
"""
Metazoom is a little ncurses-based visualizer of genome-scale metabolic models.

Nicolas Loira
nloira@gmail.com
2013
"""

import sys,os
import getopt
import curses
import time

import basicSBML



def usage():
	"""Shows usage instructions"""
	print "Usage "+sys.argv[0]+ " [-h] [-c currency_file] SBMLfile.xml \n \
		-h/--help: print this message \n \
		-c: defines a file with a list of species indentifiers used as currency metabolites\n \
		(type '?' in metazoom to list available command)"


def main():

	# parse arguments
	try: opts, args = getopt.getopt(sys.argv[1:], "hc:", ["help"])
	except getopt.GetoptError:
		usage()
		sys.exit(2)

	currency_file = None

	for o,a in opts:
		if o in ("-h","--help"):
			usage()
			sys.exit()

		if o=="-c": currency_file=a

	if len(args)!=1:
		usage()
		sys.exit(2)

	# loading SBML model
	SBMLfile = args[0]
	print "Parsing "+SBMLfile+" ..."
	model=basicSBML.SBMLmodel(SBMLfile)

	print "Imported %d reactions" % len(model.reactions)
	print "Imported %d species" % len(model.species)
	print "Imported %d compartments" % len(model.compartments)

	# boot TUI
	print "\nStarting TUI..."
	curses.wrapper(mainTUI, model)

	# closing up
	print "Shutting down metazoom..."


###############################################################

def mainTUI(*args, **kwds):
	# just wait for a while

	mainw, model=args

	# setup curses
	curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
	curses.curs_set(0) # invisible cursor

	(my,mx) = mainw.getmaxyx()
	mainw.nodelay(0) # wait for user input

	# some feedback
	mainw.addstr(5,2, str(len(model.reactions)), curses.color_pair(1))
	
	# Main loop

	while True:
		# get command
		key=mainw.getch()
		keyname=curses.keyname(key)

		# prepare new screen
		mainw.erase()

		# execute command
		mainw.addstr(5,2, keyname)

		# update screen
		mainw.noutrefresh()
		curses.doupdate()


###############################################################

if __name__ == "__main__":
    main()
