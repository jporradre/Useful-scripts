#!/usr/bin/perl -w   

=begin comment0   

    xls_to_sql.pl : Perl script useful to create SQL queries dinamically from a XLS spreadsheet.
    Copyright (C) 2015  Juan Pablo Orradre

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
=end comment0    
=cut
    

use strict;
use warnings;

use Spreadsheet::ParseExcel;

if( @ARGV eq 2)
{
  my $path = $ARGV[0];
  my $col = $ARGV[1];
 
  if ($col =~ /^[0-9]+$/){
    if (-e $path){
		main($path, $col-1);
	}else{
		print "\nFile ", $path, " doesn't exist!\n";
	}
  } else {
   help();
  }
} else {
   help();
}


sub main{

my $col_cod = $_[1];

my $fn = "res.sql";
my $parser   = Spreadsheet::ParseExcel->new();
my $workbook = $parser->parse($_[0]);

my $ini_query = "SELECT field FROM table WHERE field2 IN (";

my $end_query = ") ORDER BY field2";

unlink $fn;

open(my $fh, '>', $fn);

print $fh $ini_query;

for my $worksheet ( $workbook->worksheets() ) {

    my ( $row_min, $row_max ) = $worksheet->row_range();
    my ( $col_min, $col_max ) = $worksheet->col_range();

    my @row_max_arr = (split /-/, $row_max);
    my $rm = $row_max_arr[0];


    for my $row ( $row_min .. $row_max ) {
	
	if ($row ne 0){

        	for my $col ( $col_min .. $col_max ) {

	    		if ($col == $col_cod){
	       			my $cell = $worksheet->get_cell( $row, $col ); 
	       			next unless $cell;
	       			print $fh "'" . $cell->value() . "'";

	       			if ($row ne $rm){
=begin comment1
	It brakes the SQL query "where" statement into less-than-1000-lines parts
	to be PL/SQL compatible and don't raise exception.
=end comment1
=cut
						if ($row%999 ne 0) {
							print $fh ",\n"
						} else {
							print $fh ") OR field2 IN (\n"
						}
	       			}
				}
	    	}        
          }
    }
}


print $fh $end_query;
close $fh;

print "\nConvert process has correctly ended.\n";
}

sub help{
	print "\n Usage: xls_to_sql.pl xls_file col\n 
	XLS_file: XLS file to be processed. \n 
	Col: Column number where filter field is \n\n 
	Arguments: \n
	-h : General help \n\n
	Output: SQL script including query including field values to filter the result.\n\n";
}



