import sqlite3
import os
from os import path
import calendar
from datetime import date
from datetime import timedelta
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.lines as lines

def initialize_database():
	if not path.exists("crosswords/stats.db"):
		conn = sqlite3.connect("crosswords/stats.db")
		c = conn.cursor()
		c.execute("CREATE TABLE stats (date text, dayOfWeek text, time integer, streak integer)")
		conn.close()


def add_puzzle(puzzdate, time):
	conn = sqlite3.connect("crosswords/stats.db")
	c = conn.cursor()
	year = int(puzzdate[0 : 4])
	month = int(puzzdate[5 : 7])
	day = int(puzzdate[8 : ])

	c.execute("SELECT * from stats WHERE date=?", (puzzdate,))
	if(c.fetchone()):
		return

	if str(date.today()) == puzzdate:
		streak = 1
	else:
		streak = 0

	dayOfWeek = calendar.day_name[calendar.weekday(year, month, day)]
	c.execute("INSERT INTO stats VALUES (?, ?, ?, ?)", (puzzdate, dayOfWeek, time, streak))
	conn.commit()
	conn.close()

def remove_puzzle(puzzdate):
	conn = sqlite3.connect("crosswords/stats.db")
	c = conn.cursor()

	c.execute("DELETE from stats WHERE date=?", (puzzdate,))

	conn.commit()
	conn.close()


def print_all():
	conn = sqlite3.connect("crosswords/stats.db")
	c = conn.cursor()

	c.execute("DELETE from stats WHERE date=?", ("2020-08-24",))
	c.execute("SELECT * from stats")
	print("All Puzzles:")
	print(c.fetchall())
	conn.close()


