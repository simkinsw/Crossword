import tkinter.filedialog
import tkinter as tk
from tkinter import messagebox as mb
from tkinter import *
import time
from time import sleep
import stats
import calendar
import winsound 


class App:

    def __init__(self, master, board, clues, puzzdate, *args, **kwargs):
        #tk.Tk.__init__(self, *args, **kwargs)

        frame = tk.Frame(master)
        frame.pack(side="left", ipadx=1)

        self.offset = 55
        if len(board) > 16:
            self.fontsize = 20
            self.cellside = 44
        else:
            self.fontsize = 25
            self.cellside = 50
        self.canvaswidth = len(board[0]) * self.cellside
        self.canvasheight = len(board) * self.cellside + self.offset

        self.canvas = tk.Canvas(frame, width=self.canvaswidth, height=self.canvasheight, borderwidth=0, highlightthickness=0)

        frame2 = tk.Frame(master).pack()
        Label(frame2, text="ACROSS                                                     " + 
            "DOWN", font="Arial 12 bold", anchor="w").pack(side="top", fill="both")
        scrollbar1 = tk.Scrollbar(frame2, orient="vertical")
        scrollbar1.pack(side="right", fill="y")
        self.downclues = tk.Text(frame2, width=28, wrap=WORD, font="Arial 12", tabs="1c")
        self.downclues.pack(side="right", fill="y")
        self.downclues.tag_configure("numbers", font="Arial 12 bold")
        self.downclues.tag_configure("clues", lmargin1=0, lmargin2=39)
        scrollbar2 = tk.Scrollbar(frame2, orient="vertical")
        scrollbar2.pack(side="right", fill="y")
        self.acrossclues = tk.Text(frame2, width=28, wrap=WORD, font="Arial 12", tabs="1c")
        self.acrossclues.pack(side="right", padx=5, fill="y")
        self.acrossclues.tag_configure("numbers", font="Arial 12 bold")
        self.acrossclues.tag_configure("clues", lmargin1=0, lmargin2=39)

        self.acrossclues.config(yscrollcommand=scrollbar2.set)
        self.downclues.config(yscrollcommand=scrollbar1.set)


        aclues = clues["aclues"]
        for key in aclues:
            keystr = str(key)
            if len(keystr) == 1:
                keystr = "    " + keystr
            elif len(keystr) == 2:
                keystr = "  " + keystr
            if key != "keylist":
                self.acrossclues.insert(END, keystr + "\t", ("numbers", str(key) + "a"))
                self.acrossclues.insert(END, aclues[key] + "\n", ("clues", str(key) + "a"))
                self.acrossclues.insert(END, "\n")
        self.acrossclues.delete(INSERT)
        self.acrossclues.delete(INSERT)
        self.acrossclues.config(state=DISABLED)


        dclues = clues["dclues"]
        for key in dclues:
            keystr = str(key)
            if len(keystr) == 1:
                keystr = "    " + keystr
            elif len(keystr) == 2:
                keystr = "  " + keystr
            if key != "keylist":
                self.downclues.insert(END, keystr + "\t", ("numbers", str(key) + "d"))
                self.downclues.insert(END, dclues[key] + "\n", ("clues", str(key) + "d"))
                self.downclues.insert(END, "\n")
        self.downclues.delete(INSERT)
        self.downclues.delete(INSERT)
        self.downclues.config(state=DISABLED)


        self.date = puzzdate
        self.canvas.pack(side="top", fill="both", expand="true")
        self.rows = len(board)
        self.columns = len(board[0])
        self.bottommargin = 3
        self.down = True
        i = 0;
        while(board[0][i].color != "white"):
            i += 1;
        self.curSquare = board[0][i]
        self.board = board
        self.clues = clues
        self.highlightWord = []
        self.squaremap = {}
        self.seconds = 0
        self.minutes = 0
        self.complete = False
        self.rebus_mode = False

        self.canvas.create_rectangle(0, 0, self.canvaswidth, self.offset, fill="light gray")

        for column in range(self.columns):
            for row in range(self.rows):
                square = board[row][column]
                self.initializeSquare(square)
        
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<Key>", self.key)
        self.canvas.focus_set()
        self.focus(0, i)
        self.tick()
        self.canvas.after(1, self.tick)

    def initializeSquare(self, square):
        squaredict = {"rect":None, "text": None, "number":None}
        self.squaremap[square] = squaredict
        color = square.color
        column = square.col
        row = square.row
        x1 = column * self.cellside
        y1 = row * self.cellside + self.offset
        x2 = x1 + self.cellside
        y2 = y1 + self.cellside
        squaredict["rect"] = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags=color)
        if color != "black":
            squaredict["text"] = self.canvas.create_text(x1 + self.cellside / 2, y1 + self.cellside - (self.fontsize / 2 + self.bottommargin), 
                font="Arial " + str(self.fontsize), text="", tags=color)
        if square.number != None:
            leftOffset = 11
            if int(square.number) > 99:
                leftOffset = 13
            squaredict["number"] = self.canvas.create_text(x1 + leftOffset, y1 + 10, font="Arial 11", text=square.number, tags=color)

    def recolorSquare(self, square):
        rect = self.squaremap[square]["rect"]
        self.canvas.itemconfig(rect, fill=square.color)

    def rewriteSquare(self, square):
        text = self.squaremap[square]["text"]
        if len(square.value) > 4:
            font = 8
        elif len(square.value) > 2:
            font = 12
        elif len(square.value) > 1:
            font = 18
        else:
            font = self.fontsize
        self.canvas.itemconfig(text, text=square.value, font="Arial " + str(font))
        for row in self.board:
            for square in row:
                if square.color != "black" and square.value[0:1] != square.solution:
                    return

        if self.seconds < 10:
            string = str(self.minutes) + ":0" + str(int(self.seconds))
        else:
            string = str(self.minutes) + ":" + str(int(self.seconds))
        self.complete = True
       
        mb.showinfo("Congratulations", "You finished the puzzle in " + string)
        time = self.minutes*60 + self.seconds
        stats.add_puzzle(self.date, time)

    def drawClue(self, num, clue):
        self.canvas.delete("clue")
        if self.down:
            letter = "D"
        else:
            letter = "A"
        self.canvas.create_text(self.canvaswidth / 2 - 50, self.offset / 2, font ="Arial 16 bold", text=str(num)+letter+": "+clue, tags="clue", width = self.canvaswidth - 100)

    def focus(self, row, col):
        if not row in range(self.rows) or not col in range(self.columns):
            return

        square = self.board[row][col]

        if square.color == "black":
            return

        self.acrossclues.tag_config(str(self.curSquare.anum) + "a", background="white")
        self.downclues.tag_config(str(self.curSquare.dnum) + "d", background="white")
        self.acrossclues.tag_config(str(square.anum) + "a", background="lightblue")
        self.downclues.tag_config(str(square.dnum) + "d", background="lightblue")
        self.acrossclues.see("end")
        self.acrossclues.see(str(square.anum) + "a"+ ".first")
        self.downclues.see("end")
        self.downclues.see(str(square.dnum) + "d"+ ".first")    

        if square == self.curSquare:
            self.down = not self.down

        if self.curSquare != None:
            self.curSquare.color = "White"
            self.recolorSquare(self.curSquare)


        for s in self.highlightWord:
            s.color = "white"
            self.recolorSquare(s)

        self.highlightWord = []


        if not self.down:
            for j in range(0, self.columns):
                s = self.board[row][j]
                if s.anum == square.anum:
                    self.highlightWord.append(s)
                    s.color = "light blue"
                    self.recolorSquare(s)

        if self.down:
            for i in range(0, self.rows):
                s = self.board[i][col]
                if s.dnum == square.dnum:
                    self.highlightWord.append(s)
                    s.color = "light blue"
                    self.recolorSquare(s)


        self.curSquare = square
        square.color = "yellow"
        self.recolorSquare(square)

        if not self.down:
            cluenum = square.anum
            clue = self.clues["aclues"][cluenum]
        else:
            cluenum = square.dnum
            clue = self.clues["dclues"][cluenum]
        self.drawClue(cluenum, clue)

    

    def tick(self):
        if self.complete:
            return
        self.canvas.delete("timer")
        self.seconds += .5
        if self.seconds == 60:
            self.seconds = 0
            self.minutes += 1
        if self.seconds < 10:
            string = str(self.minutes) + ":0" + str(int(self.seconds))
        else:
            string = str(self.minutes) + ":" + str(int(self.seconds))
        self.canvas.create_text(self.canvaswidth - 35, self.offset / 2, font="Arial 14", text=string, tag="timer")
        self.canvas.after(1000, self.tick)

    def key(self, event):
        if self.rebus_mode:
            global text
            text = self.curSquare.value
            if event.keysym == "Tab" or event.keysym == "Return" or event.keysym == "Insert":
                self.rebus_mode = False
                self.curSquare.color = "yellow"
                self.recolorSquare(self.curSquare)
                return
            elif event.keysym == "BackSpace":
                text = text[0 : -1]
                self.curSquare.value = text
                self.rewriteSquare(self.curSquare)
                return
            else:
                text = text + event.char.upper()
                self.curSquare.value = text
                self.rewriteSquare(self.curSquare)
                return


        if event.keysym == "Insert":
            self.rebus_mode = True
            self.curSquare.color = "lightgreen"
            self.recolorSquare(self.curSquare)
        elif event.keysym == "Tab" or event.keysym == "Return":
            cluesquares = self.clues["cluesquares"]
            x, y = self.highlightWord[0].row, self.highlightWord[0].col
            curIndex = cluesquares.index((x, y, self.down))
            while True:
                curIndex += 1
                if curIndex == len(cluesquares):
                    curIndex = 0
                    self.down = False
                elif cluesquares[curIndex] == None:
                    self.down = True
                    curIndex += 1

                row = cluesquares[curIndex][0]
                col = cluesquares[curIndex][1]
                square = self.board[row][col]
                if self.down:
                    while row < len(self.board) and square.color != "black":
                        square = self.board[row][col]
                        if square.value == "" or square.value == " ":
                            self.focus(row, col)
                            return
                        row += 1
                else:
                    while col < len(self.board[row]) and square.color != "black":
                        square = self.board[row][col]
                        if square.value == "" or square.value == " ":
                            self.focus(row, col)
                            return
                        col += 1

        elif event.keysym == "Left":
            if self.down:
                self.focus(self.curSquare.row, self.curSquare.col)
            else:
                self.focus(self.curSquare.row, self.curSquare.col - 1)
        elif event.keysym == "Right":
            if self.down:
                self.focus(self.curSquare.row, self.curSquare.col)
            else:
                self.focus(self.curSquare.row, self.curSquare.col + 1)
        elif event.keysym == "Up":
            if not self.down:
                self.focus(self.curSquare.row, self.curSquare.col)
            else:
                self.focus(self.curSquare.row-1, self.curSquare.col)
        elif event.keysym == "Down":
            if not self.down:
                self.focus(self.curSquare.row, self.curSquare.col)
            else:
                self.focus(self.curSquare.row + 1, self.curSquare.col)

        elif self.complete:
            pass

        elif event.keysym == "BackSpace":
            if self.curSquare.value == "":
                if self.down:
                    self.focus(self.curSquare.row - 1, self.curSquare.col)
                else:
                    self.focus(self.curSquare.row, self.curSquare.col - 1)
            self.curSquare.value = ""
            self.rewriteSquare(self.curSquare)
            return
        else:
            self.curSquare.value = event.char.upper()
            self.rewriteSquare(self.curSquare)
            row, col = self.curSquare.row, self.curSquare.col
            if self.down:
                i = row + 1
                while i < len(self.board) and self.board[i][col].color != "black":
                    if self.board[i][col].value == "" or self.board[i][col].value == " ":
                        self.focus(i, col)
                        return
                    i += 1
                self.focus(row + 1, col)
            else:
                j = col + 1
                while j < len(self.board[0]) and self.board[row][j].color != "black":
                    if self.board[row][j].value == "" or self.board[row][j].value == " ":
                        self.focus(row, j)
                        return
                    j += 1
                self.focus(row, col + 1)

    def click(self, event):  
        if self.rebus_mode:
            self.rebus_mode = False
        row = (event.y - self.offset) // self.cellside
        col = (event.x) // self.cellside
        self.focus(row, col)


def main(board, clues, puzzdate):
    year = puzzdate[0 : 4]
    month = puzzdate[5 : 7]
    day = puzzdate[8 : ]

    day = int(day)
    month = int(month)
    year = int(year)

    dayofweek = calendar.day_name[calendar.weekday(year, month, day)]
    title = dayofweek + ", " + calendar.month_name[month] + " " + str(day) + ", " + str(year)

    root = Tk()
    grid = App(root, board, clues, puzzdate)
    root.title(title)
    if dayofweek == "Sunday":
        root.geometry("+200+10")
    else:    
        root.geometry("+295+50")
    root.focus_force()
    root.mainloop()
