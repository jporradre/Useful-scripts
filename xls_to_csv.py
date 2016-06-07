#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Copyright (C) 2016  Juan Pablo Orradre
#
#	 xls_to_csv.py : Python script useful to convert an Excel file to a CSV file.
#
#    Use: python xls_to_csv.py source_xls_file destiny_csv_file
#
#    Notes:
#    - Converts an Excel file to a CSV file.
#    - If the excel file has multiple worksheets, only the first worksheet is converted.
#    - Uses unicodecsv, so it will handle Unicode characters.
#    - Uses a recent version of xlrd, so it should handle old .xls and new .xlsx equally well.
#    - Based on script from http://www.penwatch.net/cms/?p=484
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
import xlrd
import unicodecsv

if len(sys.argv) < 3:
    print("ERROR - You must pass as parameters source xls filename and destiny csv filename respectively")
    exit(1)
	

xls_filename = sys.argv[1]
csv_filename = sys.argv[2]


wb = xlrd.open_workbook(xls_filename)
sh = wb.sheet_by_index(0)

fh = open(csv_filename,"wb")
csv_out = unicodecsv.writer(fh, encoding='utf-8')

for row_number in xrange (sh.nrows):
	csv_out.writerow(sh.row_values(row_number))

fh.close()
