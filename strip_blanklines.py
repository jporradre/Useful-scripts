#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Copyright (C) 2016  Juan Pablo Orradre
#
#	 strip_blanklines.py : Python script useful to strip the blank lines from a file.
#
#    Use: python strip_blanklines file
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys

#Main process flow
if __name__ == '__main__':
	
	if len(sys.argv) < 2 or sys.argv[1].strip() == "":
		print('You must pass file name as parameter')
		exit(1)
	
	filename = sys.argv[1]
	
	text = ''
	
	#Iterates the file loading the unblanked text variable
	with open(filename,'r+') as file:
		for line in file:
			if line.strip():
				text = text + line

				
	#It rewrites it without the blanks			
	with open(filename,'w+') as file:
		file.write(text.rstrip('\n'))
