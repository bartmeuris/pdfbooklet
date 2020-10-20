#!/usr/bin/env python

'''
usage: subset_booklets.py my.pdf

Creates subset_booklets.my.pdf

Pages organized in a form suitable for booklet printing, e.g.
to print 4 8.5x11 pages using a single 11x17 sheet (double-sided).
Instead of a large booklet, the pdf is divided into several mini
booklets. The reason is: professional printing works this way:
    - Print all of several mini booklets(subsets of booklet);
    - Saw each mini booklet individually;
    - glue them all together;
    - Insert the cover.

    Take a look at http://www.wikihow.com/Bind-a-Book
'''

import sys
import os
import time
from pdfrw import PdfReader, PdfWriter, PageMerge

PAGES_PERSIDE = 4
START = time.time()

# Paste 2 pages horizontally
def fixhpage(*pages):
    result = PageMerge() + (x for x in pages if x is not None)
    result[-1].x += result[0].w
    return result.render()

# Paste 2 pages vertically
def fixvpage(*pages):
    result = PageMerge() + (x for x in pages if x is not None)
    result[-1].y += result[0].h
    return result.render()

INPFN = sys.argv[1]
OUTFN = 'booklet.' + os.path.basename(INPFN)

ALL_IPAGES = PdfReader(INPFN).pages
print('The pdf file '+str(INPFN)+' has '+str(len(ALL_IPAGES))+' pages.')

print("Pages to generate: %d\n" %(len(ALL_IPAGES) / 4 ))

#Make sure we have an even number
if len(ALL_IPAGES) & 1:
    ALL_IPAGES.append(None)
    print('Inserting blank page.')


opages = []
ipages = ALL_IPAGES

while len(ipages) > 2:
    opages.append(fixhpage(ipages.pop(), ipages.pop(0)))
    opages.append(fixhpage(ipages.pop(0), ipages.pop()))

if len(ipages) >= 1:
    opages.append(fixhpage(ipages.pop(), ipages.pop(0)))

npages = []

if (len(opages) % 2) != 0:
    opages.append(None)

offset = int(len(opages) / 2)

for i in range(0, offset):
    print("Generating page %d (+ %d)" % (i, offset + i) )
    npages.append(fixvpage(opages[offset + i], opages[i]))


PdfWriter(OUTFN).addpages(npages).write()
print('It took '+ str(round(time.time()-START, 2))+' seconds to make the pdf subbooklets changes.')

