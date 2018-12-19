import tkinter as tk
from tkinter import Tk, Canvas, Button, filedialog
from PIL import ImageTk, Image
import operator
import time
import contextlib
with contextlib.redirect_stdout(None):
    from pygame import mixer

check_code = "#$&#$%^&*" # Inserted into save files, and checked on open

# Global variables for window
b = 10
x_fin = 1500
y_fin = 990
x_sav, y_sav = 0, 0

# Arrays
colour_list = ["red", "dark orange2", "green", "steel blue", "black"]
name_list = ["Nick", "Graham", "Cindy", "Stu", "AVERAGE"]
global next_c
next_c = 0
connery = ["Dr No", "FRWL", "Thunderball", "Goldfinger", "You Only Live Twice", "OHMSS", "Diamonds Are Forever"]
next_movie = ["Live and Let Die", "Man with Golden Gun", "Spy Who Loved Me", "Moonraker",
              "For Your Eyes Only", "Octopussy", "A View to Kill", "---"]
movie_colours = {"Dr No": "indian red", "FRWL": "red", "Thunderball": "SkyBlue1", "Goldfinger": "gold",
                 "You Only": "khaki", "OHMSS": "snow", "Diamonds Are": "cyan", "Live and": "lime green",
                 "Man with": "dark goldenrod", "Spy Who": "SlateGray4", "Moon": "ivory3", "For Your": "green yellow",
                 "Octop": "wheat1", "A View": "orchid1"}
person_colours = [["LightPink2", "LightPink1"], ["dark orange", "orange"],
                  ["SeaGreen3", "SeaGreen2"], ["SkyBlue3", "SkyBlue1"]]

# Image arrays for 'Recap'
bond_girls = []
bond_gadgets = []
bond_villians = []
bond_plot = []
bond_cold = []
bond_theme = [] # single image only
theme_songs = []

# Array of Person
people_list = []


class Person:
    """Person class"""
    def __init__(self, name):
        self.name = name
        self.colour = ""
       # self.movies = []
        self.matrix = [["-" for x in range(24)] for y in range(7)]

    def add_movie(self, title):
        for x in range(7):
            for y in range(24):
                if self.matrix[x][y] == "-":
                    self.matrix[x][y] = title
                    break

    def get_last(self, row):
        for y in range(24):
            if self.matrix[row][y] == "-":
                return self.matrix[row][y-1]
        return False

    def remove_last(self):
        for row in range(7):
            for y in range(24):
                if self.matrix[row][y] == "-":
                    self.matrix[row][y - 1] = "-"

    def get_movie(self, x, y):
        return self.matrix[x][y]

    def draw(self):
        print("hi")

    def get_save_string(self):
        string_build = ""
        for y in range(24):
            for x in range(7):
                string_build += str(self.matrix[x][y])
                string_build += '~'
            string_build += "\n"
        string_build += "{}\n".format(self.name)
        return string_build

    def load(self, s):
        lines = s.splitlines()
        col = 0
        for line in lines:
            line_split = line.split('~')
            for idx, movie in enumerate(line_split):
                if idx == 7:  # Skip whitespace
                    break
                self.matrix[idx][col] = movie
            col += 1

    def move_movie(self, row, col):
        old_mov = self.matrix[y_sav][x_sav]
        if x_sav < row: # Distinguishes between down and up drags
            for z in range(x_sav, row):
                self.matrix[col][z] = self.matrix[col][z+1]
            self.matrix[col][row] = old_mov
        else:
            for z in range(x_sav, row, -1):
                self.matrix[col][z] = self.matrix[col][z-1]
            self.matrix[col][row] = old_mov

    def print(self):
        for y in range(24):
            string_build = ""
            for x in range(7):
                movie = self.matrix[x][y]
                string_build += movie
                lgt = len(movie)
                for _ in range(22-lgt):
                    string_build += " "
            print(string_build)

    def get_matrix(self):
        return self.matrix

    def get_name(self):
        return self.name

    def set_matrix(self, mtx):
        self.matrix = mtx


def get_current():
    return people_list[current_person]


def get_colour(true_colour=True):
    if true_colour:
        return colour_list[current_person]
    return person_colours[current_person][0]


# UI Setup

