#!/usr/bin/python

import curses
import os
from subprocess import Popen
from re import escape

files = os.listdir(".")


class screen(object):
    def __init__(self, curdir=None, showhidden=False):

        self.window = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        self.window.keypad(1)
        curses.noecho()

        self.nameSize = 20
        self.leftmargin = 0
        self.rightmargin = 0
        self.typepadding = 5
        self.toppadding = 2

        self.set_bounds()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
        self.curdir = os.getcwd() if not curdir else curdir
        self.showhidden = showhidden

        self.prog = {
            "avi": "vlc",
            "txt": os.getenv("EDITOR") or "vim",
            "mp4": "vlc",
            "flv": "vlc",
        }

        self.actions = {
            ord("k"): self.moveup,
            ord("j"): self.movedown,
            ord("l"): self.moveright,
            ord("h"): self.moveleft,
            ord("o"): self.open,
            ord("H"): self.togglehidden,
            ord("b"): self.prevdir,
            ord("r"): lambda: self.displaydir(),
            ord("-"): self.rednamesize,
            ord("+"): self.incnamesize,
        }

    def set_bounds(self):

        self.ymax, self.xmax = self.window.getmaxyx()
        self.maxcols = (self.xmax - self.leftmargin - self.rightmargin) / (
            self.nameSize + self.typepadding
        )

    def makefiles(self):

        row = 0
        col = 0
        self.files = []
        for filename in os.listdir(self.curdir):
            if (not filename.startswith(".")) or self.showhidden:
                fileattr = (
                    filename,
                    os.path.isdir(os.path.join(self.curdir, filename)),
                    row,
                    col,
                )
                self.files.append(fileattr)

                col += 1
                if col >= self.maxcols:
                    row, col = row + 1, 0
                self.maxrows = row

    def centeralign(self, ypos, text, attrs=0):

        textlen = len(text)
        xpos = self.xmax / 2 - textlen / 2
        self.window.addstr(ypos, int(xpos), text, attrs)
        self.window.refresh()

    def displaydir(self):

        self.makefiles()
        self.window.clear()
        self.centeralign(0, "PyBrowser - " + str(self.curdir), curses.color_pair(1))
        for name, isdir, row, col in self.files:
            self.window.addnstr(
                int(row + self.toppadding),
                int(
                    self.leftmargin + col * (self.nameSize + self.typepadding)),
                    "[ ]" + name,
                    int(self.nameSize + 3),
                )

        self.itemnum = 0
        self.positioncursor()
        

    def positioncursor(self):

        filename, isdir, row, col = self.files[self.itemnum]
        self.window.move(
            row + self.toppadding, col * (self.nameSize + self.typepadding) + 1
        )
        self.window.refresh()

    def dispiteminfo(self):

        name, isdir, row, col = self.files[self.itemnum]
        head = "Directory : " if isdir else "File : "
        note = head + os.path.join(self.curdir, name)
        self.dispfootnote(note)
        self.positioncursor()
        self.window.refresh()

    def moveup(self):

        if self.itemnum >= self.maxcols:
            self.itemnum -= self.maxcols
        self.dispiteminfo()

    def movedown(self):

        if self.itemnum + self.maxcols < len(self.files):
            self.itemnum += self.maxcols
        self.dispiteminfo()

    def moveleft(self):

        if self.itemnum:
            self.itemnum -= 1
        self.dispiteminfo()

    def moveright(self):

        if self.itemnum < len(self.files) - 1:
            self.itemnum += 1
        self.dispiteminfo()

    def open(self):

        name, isdir, row, col = self.files[self.itemnum]
        if isdir:
            self.curdir = os.path.join(self.curdir, name)
            self.displaydir()
        else:
            ext = os.path.splitext(name)[1]
            fullpath = os.path.join(self.curdir, name)
            command = "nohup %s %s > /dev/null" % (
                self.prog.get(ext.lower()[1:], " "),
                escape(fullpath),
            )

            Popen(command, shell=True)
            self.displaydir()

    def dispfootnote(self, note):

        self.window.move(self.ymax - 1, 0)
        self.window.clrtoeol()
        self.window.addstr(self.ymax - 1, 0, note, curses.color_pair(2))
        self.window.refresh()

    def rednamesize(self):

        if self.nameSize > 5:
            self.nameSize -= 1
            self.set_bounds()
            self.displaydir()

    def incnamesize(self):

        if self.nameSize < 80:
            self.nameSize += 1
            self.set_bounds()
            self.displaydir()

    def prevdir(self):

        self.curdir = os.path.split(self.curdir)[0]
        self.displaydir()

    def togglehidden(self):

        self.showhidden = False if self.showhidden else True
        self.displaydir()

    def mainloop(self):

        self.displaydir()
        while True:
            key = self.window.getch()
            if key == ord("q"):
                self.quit()
                break
            else:
                self.actions.get(key, lambda: None)()

    def quit(self):

        self.window.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()


sc = screen()
sc.mainloop()
sc.quit()
