'''
This work is copyright (c) the Regents of the University of Minnesota, 2017.  
It was created by Kelly Thompson and Stacie Traill.

This script parses a single MARC binary file into separate files for books, serials, maps, visual materials, and other,
based on MARC LDR/06-07 coding. It then parses each format-specific file by holding campuses based on MARC 049 subfield a codes.
Creates one file per format per campus.
'''

import os
import re
import pymarc
from pymarc import MARCReader, MARCWriter, Record
from datetime import date

def fmt_split(MARCfile):
    
    '''
    Parses a MARC binary file based on LDR/06-07 values into separate files for books, serials, maps, visual materials, and
    other formats. Output is one .mrc file for each format.
    '''
    
    fname_str = str(MARCfile)
    fpref, fsuf = fname_str.split('.')
    today = str(date.today())

    with open(MARCfile,'rb') as f:

        reader = MARCReader(f)
    
        #opens a file for each format
        writer_bks = MARCWriter(open(fpref + '_bks.mrc', 'wb'))
        writer_ser = MARCWriter(open(fpref + '_ser.mrc', 'wb'))
        writer_maps = MARCWriter(open(fpref + '_maps.mrc', 'wb'))
        writer_vis = MARCWriter(open(fpref + '_vis.mrc', 'wb'))
        writer_other = MARCWriter(open(fpref + '_other.mrc', 'wb'))

        for rec in reader:
            
            field_909 = pymarc.Field(
                tag = '909',
                indicators = [' ',' '],
                subfields = ['a', 'bcat', 'b', 'MNU', 'c', today, 'd', 'marcive'])
            
            rec.add_ordered_field(field_909)
            
            ldr = rec.leader
        
            #regexes for string matching to determine format
            bks_re = re.compile('^.{6}am.*')
            ser_re = re.compile('^.{6}a[s|i].*')
            maps_re = re.compile('^.{6}e.*')
            vis_re = re.compile('^.{6}k.*')
        
            #determines format based on regex match of LDR/06-07 values
            bks = bks_re.match(ldr)
            ser = ser_re.match(ldr)
            maps = maps_re.match(ldr)
            vis = vis_re.match(ldr)
            
            #writes record to correct file based on regex matches
            if bks:
                writer_bks.write(rec)
            elif ser:
                writer_ser.write(rec)
            elif maps:
                writer_maps.write(rec)
            elif vis:
                writer_vis.write(rec)
            else:
                writer_other.write(rec)
            
            
    #closes master format files
    writer_bks.close()
    writer_ser.close()
    writer_maps.close()
    writer_vis.close()
    writer_other.close()


def campus_split():

    '''
    Finds the master format files created by fmt_split(). then writes the records in each format file to
    separate files for holding campuses based on coding in MARC 049 subfield a. Outputs one file per campus per format.
    '''
    campuses = ['MNGE', 'MNXN']
    
    for campus in campuses:
    
        files = [f for f in os.listdir() if re.match(r'.+(bks|ser|maps|vis|other)\.mrc', f)]

        for file in files:

            with open(file, 'rb') as f:
            
                filename = str(file)
                fpref, fsuf = filename.split('.')
                writer = MARCWriter(open(fpref + '_' + campus + '.mrc', 'wb'))
                reader = MARCReader(f)
    
                for rec in reader:
                    fields049 = rec.get_fields("049")
                    for field in fields049:
                        suba049 = field.get_subfields("a")
                        for suba in suba049:
                            if campus in suba:
                                writer.write(rec)
                            else:
                                continue
                        
                writer.close()

def main():

    '''
    Main function: gets user input for unparsed MARC file and runs
    fmt_split() and campus_split()
    '''
    
    fname = input ("Enter the MARC filename: ")
    fmt_split(fname)
    print("File splits by format complete.")
    campus_split()
    print("Format split by campus successful.")

main()