def load_images():
    img_paths = ["/diamonds.png", "/liveand.png", "/goldgun.png", "/spywho.png",
                 "/moon.png", "/youreyes.png", "/octo.png", "/view.png"]
    for p in img_paths:
        bond_girls.append(ImageTk.PhotoImage(Image.open("girls"+p)))
        bond_gadgets.append(ImageTk.PhotoImage(Image.open("gadgets"+p)))
        bond_villians.append(ImageTk.PhotoImage(Image.open("villians"+p)))
        bond_plot.append(ImageTk.PhotoImage(Image.open("plot" + p)))
        bond_cold.append(ImageTk.PhotoImage(Image.open("coldopens" + p)))

    bond_theme.append(ImageTk.PhotoImage(Image.open("themes/themes.png")))

    mp3_list = ["drno", "russ", "gold", "thun", "twic", "ohmss", "diam",
            "live", "ggun", "spyw", "moon", "fyeo", "octo", "view"]
    for mp3 in mp3_list:
        theme_songs.append("themes/"+mp3+".mp3")


def add_buttons():
    side_x_init = 1550
    side_people = side_x_init
    for i in range(4):
        btn.append(Button(master, text=name_list[i], bg=colour_list[i], font=("Purisa", 20), command=lambda c=i: but_press(c)))
        btn[i].place(x=side_people, y=100)
        master.update_idletasks()
        side_people += btn[i].winfo_width()

    btn.append(Button(master, text="Add Next Movie  -->", bg="lavender", font=("Purisa", 10), command=lambda c=4: but_press(c)))
    btn[4].place(x=side_x_init, y=800)
    btn.append(Button(master, text="Remove Last", state="disabled", bg="lavender", font=("Purisa", 8), command=lambda c=5: but_press(c)))
    btn[5].place(x=side_x_init+20, y=830)

    cat_x = side_x_init
    cat_y = 500
    btn.append(Button(master, text="Cold Open", bg="powder blue", font=("Purisa", 15), command=lambda c=6: but_press(c)))
    btn[6].place(x=cat_x, y=cat_y)
    btn.append(Button(master, text="Plot", bg="MediumPurple1", font=("Purisa", 15), command=lambda c=7: but_press(c)))
    btn[7].place(x=cat_x+200, y=cat_y)
    btn.append(Button(master, text="Theme Song", bg="cornsilk2", font=("Purisa", 15), command=lambda c=8: but_press(c)))
    btn[8].place(x=cat_x, y=cat_y+50)
    btn.append(Button(master, text="Bond Girls", bg="pink", font=("Purisa", 15), command=lambda c=9: but_press(c)))
    btn[9].place(x=cat_x+200, y=cat_y+50)
    btn.append(Button(master, text="Gadgets", bg="tan1", font=("Purisa", 15), command=lambda c=10: but_press(c)))
    btn[10].place(x=cat_x, y=cat_y+100)
    btn.append(Button(master, text="Villians", bg="snow4", font=("Purisa", 15), command=lambda c=11: but_press(c)))
    btn[11].place(x=cat_x+200, y=cat_y+100)

    btn.append(Button(master, text="Load", bg="snow4", font=("Purisa", 10), command=lambda c=12: but_press(c)))
    btn[12].place(x=cat_x+100, y=cat_y+450)
    btn.append(Button(master, text="Save", bg="snow4", font=("Purisa", 10), command=lambda c=13: but_press(c)))
    btn[13].place(x=cat_x+200, y=cat_y+450)

    btn.append(Button(master, text="AVERAGE", bg="snow4", font=("Purisa", 25), command=lambda c=14: but_press(c)))
    btn[14].place(x=side_x_init+80, y=200)


