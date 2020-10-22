#!/usr/bin/env python3

import sys
import os
import time
import easygui
import getopt
from pdfrw import PdfReader, PdfWriter, PageMerge

class BookletPage:
    """
    Represents a single page in the booklet.
    Acts as an iterator and an array:
    0 = top left
    1 = top right
    2 = bottom left
    3 = bottom right
    """
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
        return "---\n[{}, {}]\n[{}, {}]".format(self[0], self[1], self[2], self[3])

class Booklet:
    """
    Represents booklet. Calcultates the page positions based on a page count.
    Acts as an iterator returning BookletPage instances in the right order.
    """
    def __init__(self, pagecount: int):
        
        self.realcount = pagecount
        # Count must be a multiple of 8: 4 per side
        self.count = (pagecount + (8 - (pagecount % 8))) if (pagecount % 8) != 0 else pagecount
        
        self.quadpage = 0
        self.quadpages = []
        pn = 0
        # Add a 'quad' page per 4 pages
        for pn in range(int(self.count / 4)):
            # print("Adding quad page: {}".format(pn+1))
            self.quadpages.append(BookletPage(self, pn + 1))
        # print("Creating booklet with {} ({}) pages -> {}x4 pages".format(self.realcount, self.count, len(self.quadpages)))

        # Not nice, brute force through pages. Could probably be done with math magic, but logic for this is a bit more clear.
        pnr = 0
        # 1: 1st halve, 1st quarter of the pages: loop front to back
        for x in range(len(self.quadpages)):
            # Alternate front & back: Even pages on the top right, odd on the top left
            self.quadpages[x][1 if (pnr % 2) == 0 else 0] = pnr
            pnr += 1
        
        # 2: 1st halve, 2nd quarter of the pages: loop front to back
        for x in range(len(self.quadpages)):
            # Alternate front & back: Even pages on the top left, odd on the top right
            self.quadpages[x][3 if (pnr % 2) == 0 else 2] = pnr
            pnr += 1

        # 3: 2nd halve, 3rd quarter of the pages: loop back to front
        for x in range(len(self.quadpages) - 1, -1, -1):
            # Alternate front & back: Even pages on the bottom right, odd on the bottom left
            self.quadpages[x][3 if (pnr % 2) == 0 else 2] = pnr
            pnr += 1

        # 4: 2nd halve, 4th quarter of the pages: loop back to front
        for x in range(len(self.quadpages) - 1, -1, -1):
            # Alternate front & back: Even pages on the bottom left, odd on the bottom right
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

def genPage(inpages, bookpage):
    scale = 0.5
    # Get the list of the pages, skip empty-ones
    pages = PageMerge() + ( inpages[i] for i in bookpage if i is not None and inpages[i] is not None)
    # Create a list with the positions of the pages that were empty, so we can correct the offset
    # when enumerating the pages in the pages list.
    nonepages = list( int(i) for i, p in enumerate(bookpage) if p is None or inpages[p] is None)
    
    # Figure out the size of the sub-pages, taking into account the scaling
    Xoff, Yoff = (scale * i for i in pages.xobj_box[2:])
    # Determine the offset corrections for each page position
    move = [ [0, Yoff], [Xoff, Yoff], [0, 0], [Xoff, 0] ]

    fixoff = 0
    for xi, p in enumerate(pages):
        try:
            # Fix offset if current index is in none list
            nonepages.index( (xi + fixoff) )
            # print("Added index fix for page {} (in none pages: {})".format(xi + fixoff, nonepages))
            fixoff += 1
        except ValueError:
            pass
        i = xi + fixoff

        # Scale the sub-page and correct the position on the current merged page
        p.scale(scale)
        p.x = move[i][0]
        p.y = move[i][1]

    # Render the merged pages and return the output
    return pages.render()
    
    

def genBooklet(infile: str, outfile: str):
    """
    Loads a PDF from infile, and generates a booklet from it, writing it to the outfile.
    """
    inpages = PdfReader(infile).pages
    writer = PdfWriter(outfile)
    
    book = Booklet(len(inpages))
    # Make sure the input page count matches the calculated pages count from the booklet
    while len(inpages) < book.count:
        inpages.append(None)

    # inpages = o_inpages
    opages = []

    # Generate all pages and append them to the output file
    for page in book:
        opages.append(genPage(inpages, page))

    writer.addpages(opages)
    writer.write()

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "an", ["autofilename", "noninteractive"])
    except Exception as e:
        print(e)
        sys.exit(2)

    autofilename = False
    noninteractive = False
    for o, a in opts:
        if o == "-a":
            autofilename = True
        if o == "-n":
            noninteractive = True
            autofilename = True

    if len(args) > 0:
        infile = args[0]
    else:
        infile = easygui.fileopenbox(msg="Open PDF document to generate booklet for", default="*.pdf", filetypes=["*.pdf"] )

    if infile is None:
        print("No document selected, exiting")
        sys.exit(1)

    # Autogenerate filename
    outfile = os.path.dirname(infile) + os.path.sep + 'booklet-' + os.path.basename(infile)
    if len(args) > 1:
        # Override output filename from cli args
        outfile = args[1]
        autofilename = True

    if not autofilename:
        # Ask for a file if we didn't request automatic filename generation, or wanted non-interactive mode.
        outfile = easygui.filesavebox(msg="Save booklet file", default=outfile, filetypes=["*.pdf"]  )

    if outfile is None:
        print("No output document selected, exiting")
        sys.exit(1)

    # Generate the booklet
    genBooklet(infile, outfile)

    if not noninteractive:
        easygui.msgbox("Booklet generated, saved to {}".format(outfile))
    else:
        print("Booklet generated, saved to {}".format(outfile))

if __name__ == "__main__":
    main()