def calc_average(dayOfWeek):
	dayNum = list(calendar.day_name).index(dayOfWeek)

	conn = sqlite3.connect("crosswords/stats.db")
	c = conn.cursor()
	c.execute("SELECT time from stats WHERE dayOfWeek=?", (dayOfWeek,))
	times = c.fetchall()

	if times == []:
		return 0

	avg = 0
	for time in times:
		avg += time[0]
	avg /= len(times)
	mins = int(avg // 60)
	secs = int(avg % 60)
	conn.close()
	return avg


def calc_best(dayOfWeek):
	conn = sqlite3.connect("crosswords/stats.db")
	c = conn.cursor()
	c.execute("SELECT time from stats WHERE dayOfWeek=?", (dayOfWeek,))
	times = c.fetchall()

	if times == []:
		return 0

	best = times[0][0]
	for time in times:
		if time[0] < best:
			best = time[0]
	mins = int(best // 60)
	secs = int(best % 60)
	return best


def most_recent(dayOfWeek):
	conn = sqlite3.connect("crosswords/stats.db")
	c = conn.cursor()
	c.execute("SELECT time, date from stats WHERE dayOfWeek=?", (dayOfWeek,))
	days = c.fetchall()

	if days == []:
		return 0

	curyear = curmonth = curday = 0
	for entry in days:
		puzzdate = entry[1]
		year = int(puzzdate[0 : 4])
		month = int(puzzdate[5 : 7])
		day = int(puzzdate[8 : ])
		if year > curyear:
			time = entry[0]
		elif year == curyear and month > curmonth:
			time = entry[0]
		elif year == curyear and month == curmonth and day > curday:
			time = entry[0]
	mins = int(time // 60)
	secs = int(time % 60)
	return time


def puzzles_completed():
	conn = sqlite3.connect("crosswords/stats.db")
	c = conn.cursor()
	c.execute("SELECT * from stats")
	num = len(c.fetchall())
	return num


def streak():
	conn = sqlite3.connect("crosswords/stats.db")
	c = conn.cursor()
	c.execute("SELECT date from stats")
	dates = c.fetchall()

	streak = 0
	if (str(date.today()),) in dates:
		streak = 1

	curdate = date.today() + timedelta(-1)
	while (str(curdate),) in dates:
		streak += 1
		curdate = curdate + timedelta(-1)

	return 501 + streak


def graph():
	conn = sqlite3.connect("crosswords/stats.db")
	c = conn.cursor()

	today = calendar.day_name[date.today().weekday()]

	days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
	datadict = {"Recent":{}, "Best":{}, "Average":{}, "Day":{}}

	for i in range(0, 7):
		datadict["Day"][days[i]] = days[i]
		datadict["Recent"][days[i]] = most_recent(days[i])
		datadict["Best"][days[i]] = calc_best(days[i])
		datadict["Average"][days[i]] = calc_average(days[i])

	data = pd.DataFrame.from_dict(datadict)

	sns.set(style="whitegrid")

	# Initialize the matplotlib figure
	f, ax = plt.subplots(figsize=(12, 9))


	sns.barplot(x="Day", y="Recent", data=data, alpha=0)

	for rect in ax.patches:
		rect.set_width(rect.get_width() + .1)
		rect.set_x(rect.get_x() - .05)
		line = lines.Line2D([rect.get_x(), rect.get_x()+rect.get_width()], [rect.get_height()], color="black", linestyle="--")
		ax.add_line(line)

	clrs = ["lightcoral" if (x==today) else "cornflowerblue" for x in days]
	sns.barplot(x="Day", y="Average", data=data, palette=clrs, edgecolor="black", linestyle="-")

	clrs = ["red" if (x==today) else "dodgerblue" for x in days]
	sns.barplot(x="Day", y="Best", data=data, palette=clrs, edgecolor="black")

	for i in range(len(ax.patches)):
		rect = ax.patches[i]
		if rect.get_height() in datadict["Best"].values():
			rect.set_width(rect.get_width() + .1)
			rect.set_x(rect.get_x() - .05)
			height = rect.get_height()
			minutes = str(int(height // 60))
			seconds = str(int(height % 60))
			if len(seconds) == 1:
				seconds = "0" + seconds
			time = minutes + ":" + seconds
			offset = -15
			if not time == "0:00":
				ax.annotate('{}'.format("Best: " + time), xy=(rect.get_x() + rect.get_width() / 2, height), xytext=(0, offset), textcoords="offset points", ha="center", va="bottom", fontweight="bold")
		if rect.get_height() in datadict["Average"].values():
			rect.set_width(rect.get_width() + .1)
			rect.set_x(rect.get_x() - .05)
			r,g,b,a = rect.get_facecolor()
			rect.set_facecolor((r,g,b,.5))
			height = rect.get_height()
			minutes = str(int(height // 60))
			seconds = str(int(height % 60))
			if len(seconds) == 1:
				seconds = "0" + seconds
			time = minutes + ":" + seconds
			if int(ax.patches[i-7].get_height()) in range(int(height) - 5, int(height)+50):
				offset = -15
			else:
				offset = 1
			if not time == "0:00":
				ax.annotate('{}'.format("Average: " + time), xy=(rect.get_x() + rect.get_width() / 2, height), xytext=(0, offset), textcoords="offset points", ha="center", va="bottom", fontweight="bold")
		if rect.get_height() in datadict["Recent"].values():
			if rect.get_height() == datadict["Recent"][today]:
				label = "Today: "
			else:
				label = "Recent: "
			height = rect.get_height()
			minutes = str(int(height // 60))
			seconds = str(int(height % 60))
			if len(seconds) == 1:
				seconds = "0" + seconds
			time = minutes + ":" + seconds
			if int(ax.patches[i+7].get_height()) in range(int(height), int(height) + 50):
				offset = -15
			else:
				offset = 1
			if not time == "0:00":
				ax.annotate('{}'.format(label + time), xy=(rect.get_x() + rect.get_width() / 2, height), xytext=(0, offset), textcoords="offset points", ha="center", va="bottom", fontweight="bold")

	ax.annotate('{}'.format(str(streak())) + " day streak", xy=(0, calc_average("Sunday")), xytext=(0.001, 0), textcoords="offset points", ha="left", va="bottom", fontsize=20)

	sns.despine(left=True, bottom=True, top=True, right=True)
	f.axes[0] = ""
	ax.set_ylabel("")
	ax.set_xlabel("")
	ax.grid(False)
	ax.axes.yaxis.set_visible(False)
	thismanager = plt.get_current_fig_manager()
	thismanager.window.wm_geometry("+350+30")
	plt.show()



