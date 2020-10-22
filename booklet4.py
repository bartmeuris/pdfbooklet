#!/usr/bin/env python3

import sys
import os
import time
import easygui
from pdfrw import PdfReader, PdfWriter, PageMerge



class BookletPage:
    def __init__(self, booklet, pagenr: int):
        self.booklet = booklet
        self.nr = pagenr
        self.pages = [None,None,None,None]
    
    def __getitem__(self, key):
        if self.pages[key] is not None and self.pages[key] < self.booklet.realcount:
            return self.pages[key]
        return None

    def __setitem__(self, key, val):
        self.pages[key] = val

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index > 3:
            raise StopIteration
        self.index += 1
        return self[ self.index - 1 ]

    def __repr__(self):
        return "---\n[" + repr(self[0]) + ", " + repr(self[1]) + "]\n[" + repr(self[2]) + ", " + repr(self[3]) + "]"

class Booklet:
    def __init__(self, pagecount: int):
        
        self.realcount = pagecount
        self.count = (pagecount + (4 - (pagecount % 4))) if (pagecount % 4) != 0 else pagecount
        
        self.quadpage = 0
        self.quadpages = []
        for pn in range(int(self.count / 4)):
            self.quadpages.append(BookletPage(self, pn))

        # print("Creating booklet with {} ({}) pages -> {}x4 pages".format(self.realcount, self.count, len(self.quadpages)))
        
        pnr = 0

        # Add first set of pages
        for x in range(len(self.quadpages)):
            self.quadpages[x][1 if (pnr % 2) == 0 else 0] = pnr
            pnr += 1

        for x in range(len(self.quadpages)):
            self.quadpages[x][3 if (pnr % 2) == 0 else 2] = pnr
            pnr += 1

        for x in range(len(self.quadpages) - 1, -1, -1):
            self.quadpages[x][3 if (pnr % 2) == 0 else 2] = pnr
            pnr += 1

        for x in range(len(self.quadpages) - 1, -1, -1):
            self.quadpages[x][1 if (pnr % 2) == 0 else 0] = pnr
            pnr += 1


    def __iter__(self):
        self.quadpage = 0
        return self

    def __next__(self):
        if self.quadpage >= len(self.quadpages):
            raise StopIteration
        self.quadpage += 1
        return self.quadpages[self.quadpage - 1]

    def __repr__(self):
        return """---
Book:
    Pages: %d (fixed: %d)
    Quad pages: (%d /) %d
""" % (self.realcount, self.count, self.quadpage + 1, len(self.quadpages))

def genPage(inpages, bookpage):
    scale = 0.5
    pages = PageMerge() + ( inpages[i] for i in bookpage if i is not None and inpages[i] is not None)
    nonepages = list( int(i) for i, p in enumerate(bookpage) if p is None or inpages[p] is None)

    Xoff, Yoff = (scale * i for i in pages.xobj_box[2:])
    # move = [ [0, 0], [Xoff, 0], [0, Yoff], [Xoff, Yoff] ]
    move = [ [0, Yoff], [Xoff, Yoff], [0, 0], [Xoff, 0] ]
    
    # print("Xoff: {} / Yoff: {}".format(Xoff, Yoff))

    fixoff = 0
    for xi, p in enumerate(pages):
        # Fix offset if current index is in none list
        try:
            # print("Test if {} in {}".format(xi + fixoff, nonepages))
            nonepages.index( (xi + fixoff) )
            # print("Added index fix for page {} (in none pages: {})".format(xi + fixoff, nonepages))
            fixoff += 1
        except ValueError:
            pass
        i = xi + fixoff
        p.scale(scale)
        # print("[page {} index {} fix {}]: x: {} / y: {}".format(bookpage[i], i, fixoff, move[i][0], move[i][1]))
        p.x = move[i][0]
        p.y = move[i][1]

    return pages.render()
    
    

def genBooklet(infile: str, outfile: str):
    o_inpages = PdfReader(infile).pages
    writer = PdfWriter(outfile)
    
    book = Booklet(len(o_inpages))

    while len(o_inpages) < book.count:
        print("Adding blank page")
        o_inpages.append(None)
    
    inpages = o_inpages
    opages = []

    for page in book:
        # writer.addpages(genPage(inpages, page))
        opages.append(genPage(inpages, page))

    writer.addpages(opages)
    writer.write()

infile = easygui.fileopenbox(msg="Open PDF document to generate booklet for", default="*.pdf", filetypes=["*.pdf"] )
if infile is None:
    print("No document selected, exiting")
    exit()
outfile = 'booklet.' + os.path.basename(infile)
outfile = easygui.filesavebox(msg="Save booklet file", default=outfile, filetypes=["*.pdf"]  )
if outfile is None:
    print("No output document selected, exiting")

genBooklet(infile, outfile)
easygui.msgbox("Booklet generated, saved to {}".format(outfile))
