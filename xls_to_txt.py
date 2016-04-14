#!/usr/bin/env python
# -*- coding: utf-8 -*-


#Copyright (C) 2016  Juan Pablo Orradre
#
#	 xls_to_txt.py : Python script useful to create a TXT file from data of a XLS spreadsheet.
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

import xlrd

#Function that writes the plain file
def write(pText,pFile):
	file = open(pFile, "a")
	file.write(pText)
	file.close()
	
	
total = "";
wb_filename = './workbook.xls'
result_filename = "result.txt"

# Opens workbook
wb = xlrd.open_workbook(wb_filename)

# Loads workbooks' first sheet
sheet = wb.sheet_by_index(0)

# Loads sheet's number of columns
num_cols = sheet.ncols   

# Iterates rows and then columns in order to load each cell value in "total" variable
for row in range(0, sheet.nrows):   
	for column in range(0, num_cols):
	
		try:
			cell_value = str(sheet.cell(row, column).value) 
		except UnicodeEncodeError:
			cell_value = str(sheet.cell(row, column).value.encode("utf-8","ignore")) 
			
		total = total + cell_value + "\t"

	#After iterating all columns of current row, prints carriage return (\r\n) ....
	total = total + "\r\n"

#When finished, prints all data in TXT file
write(total,result_filename)
