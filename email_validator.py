#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Copyright (C) 2016  Juan Pablo Orradre
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

import re;
import sys;

regexVal = "^[a-zA-Z0-9!#\$%&'\*\+\-\/=\?\^_`\{\|}~]+(\.[a-zA-Z0-9!#\$%&'\*\+\-\/=\?\^_`\{\|}~]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,4})$";

def printdec(pText):
	print(pText.decode("utf-8","ignore"));

	
if len(sys.argv) < 2:
    printdec("ERROR - Debe indicar el archivo a revisar como parámetro");
    exit(1);
	

if __name__ == '__main__':
		
	with open(sys.argv[1]) as f:
	
		i = 1;
	
		for line in f:
  
			address = line.split(":")[0];
		
			match = re.match(regexVal, address);
		
			if match is None:
				printdec("La direccion "+address+" es incorrecta. Línea "+str(i));
			
			i+=1;