def draw(c, event=None):
    c.delete("all")
    x_s = x_fin/7
    y_s = y_fin/24

    labels = ["Cold Open", "Theme Song", "Gadgets", "Villians", "Bond Girls", "Plot", "OVERALL"]

    for _ in range(7):
        last_buff = 10 if _ == 6 else 0
        c.create_text(b+x_s*_+x_s/2+last_buff, 10, text=labels[_], font=("Purisa", 15))

    for yz in range(24):
        for xz in range(7):
            last_buff = 10 if xz == 6 else 0
            x = b+x_s*xz+last_buff
            y = b*2+y_s*yz
            movie = get_current().get_movie(xz, yz)
            drag_movie = get_current().get_movie(y_sav, x_sav)
            # Average is done a little different
            if current_person == 4:
                for clr in movie_colours.keys():
                    #print("%s   %s" % (clr, movie))
                    if clr in movie:
                        rect_colour = movie_colours[clr]
                        break
                    else:
                        rect_colour = "gainsboro"
            else:
                if movie in connery:
                    rect_colour = person_colours[current_person][0]
                elif movie in next_movie:
                    rect_colour = person_colours[current_person][1]
                else:
                    rect_colour = "gainsboro"
            c.create_rectangle(x, y, x + x_s, y + y_s, fill=rect_colour)
            c.create_text(x+x_s+(x-(x+x_s/2)), y+y_s+(y-(y+y_s/2)), text=movie, font=("Purisa", 15))

    # Mouse drags
    if event is not None:
        if drag_movie in connery:
            rect_colour = person_colours[current_person][0]
        elif drag_movie in next_movie:
            rect_colour = person_colours[current_person][1]
        else:
            rect_colour = "gainsboro"
        c.create_rectangle(event.x-(x_s/2), event.y-(y_s/2), event.x-(x_s/2)+x_s, event.y-(y_s/2)+y_s, fill=rect_colour)  # , fill="black")
        c.create_text(event.x, event.y, text=drag_movie, font=("Purisa", 15))

    c.create_text(1715, 45, text=name_list[current_person], fill=get_colour(), font=("Purisa", 25))
    c.create_rectangle(1530,450,1880,660)  # , fill="black")
    c.create_text(1705, 470, text="RECAP", font=("Purisa", 20))
    c.create_text(1800, 812, text=next_movie[next_c], fill="black", font=("Purisa", 15))
    c.pack()


# GUI Reactions
def reset_add():
    if next_c == len(next_movie) - 1:
        btn[4].config(state="disabled")
        btn[5].config(state="normal")
    elif next_c == 0:
        btn[4].config(state="normal")
        btn[5].config(state="disabled")
    else:
        btn[4].config(state="normal")
        btn[5].config(state="normal")


def but_press(i):
    global next_c
    global next_movie

    if i < 4:
        global current_person
        current_person = i
        save(True)  # Auto-save
    elif i == 4:
        for p in range(4):
            people_list[p].add_movie(next_movie[next_c])
        next_c += 1
        reset_add()
    elif i == 5:
        last = next_movie[next_c-1]
        for p in range(4):
            for row in range(7):
                if people_list[p].get_last(row) != last:
                    return
        for p in range(4):
            people_list[p].remove_last()
        next_c -= 1
        if next_c == 0:
            btn[i].config(state="disabled")
        else:
            btn[4].config(state="normal")
    elif i == 6:
        recap("cold")
    elif i == 7:
        recap("plot")
    elif i == 8:
        recap("theme")
    elif i == 9:
        recap("girls")
    elif i == 10:
        recap("gadgets")
    elif i == 11:
        recap("villians")
    elif i == 12:
        load()
    elif i == 13:
        save()
    elif i == 14:  # Average person
        current_person = 4
        update_average()
    return


def recap(type_s):
    if type_s is "girls":
        disp_list = bond_girls
    elif type_s is "gadgets":
        disp_list = bond_gadgets
    elif type_s is "villians":
        disp_list = bond_villians
    elif type_s is "plot":
        disp_list = bond_plot
    elif type_s is "cold":
        disp_list = bond_cold
    elif type_s is "theme":
        disp_list = bond_theme
    else:
        return

    win = tk.Toplevel()

    # Slightly different for theme, as only one image
    idx = 0 if type_s == "theme" else next_c

    w = disp_list[idx].width()
    h = disp_list[idx].height()
    win.geometry("%dx%d+%d+%d" % (w, h, 0, 0))

    photo = disp_list[idx]
    label = tk.Label(win, image=photo)
    label.image = photo
    label.pack()

    if type_s == "theme":
        for x in range(7+next_c):
            b = Button(win, text="Play", bg="powder blue", font=("Purisa", 15), command=lambda c=x: play_song(c))
            x_loc = 30 + 115 * x if x < 7 else 30 + 115 * (x-7)
            y_loc = 180 if x < 7 else 460
            b.place(x=x_loc, y=y_loc)
        b = Button(win, text="Stop", bg="light coral", font=("Purisa", 15), command=lambda: stop_song())
        b.place(x=860, y=200)

    close = Button(win, text="CLOSE", bg="red", font=("Purisa", 12),
                       command=lambda c=c: win.destroy())
    close.place(x=w - 100, y=20)


