#!/usr/bin/env python3

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
    
    def __repr__(self):
        return "---\n[" + repr(self[0]) + ", " + repr(self[1]) + "]\n[" + repr(self[2]) + ", " + repr(self[3]) + "]"

class Booklet:
    def __init__(self, pagecount: int):
        
        self.realcount = pagecount
        self.count = pagecount + (4 - (pagecount % 4))
        
        self.quadpage = 0
        self.quadpages = []
        for pn in range(int(self.count / 4)):
            self.quadpages.append(BookletPage(self, pn))
        
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

book = Booklet(17)

print(repr(book))

for x in book:
    print(repr(x))
