import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar, DateEntry
from datetime import date




def pick_calendar():
    def save_sel():
        global ret
        global root
        ret = str(cal.selection_get())
        root.destroy()

    top = tk.Toplevel(root)

    today = str(date.today())
    year = int(today[0 : 4])
    month = int(today[5 : 7])
    day = int(today[8: 10])
    cal = Calendar(top,
                   font="Arial 14", selectmode='day',
                   year=year, month=month, day=day)
    cal.pack(fill="both", expand=True)
    ttk.Button(top, text="OK", command=save_sel).pack()


def pick_today():
    global ret
    global root
    ret = str(date.today())
    root.destroy()


def main():
    global root
    global ret
    root = tk.Tk()
    root.title("Pick A Date")
    center(root)
    s = ttk.Style(root)
    s.theme_use('clam')

    ttk.Button(root, text='Today', command=pick_today).pack(padx=10, pady=10)
    ttk.Button(root, text='Calendar', command=pick_calendar).pack(padx=10, pady=10)

    root.mainloop()
    return ret

def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry('{}x{}+{}+{}'.format(120, 110, x, y))


if __name__ == "__main__":
    main()