#!/usr/bin/env python
from __future__ import with_statement
from datetime import datetime

"""
This is a cool script to check lab attendance at Georgia Tech by comparing a roster dictionary to the collected 
buzzcard numbers collected from a given lab. A roster from the class is required for this script.
"""

__author__ = "Marie Weeks"
__version__ = "1.1"

import os
import sys
import csv
import argparse


def main():
	parser = argparse.ArgumentParser(description=('Script to check Lab attendance. ' 
		'Returns two csv files: Attendance.csv with all students and Attendance_Missing.csv with only the absent students.'))
	parser.add_argument('buzzCards', help='csv list of GTIDs from buzz cards collected.')
	parser.add_argument('classRoster', help='csv of full class roster.')
	parser.add_argument('-i', '--index', help='column index of gtids for buzzCards.csv. (Default is 0)', nargs='?', type=int, const=0, default=0)
	parser.add_argument('-r', '--recRoster', help=' semicolon delimited csv list of students in recitation section to check. '
		'Use if checking only a recitation at a time.')
	parser.add_argument('-f', '--fix', help='csv with names to replace (for roster check). '
	 	'Use if you have a Confidential student.')
	parser.add_argument('-d', '--date', help='Add date to returned filenames. (Default is current date)', 
		metavar= 'mm-dd-yy', nargs='?', const=datetime.now().strftime('%m-%d-%y'))

	if len(sys.argv) == 1 :
		parser.print_help()
		sys.exit(1)

	args = parser.parse_args()

	print "Performing setup"

	ids = args.buzzCards
	classCsv = args.classRoster
	recCsv = args.recRoster
	i = args.index
	repCsv = args.fix
	recity = []
	datey = args.date

	classy = makeDict(classCsv)
	students = classy.values()
	buzzy = makeList(ids, i)

	if args.recRoster :
		recity = makeList(recCsv, 0, ';')

	print "Building attendance list from buzzcards"
	attendance = [classy[key].upper() if key in classy else printError("--> !!! ERROR: Buzzcard [" + key + "] not in class roster !!!") for key in buzzy]

	print "Creating final attendance csv"
	if args.fix :
		replace = makeDict(repCsv, ';', False)
		invert = {v:k for k,v in replace.items()}
		makeFinal(attendance, students, datey, recity, replace, invert)
	else :
		makeFinal(attendance, students, datey, recity)

	print "Done."



def makeDict(csvfile, dlimit=',', roster=True) :
	"""Create dictionary of gtids to student names from class roster.

	Reads through csv file, adding the current GTID student name pair to the dictionary. When 
	finished, returns the dictionary.

	Args:
		csvfile: csv file of current class roster (contains GTIDs for every student)

	Returns:
		A dictionary of GTIDs to student names.
	"""

	print "----> Making dictionary from: " + csvfile
	with open(csvfile, 'rb') as f:
		reader = csv.reader(f, delimiter=dlimit)
		if roster :
			rosterDict = {rows[0]:(rows[1] + ", " + rows[2]) for rows in reader}
		else :
			rosterDict = {rows[0]:rows[1] for rows in reader}

	return rosterDict


def makeList(csvfile, index=0, dlimit=',') :
	"""Creates list from given csv file

	Reads through the csv file and creates a list out every value in the first column.

	Args:
		csvfile: csv file with single column of data to be transformed into list

	Returns:
		A list of all values from column one of the input csv file
	"""

	print "----> Making list from: " + csvfile
	with open(csvfile, 'rb') as f:
		reader = csv.reader(f, delimiter=dlimit)
		listy = [rows[index] for rows in reader]

	return listy


def makeFinal(attendance, roster, date, recitation={}, replace={}, invert={}, dlimit=';') :
	"""Makes new csv file marking which students came to the timed lab.

	Goes through each student in the recitation list, writing each name to a new csv file. 
	If the student's name is found within the attendance list, their name is added with an 
	'x' in the following column. Else, the next column is empty for that student's row. If
	n is not input, resulting file will be named "TLAttendance.csv". If n is input, the value
	of n will be appended to the filename following "TL". Delimiter used for this csv is a
	semicolon since all student names contain a comma.

	Args:
		attendance: list of students who attended the timed lab 
		recitation: list of students in that particular recitation section
		n: number of current timed lab

	"""

	if date :
		fname = 'Attendance_' + date + '.csv'
	else :
		fname = 'Attendance.csv'

	with open (fname, 'w') as f :
		writer = csv.writer(f, delimiter=dlimit)
		row = ['STUDENT', 'PRESENT']
		writer.writerow(row)

		if recitation :
			students = recitation
		else :
			students = roster

		missing = []
		for name in students :

			if name in replace :
				name = replace[name]
				replaced = True
			else :
				replaced = False

			if name.upper() in attendance :

				if replaced :
					name = invert[name]
				row = [name, 'x']

			else : 
				if replaced :
					name = invert[name]
				row = [name]
				missing.append(name)

			writer.writerow(row)

	print "----> Created file: " + fname

	fname = fname.split('.')[0]
	fname += '_Missing.csv'

	with open (fname, 'w') as f :
		writer = csv.writer(f, delimiter=dlimit)
		row = ['STUDENT']
		writer.writerow(row)

		for name in missing :
			writer.writerow([name])

	print "----> Created file :" + fname


def printError(string):
	print string

main()