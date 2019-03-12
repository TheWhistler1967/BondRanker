import tkinter as tk
from tkinter import Canvas, Button, Label
from PIL import ImageTk, Image
import contextlib
with contextlib.redirect_stdout(None):
    from pygame import mixer


class RecapWindow:

    def __init__(self, p, width, draw_movies, cat_images, cat, title, mp3_dict=None):
        self.label_img = []
        self.label_txt = []
        self.person = p
        self.width = width
        self.cat = cat
        self.draw_movies = draw_movies
        self.cat_images = cat_images.copy()
        self.cat_images['-'] = ['categories\\default_movie.png' for i in range(6)]
        self.selected = self.get_last()

        #  mp3 setup
        self.mp3_dict = mp3_dict
        if self.mp3_dict is not None:
            self.mp3_folder = True
            self.mp3_buttons = []
            mixer.init()
        else:
            self.mp3_folder = False

        # Setup tk nd canvas
        self.master = tk.Toplevel()
        self.master.winfo_toplevel().title(title)
        self.canv = Canvas(self.master, width=width, height=1000)
        self.canv.configure(bg='gainsboro')
        self.master.bind('<KeyRelease>', self.key_handler)
        self.master.bind('<MouseWheel>', self.scroll)

        # Used for scrolling
        self.scroll_up = False
        self.scroll_down = False
        self.scroll = []  # Image objects

        self.draw()

        # Select the last movie
        if not self.mp3_folder:  # True is initial call, deals with placement button bug
            self.on_click(self.selected)

    def draw(self):
        resize_w = 240
        resize_h = 165
        x = 0
        y = 0
        border = 30
        buffer = 40

        # Add buttons
        b = Button(self.master, text="Save and Exit", bg='green', font=("Purisa", 10), command=self.save_exit)
        b.place(x=self.width-100, y=10)

        if self.mp3_folder:
            b1 = Button(self.master, text="Play", bg='green', font=("Purisa", 10),
                        command=lambda cmd='Play':self.mp3_ctrl(cmd))
            self.mp3_buttons.append(b1)
            b1.place_forget()
            b2 = Button(self.master, text="Stop", bg='red', font=("Purisa", 10),
                        command=lambda cmd='Stop':self.mp3_ctrl(cmd))
            self.mp3_buttons.append(b2)
            b2.place_forget()



        # Draw movies
        for idx, m in enumerate(self.draw_movies):
            i = Image.open(self.cat_images[m][self.cat])
            i = i.resize((resize_w, resize_h), Image.ANTIALIAS)
            render = ImageTk.PhotoImage(i)
            img = Label(self.canv, image=render, highlightthickness=0, borderwidth=0)
            self.label_img.append(img)
            img.image = render
            img.bind('<Button-1>', lambda event, n=idx: self.on_click(n))
            img.place(x=x + border, y=y + border)

            text_label = Label(self.canv, text="{}   {}".format(idx+1, m), font=('Comic Sans MS', 15), bg='gainsboro')
            text_label.place(x=x+border, y=y-5)
            self.label_txt.append(text_label)
            if (idx + 1) % 4 == 0:
                y = 0
                x = x + resize_w + buffer
            else:
                y = y + resize_h + (buffer*2)

        # Scroll
        i = Image.open('categories\\scroll_up.png')
        i = i.resize((100,100), Image.ANTIALIAS)
        render = ImageTk.PhotoImage(i)
        img = Label(self.canv, image=render, highlightthickness=0, borderwidth=0)
        self.label_img.append(img)
        img.image = render
        img.bind('<Enter>', lambda event, n='Up': self.scroll_enter(n))
        img.bind('<Leave>', lambda event, n='Up': self.scroll_exit(n))
        img.bind('<1>', lambda event, n='Up': self.key_handler(n))
        img.place(x=x, y=380)
        self.scroll.append(img)

        i = Image.open('categories\\scroll_down.png')
        i = i.resize((100, 100), Image.ANTIALIAS)
        render = ImageTk.PhotoImage(i)
        img = Label(self.canv, image=render, highlightthickness=0, borderwidth=0)
        self.label_img.append(img)
        img.image = render
        img.bind('<Enter>', lambda event, n='Down': self.scroll_enter(n))
        img.bind('<Leave>', lambda event, n='Down': self.scroll_exit(n))
        img.bind('<1>', lambda event, n='Down': self.key_handler(n))
        img.place(x=x, y=500)
        self.scroll.append(img)
        self.canv.pack()

    def save_exit(self):
        self.person.update_order(self.cat, self.draw_movies)
        if self.mp3_folder:
            mixer.music.fadeout(500)
        self.master.destroy()

    def mp3_ctrl(self, cmd):
        c, movie = self.get_text_split(self.selected, self.label_txt[self.selected].cget('text'))
        if movie == '-':
            return
        if cmd == 'Play':
            mixer.music.load(self.mp3_dict[movie])
            mixer.music.play()
        else:
            mixer.music.fadeout(500)

    def scroll_enter(self, event):
        if event == "Up":
            self.scroll_up = True
            self.scroll_down = False
            path = 'categories\\scroll_up_on.png'
            x = 0
        else:
            self.scroll_up = False
            self.scroll_down = True
            path = 'categories\\scroll_down_on.png'
            x = 1

        i = Image.open(path)
        i = i.resize((100, 100), Image.ANTIALIAS)
        render = ImageTk.PhotoImage(i)
        self.scroll[x].config(image=render)
        self.scroll[x].image = render

    def scroll_exit(self, event):
        self.scroll_up = False
        self.scroll_down = False

        if event == "Up":
            path = 'categories\\scroll_up.png'
            x = 0
        else:
            path = 'categories\\scroll_down.png'
            x = 1

        i = Image.open(path)
        i = i.resize((100, 100), Image.ANTIALIAS)
        render = ImageTk.PhotoImage(i)
        self.scroll[x].config(image=render)
        self.scroll[x].image = render

    def scroll(self, event):
        if self.scroll_up is False and self.scroll_down is False:
            return
        if self.scroll_up:
            self.key_handler("Up")
        else:
            self.key_handler("Down")

    def on_click(self, i):
        self.label_txt[self.selected].config(bg='gainsboro')
        self.label_txt[i].config(bg="green")
        self.selected = i
        if self.mp3_folder:
            self.move_buttons()

    def move_buttons(self):
        c, movie = self.get_text_split(self.selected, self.label_txt[self.selected].cget('text'))

        if movie == '-':
            self.mp3_buttons[0].place_forget()
            self.mp3_buttons[1].place_forget()
        else:
            x_pos = self.label_img[self.selected].winfo_rootx()
            y_pos = self.label_img[self.selected].winfo_rooty()
            self.mp3_buttons[0].place(x=x_pos-20, y=y_pos+100)
            self.mp3_buttons[1].place(x=x_pos+20, y=y_pos+100)

    def key_handler(self, event):
        if self.selected == -1:
            return

        if not isinstance(event, str):
            event = event.keysym

        if event == "Up":
            if self.selected == 0:  # Can't move up from the first
                return
            self.swap_movies(-1)
            self.selected -= 1

        if event == "Down":
            if self.selected == len(self.draw_movies) - 1:  # Can't move down from the last
                return
            self.swap_movies(1)
            self.selected += 1

        if self.mp3_folder:
            self.move_buttons()

    def swap_movies(self, change):
        resize_w = 240
        resize_h = 165
        saved_movie = self.draw_movies[self.selected]
        # Swap the movie order (this will update person)
        self.draw_movies[self.selected] = self.draw_movies[self.selected + change]
        self.draw_movies[self.selected + change] = saved_movie

        # Swap the text
        t1 = self.label_txt[self.selected].cget('text')
        t2 = self.label_txt[self.selected + change].cget('text')
        num1, title1 = self.get_text_split(self.selected, t1)
        num2, title2 = self.get_text_split(self.selected + change, t2)
        self.label_txt[self.selected].config(text="{}   {}".format(num1, title2), bg='gainsboro')
        self.label_txt[self.selected + change].config(text="{}   {}".format(num2, title1), bg='green')

        # Swap the images
        i1 = Image.open(self.cat_images[title1][self.cat])
        i2 = Image.open(self.cat_images[title2][self.cat])
        i1 = i1.resize((resize_w, resize_h), Image.ANTIALIAS)
        i2 = i2.resize((resize_w, resize_h), Image.ANTIALIAS)
        render1 = ImageTk.PhotoImage(i1)
        render2 = ImageTk.PhotoImage(i2)
        self.label_img[self.selected].config(image=render2)
        self.label_img[self.selected + change].config(image=render1)
        self.label_img[self.selected].image = render2
        self.label_img[self.selected + change].image = render1

    def get_text_split(self, idx, text):
        if idx < 9:
            num = text[:1]
            title = text[4:]
        else:
            num = text[:2]
            title = text[5:]
        return num, title

    def get_last(self):
        for x in range(len(self.draw_movies)):
            if self.draw_movies[x] == '-':
                return x-1
        return len(self.draw_movies)-1
