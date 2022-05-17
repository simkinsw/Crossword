import requests
import json
import http.cookiejar as cookiejar
import sys
from datetime import date
import numpy as np
from square import Square
import grid 
import calendar
import tkinter
from tkinter import filedialog
from tkinter import messagebox as mb
import os
from os import path
from shutil import copyfile
import stats
import datepicker

def main():
    puzzdate = datepicker.main()
    #puzzdate = "2020-08-23"

    url = "https://nyt-games-prd.appspot.com/svc/crosswords/v3/36569100/puzzles.json?publish_type=daily&sort_order=asc&sort_by=print_date"
    response = requests.get(url)
    json_data = json.loads(response.text)
    puzzleList = json_data["results"]
    for puzzle in puzzleList:
        if puzzle["print_date"] == puzzdate:
            puzzleID = puzzle["puzzle_id"]
            break

    if not path.isdir("crosswords"):
        os.mkdir("crosswords")

    if not path.exists("crosswords/cookies.txt"):
        root = tkinter.Tk()
        root.withdraw()
        mb.showinfo("Cookies not loaded", "Please select your cookies.txt file. You must be logged in to nytimes.com\n\n" +
            "Try using the Chrome extension \"cookies.txt\" to download it.")
        cookie_path = filedialog.askopenfilename()
        copyfile(cookie_path, "crosswords/cookies.txt")
        root.destroy()

    stats.initialize_database()

    cj = cookiejar.MozillaCookieJar("crosswords/cookies.txt")
    cj.load()
    print("https://www.nytimes.com/svc/crosswords/v2/puzzle/" + str(puzzleID) + ".puz")
    r = requests.get("https://www.nytimes.com/svc/crosswords/v2/puzzle/" + str(puzzleID) + ".puz", cookies = cj)
   
    open("crosswords/" + puzzdate + ".puz", "wb").write(r.content)
    
    with open("crosswords/" + puzzdate + ".puz", "rb") as file:
        file.seek(44, 1)
        cols = int.from_bytes(file.read(1), "big")
        rows = int.from_bytes(file.read(1), "big")
        boardinput = file.read()[6 : ]


    #board building
    board = [[0] * cols for _ in range(rows)]
    aclues = ["None"]
    dclues = []
    acluesquares = []
    dcluesquares = []

    i = 0
    j = 0
    id = 0
    curNum = 1

    for square in boardinput:
        value = chr(square)
        if value == '-':
            break
        
        num = "_"

        dnum = -1

        if value != ".":
            if i == 0 or j == 0:
                num = str(curNum)
                if j == 0 or board[i][j-1].color == "black":
                    aclues.append(curNum)
                if i == 0 or board[i-1][j].color == "black":
                    dclues.append(curNum)
                    dnum = curNum
                curNum += 1
            elif board[i][j-1].color == "black" or board[i-1][j].color == "black":
                num = str(curNum)
                if board[i][j-1].color == "black":
                    aclues.append(curNum)
                if board[i-1][j].color == "black":
                    dclues.append(curNum)
                    dnum = curNum
                curNum += 1

        if value != "." and dnum == -1:
            dnum = board[i-1][j].dnum  

        board[i][j] = Square(i, j, num, "", value, aclues[-1], dnum)

        if num != "_":
            if num == str(aclues[-1]):
                acluesquares.append((i, j, False))
            if num == str(dnum):
                dcluesquares.append((i, j, True))

        j += 1
        if j == cols:
            j = 0
            i += 1
        if i == rows:
            break

    aclues = aclues[1:]
    acluesquares.append(None)
    acluesquares.extend(dcluesquares)
    cluesquares = acluesquares


    #Clue parsing
    boardstring = boardinput.decode("cp437")
    startindex = boardstring.index("The New York Times") + 19

    adict = {}
    ddict = {}
    aindex = 0
    dindex = 0

    clue = ""
    cluenum = 0
    for byte in boardinput[startindex : ]:
        if byte != 0:
            clue += chr(byte)
        else:
            if cluenum == len(aclues) + len(dclues):
                break
            elif aindex == len(aclues) or (dindex < len(dclues) and dclues[dindex] < aclues[aindex]):
                ddict[dclues[dindex]] = clue
                dindex += 1
            else:
                adict[aclues[aindex]] = clue
                aindex += 1
            cluenum += 1
            clue = ""

    adict["keylist"] = aclues
    ddict["keylist"] = dclues

    clues = {"aclues":adict, "dclues":ddict, "cluesquares":cluesquares}

    grid.main(board, clues, puzzdate) 



if __name__ == '__main__':


#    stats.add_puzzle("2021-09-21", 1000)
#    stats.add_puzzle("2021-09-22", 387)
#    stats.add_puzzle("2021-09-23", 319)
#    stats.add_puzzle("2021-09-23", 724)
#    stats.add_puzzle("2021-09-24", 676)
#    stats.add_puzzle("2021-09-25", 676)
#    stats.add_puzzle("2021-09-26", 676)
#    stats.add_puzzle("2021-09-27", 676)
#    print(stats.streak())


    stats.graph()