def play_song(x):
    mixer.init()
    mixer.music.load(theme_songs[x])
    mixer.music.play()


def stop_song(win=None):
    if win is not None:
        win.destroy()
    mixer.music.fadeout(500)


def update_average():
    sorted_matrix = [["-" for x in range(24)] for y in range(7)]
    movie_dict = {}
    for m in connery:
        movie_dict[m] = 0.0
    for x in range(next_c):
        movie_dict[next_movie[x]] = 0.0

    # Work one column at a time
    temp_dict = movie_dict
    for x in range(7):
       # print("\n\nFIrst")
        # Clear dict for the next round
        for m in temp_dict:
            temp_dict.update({m: 0.0})

        for p in people_list:
            if p.get_name() == "AVERAGE":
                continue
            mtx = p.get_matrix()
            for y in range(24):
                if mtx[x][y] == '-':
                    continue
                new = {mtx[x][y]: temp_dict[mtx[x][y]]+y}
                temp_dict.update(new)

        for m in temp_dict:
            new = {m: temp_dict[m]/4+1}
            temp_dict.update(new)

        # Sort dict, and set the average matrix up (also setup colour dict)
        sorted_dict = sorted(temp_dict.items(), key=operator.itemgetter(1))
        for col in range(24):
            if col == len(sorted_dict):
                break
            title = sorted_dict[col][0]
            sub = 14-len(title)  # Max title length is set here
            if sub < 0:
                title = title[:sub]
            title += "  %s" % str(sorted_dict[col][1])
            sorted_matrix[x][col] = title

    # Finally, set the matrix
    people_list[4].set_matrix(sorted_matrix)


# Mouse stuff

def get_pos(event):
    x_pos, y_pos = event.x, event.y
    row = 0
    col = 0

    box_y = y_fin / 24
    box_x = x_fin/7
    for y in range(24, -1, -1):
        if y_pos > box_y*y+b*2:
            row = y
            break

    for x in range(7, -1, -1):
        if x_pos > b+box_x*x:
            col = x
            break
    return row, col


def left_click(event):
    global x_sav
    global y_sav
    x_sav, y_sav = get_pos(event)
    if y_sav > 6:
        y_sav = 6


def left_release(event):
    x_pos, y_pos = get_pos(event)
    if y_pos != y_sav or y_sav > 6 or y_pos > 6 or current_person == 4:
        draw(c)
        return
    else:
        get_current().move_movie(x_pos, y_pos)
    draw(c)


def left_drag(event):
    if current_person == 4:
        return
    if event.x < 1500:
        draw(c, event)


# Save and Load

def save(auto_save=False):
    if auto_save:
        file_name = "saves/auto_save.txt"
    else:
        file_name = "saves/%s.txt" % time.strftime("%Y%m%d-%H%M%S")
    text_file = open(file_name, "w")
    text_file.write("{}\n".format(check_code))
    text_file.write("%d\n" % next_c)
    for x in range(4):
        p = people_list[x]
        text_file.write(p.get_save_string())


def load():
    print("Loading...")
    file_path = filedialog.askopenfilename()

    # Check for wrong file type
    if not file_path.endswith('.txt'):
        print("ERROR: Bad file type")
        return

    file = open(file_path, "r")
    lines = [line.rstrip('\n') for line in file]

    # Check for wrong save file
    if len(lines) == 0 or lines[0] != check_code:
        print("ERROR: Bad save file")
        return

    build_string = ""
    global next_c
    for idx, line in enumerate(lines):
        skip = False
        # Skip check line
        if idx == 0:
            continue

        # Add movies as required
        if idx == 1:
            next_c = int(lines[idx])
            reset_add()
            continue
        # Check if end of load string, else keep building string
        for x in range(4):
            if line == name_list[x]:
                people_list[x].load(build_string)
                build_string = ""
                skip = True
                continue
        if not skip:
            build_string += "%s\n" % line
    print("Done!")


# Main
btn = []
master = Tk()
master.winfo_toplevel().title("Bond Ranker")
c = Canvas(master, width=1920, height=1080)

for p in range(5):
    people_list.append(Person(name_list[p]))
for m in connery:
    for p in range(5):
        people_list[p].add_movie(m)
current_person = 0

load_images()

master.bind('<Button-1>',  left_click)
master.bind('<ButtonRelease-1>',  left_release)
master.bind('<B1-Motion>',  left_drag)
add_buttons()

draw(c)
c.mainloop()
