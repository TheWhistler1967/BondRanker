import os

import random
from person import Person
from recap import RecapWindow
from tkinter import Tk, Canvas, Button, filedialog, Label
import operator
import time
import contextlib
with contextlib.redirect_stdout(None):
    from pygame import mixer

# Inserted into save files, and checked on open
check_code = "#$&#$%^&*"

# Variables for window
border = 10
x_fin = 1500
y_fin = 990
x_sav, y_sav = 0, 0


# --------------------
# INITIAL SETTINGS
# --------------------
def lighten_darken(hex_normal):
    """
    Takes hex and a factor, converts to rgb, and returns lighter/darker hex
    :param hex_normal: Tuple of rgb values
    :param factor: factor for change where 0.15 = 15%
    :return: tuple of hex conversions
    """
    factor = 0.15  # Degree of change

    # convert hex to rgb
    hex_normal = hex_normal.lstrip('#')
    lv = len(hex_normal)
    r, g, b = tuple(int(hex_normal.lstrip('#')[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

    # Darken
    dark = (max(0, int(r-(r*(1+factor)-r))),
            max(0, int(g-(g*(1+factor)-g))),
            max(0, int(b-(b*(1+factor)-b))))
    hex_dark = '#%02x%02x%02x' % dark

    # Lighten
    light = (min(255, int(r * (1+factor))),
             min(255, int(g * (1+factor))),
             min(255, int(b * (1+factor))))
    hex_light = '#%02x%02x%02x' % light

    return hex_dark, '#'+hex_normal, hex_light


def load_settings():
    """
    Reads the settings .txt files and loads into memory
    :return: [Lists]: seen_movies, next_movies, categories, names, chosen_colours
    """
    # Load the movies and categories
    paths = ['settings/movies_seen.txt',
             'settings/movies_next.txt',
             'settings/categories.txt',
             'settings/persons.txt',
             'settings/movies_custom_colours.txt']
    return_data = ([], [], [], [], [])
    print("Loading .txt files...")

    # Load in seen_movies, next_movies, categories
    for x in range(3):
        file = open(paths[x], "r")
        lines = [line.rstrip('\n') for line in file]
        for line in lines:
            return_data[x].append(line)
    return_data[2].append("OVERALL")

    # Load the people/colours
    file = open(paths[3], "r")
    lines = [line.rstrip('\n') for line in file]
    for max_peep, line in enumerate(lines):
        name_col = line.split(':')
        hex_tup = lighten_darken(name_col[1])
        return_data[3].append(Person(name_col[0], hex_tup))
        for m in return_data[0]:
            return_data[3][len(return_data[3])-1].add_movie(m)
        if max_peep >= 12:
            print("ERROR: Max people exceeded (check settings/persons.txt)")
            return None

    # add 'Average' player
    return_data[3].append(Person("AVERAGE", ('@000000', '#000000', '#000000')))

    # Create list of custom colours:
    file = open(paths[4], "r")
    lines = [line.rstrip('\n') for line in file]
    for c in lines:
        return_data[4].append(c)

    return return_data


def add_buttons():
    """
    Adds buttons to the GUI
    """
    side_x_init = 1550
    x_pos = side_x_init
    y_pos = 10

    # Add people buttons (ID 0 to 11)
    for idx in range(num_players):
        if idx % 4 is 0:
            x_pos = side_x_init
            y_pos += 60
        p = people_list[idx]
        btn.insert(idx, Button(master, text=p.get_name(), bg=p.get_color("norm"), font=("Purisa", 20),
                               command=lambda c=idx: but_press(c)))
        btn[idx].place(x=x_pos, y=y_pos)
        master.update_idletasks()
        x_pos += btn[idx].winfo_width()

    # Fill list gaps if less that 12 people
    for x in range(12-len(btn)):
        btn.append(None)

    # Add average (ID 12)
    y_pos += 80
    x_pos = side_x_init+80
    btn.insert(12, Button(master, text="AVERAGE", bg="snow4", font=("Purisa", 25),
                          command=lambda c=12: but_press(c)))
    btn[12].place(x=x_pos, y=y_pos)

    # Add toggle
    y_pos += 80
    x_pos = side_x_init+80
    btn.insert(13, Button(master, text="Toggle", bg="#FFFFE0", font=("Purisa", 15),
                          command=lambda c=13: but_press(c)))
    btn[13].place(x=x_pos+53, y=y_pos+30)
    if len(custom_colours) < len(seen_movies+next_movies):
        btn[13].place_forget()

    # Add next movie and remove last (ID 14 and 15)
    btn.insert(14, Button(master, text="Add Next Movie  -->", bg="lavender", font=("Purisa", 10),
                          command=lambda c=14: but_press(c)))
    btn[14].place(x=side_x_init, y=850)
    btn.insert(15, Button(master, text="Remove Last", state="disabled", bg="lavender", font=("Purisa", 8),
                          command=lambda c=15: but_press(c)))
    btn[15].place(x=side_x_init+20, y=880)

    # Add Save and Load (ID 16 and 17)
    btn.insert(16, Button(master, text="Load", bg="snow4", font=("Purisa", 10),
                          command=lambda c=16: but_press(c)))
    btn[16].place(x=x_pos+50, y=950)
    btn.insert(17, Button(master, text="Save", bg="snow4", font=("Purisa", 10),
                          command=lambda c=17: but_press(c)))
    btn[17].place(x=x_pos+150, y=950)

    # Add categories (ID 18-23)
    cat_x = side_x_init
    cat_y = 500
    for idx, cat in enumerate(categories):
        if idx is len(categories)-1:  # Don't add overall
            break
        btn.insert(idx+18, Button(master, text=cat, bg="powder blue", font=("Purisa", 15),
                                  command=lambda c=idx+18: but_press(c)))
        btn[idx+18].place(x=cat_x, y=cat_y)
        cat_y += 50 if cat_x == (side_x_init+200) else 0
        cat_x = (side_x_init+200) if cat_x == side_x_init else side_x_init

    # Add close window
    b = Button(master, text="Save and Exit", bg="#DD3F3F", font=("Purisa", 10), command=close_window)
    b.place(x=1700, y=1000)

    # Need to do this to stop top left movie dragging when on button
    for b in btn:
        if b is not None:
            b.bind('<Enter>', lambda event, n='Enter': button_enter_exit(n))
            b.bind('<Leave>', lambda event, n='Leave': button_enter_exit(n))


def load_images_and_mp3s(movies):
    """
    Creates a dict of movies with list of images for each category
    :param movies: list of movies (seen and next)
    :return: dict
    """
    mp3_next = False  # Found a folder with mp3s
    mp3_d = {}
    img_arrays = {}
    for m in movies:
        img_arrays[m] = []
    idx = 0
    for root, subdir, files in os.walk('categories'):
        if idx > 0:  # Skip root folder
            for i, m in enumerate(movies):
                if len(subdir) > 0 and subdir[0] == 'mp3':
                    img_arrays[m].append("{}\{}".format(root, files[i]))
                    mp3_d[len(img_arrays[m]) - 1] = {}
                    mp3_next = True
                else:
                    if mp3_next is True:
                        mp3_d[len(img_arrays[m])-1][m] = "{}\{}".format(root, files[i])
                        # Check if end of folder
                        if len(img_arrays) - 1 == i:
                            mp3_next = False
                    else:
                        img_arrays[m].append("{}\{}".format(root, files[i]))
        idx += 1

    return img_arrays, mp3_d


def shuffle_colours(list_m):
    """
    Creates random bg colours for the movies, without making them too similar
    :return: movie_d: dict of movies to generated colours
    """
    movie_d = {}
    colours = []  # List of colours used to compare new ones
    closeness = 160  # The higher this value, the more unique the colours will be
    threshold = 200  # The lower this number, the darker colours can be
    attempts = 20000  # Returns what it has after it fails this many times

    for mx in list_m:
        count = 0
        while True:
            unique = True  # Used to break out of two loops
            count += 1  # Used to break out if taking too long

            if count > attempts:  # Returns if failing for too long
                return movie_d

            rgb = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            if (rgb[0] + rgb[1] + rgb[2]) < threshold:
                continue
            # Compare similarity of new colour to other ones (pretty crude, can be improved)
            for c in colours:
                similar_weight = 0
                for x in range(3):
                    difference = max(c[x], rgb[x]) - min(c[x], rgb[x])
                    similar_weight += difference

                    # Individual colours are different enough to pass
                    if difference > closeness-(closeness/2):
                        similar_weight += closeness

                if similar_weight < closeness:
                    unique = False

            # Good colour, break out
            if unique is True:
                break

        # Save the colour
        colours.append(rgb)
        #print("{} Saved: {}, {}, {}".format(mx, rgb[0], rgb[1], rgb[2]))
        movie_d[mx] = '#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2])
    return movie_d
# --------------------


# --------------------
# Live GUI Stuff
# --------------------
def draw(c, event=None):
    """
    Draw on the canvas
    :param c: canvas
    :param event: Event passed if dragging
    """
    c.delete("all")
    x_s = x_fin/7
    y_s = y_fin/24
    rect_colour = 'black'
    person = people_list[current_person]

    # Cat titles
    for _ in range(7):
        last_buff = 10 if _ == 6 else 0
        c.create_text(border+x_s*_+x_s/2+last_buff, 10, text=categories[_], font=("Purisa", 15))

    # Each movie in the cat
    drag_movie = None
    for yz in range(24):
        for xz in range(7):
            last_buff = 10 if xz == 6 else 0
            x = border+x_s*xz+last_buff
            y = border*2+y_s*yz

            movie = person.get_movie(xz, yz)
            drag_movie = person.get_movie(y_sav, x_sav)

            # Don't draw movie being dragged
            if event is not None and movie == drag_movie and y_sav == xz:
                movie = ''

            # Average is done a little different (the actual title has numbers in the name so it messes)
            if current_person == num_players:  # Is Average player
                for mov_title in movie_dict.keys():
                    if len(mov_title) > 14:
                        cut_title = mov_title[:14]
                    else:
                        cut_title = mov_title
                    if cut_title in movie:
                        rect_colour = movie_dict[mov_title]
                        break
                    else:
                        rect_colour = "gainsboro"
            else:
                if toggle_static:
                    if movie in static_colours:
                        rect_colour = static_colours[movie]
                    else:
                        rect_colour = "gainsboro"
                else:
                    if movie in seen_movies:
                        rect_colour = person.get_color("dark")
                    elif movie in next_movies:
                        rect_colour = person.get_color("light")
                    else:
                        rect_colour = "gainsboro"
            c.create_rectangle(x, y, x + x_s, y + y_s, fill=rect_colour)
            c.create_text(x+x_s+(x-(x+x_s/2)), y+y_s+(y-(y+y_s/2)), text=movie, font=("Purisa", 15))

    # Mouse drags
    if event is not None:
        if drag_movie in seen_movies:
            rect_colour = person.get_color("dark")
        elif drag_movie in next_movies:
            rect_colour = person.get_color("light")
        else:
            rect_colour = "gainsboro"
        c.create_rectangle(event.x-(x_s/2), event.y-(y_s/2), event.x-(x_s/2)+x_s, event.y-(y_s/2)+y_s, fill=rect_colour)
        c.create_text(event.x, event.y, text=drag_movie, font=("Purisa", 15))

    # Text
    c.create_text(1715, 45, text=person.get_name(), fill=person.get_color("norm"), font=("Purisa", 25))
    c.create_rectangle(1530, 450, 1880, 660)
    c.create_text(1705, 470, text="RECAP", font=("Purisa", 20))
    next_movie = next_movies[next_c] if next_c < len(next_movies) else '---'
    c.create_text(1800, 860, text=next_movie, fill="black", font=("Purisa", 15))

    c.pack()


def reset_add():
    """
    Disables the movie add/remove buttons when at one end
    """
    if next_c == len(next_movies):
        btn[14].config(state="disabled")
        btn[15].config(state="normal")
    elif next_c == 0:
        btn[14].config(state="normal")
        btn[15].config(state="disabled")
        btn[16].config(state="normal")
    else:
        btn[15].config(state="normal")
        btn[14].config(state="normal")
        btn[16].config(state="disabled")


def update_average():
    """
    Updates the 'average' person based on other player picks
    """
    sorted_matrix = [["-" for x in range(24)] for y in range(7)]
    movie_avg_dict = {}
    for m in seen_movies:
        movie_avg_dict[m] = 0.0
    for x in range(next_c):
        movie_avg_dict[next_movies[x]] = 0.0

    # Work one column at a time
    temp_dict = movie_avg_dict
    for x in range(7):
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
            new = {m: round(temp_dict[m]/num_players+1, 1)}
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
    people_list[num_players].set_matrix(sorted_matrix)  # Set average matrix
# --------------------


# --------------------
# Button presses and recap
# --------------------
def but_press(i):
    """
    Deals with the various GUI buttons
    :param i: ID of pressed buttons
    :return: nothing
    """
    global next_c
    global next_movies
    global current_person
    global movie_dict
    global toggle_static
    global shuffled_colours

    # Change current player
    if i < 12:
        current_person = i
    elif i == 12:
        if current_person == num_players:
            shuffled_colours = shuffle_colours(seen_movies+next_movies)
            movie_dict = shuffled_colours
        else:
            x = btn[12].winfo_rootx()
            y = btn[12].winfo_rooty()
            update_average()
            current_person = num_players  # Average player
    # Toggle static
    elif i == 13:
        if toggle_static is False:
            movie_dict = static_colours
            toggle_static = True
        else:
            movie_dict = shuffled_colours
            toggle_static = False
    # Add/Remove next movie
    elif i == 14 or i == 15:
        if i == 14:  # Add
            for p in range(num_players):
                people_list[p].add_movie(next_movies[next_c])
            next_c += 1
        else:  # Remove
            last = next_movies[next_c-1]
            for p in range(num_players):  # Check all players if valid removal
                for row in range(7):
                    if people_list[p].get_last(row) != last:
                        return
            for p in range(num_players):  # Remove it
                people_list[p].remove_last()
            next_c -= 1
        update_average()
        reset_add()  # Add/remove button disable/enable
    # Save and Load
    elif i == 16:
        load()
    elif i == 17:
        save()
    # Recap
    elif i >= 18:
        recap(i)

    if i >= 14:
        toggle_static = False
    save(True)  # Auto save
    return


# width, person, draw_movies, cat_images):
def recap(i):
    if current_person == num_players:
        return
    cat = i-18
    draw_movies = []

    w = 300 * (24/4)

    for x in range(24):
        draw_movies.append(people_list[current_person].get_movie(cat, x))

    if cat in mp3_dict:
        RecapWindow(people_list[current_person], w, draw_movies, cat_images, cat, categories[cat], mp3_dict[cat])
    else:
        RecapWindow(people_list[current_person], w, draw_movies, cat_images, cat, categories[cat])


def button_enter_exit(cmnd):
    global drag_on
    if cmnd == 'Enter':
        drag_on = False
    else:
        drag_on = True


def close_window():
    save()
    master.destroy()
# --------------------


# --------------------
# Mouse stuff
# --------------------
def get_pos(event):
    x_pos, y_pos = event.x, event.y
    row = 0
    col = 0

    box_y = y_fin / 24
    box_x = x_fin/7
    for y in range(24, -1, -1):
        if y_pos > box_y*y+border*2:
            row = y
            break

    for x in range(7, -1, -1):
        if x_pos > border+box_x*x:
            col = x
            break
    # Dragging too low
    if row >= len(all_movies):
        row = len(all_movies)-1
    return row, col


def left_click(event):
    global x_sav
    global y_sav
    x_sav, y_sav = get_pos(event)
    if y_sav > 6:
        y_sav = 6


def left_release(event):
    x_pos, y_pos = get_pos(event)
    if y_pos != y_sav or y_sav > 6 or y_pos > 6 or current_person == num_players:  # Average player
        draw(canv)
        return
    else:
        people_list[current_person].move_movie(x_pos, y_pos, x_sav, y_sav)
    draw(canv)


def left_drag(event):
    global toggle_static
    toggle_static = False
    if current_person == num_players:  # Average player
        return
    if event.x < 1500 and drag_on is True:
        draw(canv, event)
# --------------------


# --------------------
# Save and load
# --------------------
def save(auto_save=False):
    """
    Saves the players and their movies into text file
    :param auto_save: Adjusts the file_name when true
    """
    file_name = "saves/auto_save.txt" if auto_save else "saves/%s.txt" % time.strftime("%Y%m%d-%H%M%S")
    text_file = open(file_name, "w")

    # Get a list of player names
    names = []
    for p in people_list:
        names.append(p.get_name())

    # Write load settings to top of file
    text_file.write("{}\n".format(check_code))
    text_file.write("{}\n".format(names))
    text_file.write("{}\n".format(categories))
    text_file.write("{}\n".format(seen_movies))
    text_file.write("{}\n".format(next_movies))
    text_file.write("%d\n" % next_c)

    # Save players
    for x in range(num_players):
        p = people_list[x]
        text_file.write(p.get_save_string())


def load():
    """
    Loads players from a .txt file
    """
    file_path = filedialog.askopenfilename()

    # Check for wrong file type
    if not file_path.endswith('.txt'):
        print("ERROR: Bad file type")
        return

    file = open(file_path, "r")
    lines = [line.rstrip('\n') for line in file]

    # Confirm check code
    if len(lines) == 0 or lines[0] != check_code:
        print("ERROR: Bad save file")
        return

    # Get list of player names
    names = []
    for p in people_list:
        names.append(p.get_name())

    build_string = ""
    global next_c
    for idx, line in enumerate(lines):
        skip = False
        # Skip check line
        if idx == 0:
            continue

        # Check settings mismatch
        if idx == 1:
            if lines[idx] != str(names):
                print("LOAD ERROR: Names mismatch settings")
                return False
            continue
        if idx == 2:
            if lines[idx] != str(categories):
                print("LOAD ERROR: Categories mismatch settings")
                return False
            continue

        # Check if reloading without new movies
        if idx == 3:
            compare1 = str(lines[idx]+lines[idx + 1]).replace("][", ", ")
            if lines[idx] == str(seen_movies) and lines[idx+1] == str(next_movies):
                print("Loading previous state")
                next_c = int(lines[idx+2])
                reset_add()
            # Else check if next phase of marathon
            elif compare1 == str(seen_movies):
                print("Loading next phase")
            else:
                print("LOAD ERROR: Movie settings mismatch")
                return
            continue

        # Check if end of load string, else keep building string
        if idx >= 6:
            for x in range(len(names)):
                if line == names[x]:
                    people_list[x].load(build_string)
                    build_string = ""
                    skip = True  # Skips on last person
                    continue
            if not skip:
                build_string += "%s\n" % line
    print("Loaded")
# --------------------

def __callback():
    return


# Main
drag_on = True  # Cannot drag when False
btn = []
current_person = 0
next_c = 0
seen_movies, next_movies, categories, people_list, custom_colours = load_settings()
cat_images, mp3_dict = load_images_and_mp3s((seen_movies+next_movies))
num_players = len(people_list)-1  # Number of actual players (and idx of Average)

# Setup random colours for movies (used by 'Average')
toggle_static = False
shuffled_colours = shuffle_colours(seen_movies + next_movies)
movie_dict = shuffled_colours
# Setup static colours for movies *used by 'Average')
all_movies = seen_movies+next_movies
static_colours = {}
for x in range(len(all_movies)):
    static_colours[all_movies[x]] = custom_colours[x]

# Czreat tk, canvas etc
master = Tk()
master.winfo_toplevel().title("Bond Ranker")
master.wm_attributes("-topmost", 1)
master.protocol("WM_DELETE_WINDOW", __callback)
canv = Canvas(master, width=1920, height=1080)
master.bind('<Button-1>',  left_click)
master.bind('<ButtonRelease-1>',  left_release)
master.bind('<B1-Motion>',  left_drag)
add_buttons()
draw(canv)
canv.mainloop()
