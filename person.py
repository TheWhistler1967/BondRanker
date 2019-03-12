class Person:

    def __init__(self, name, colors):
        self.name = name
        self.matrix = [["-" for x in range(24)] for y in range(7)]
        self.color_dict = {"dark": colors[0],
                           "norm": colors[1],
                           "light": colors[2]}

    #  Adds new movie to bottom row
    def add_movie(self, title):
        for x in range(7):
            for y in range(24):
                if self.matrix[x][y] == "-":
                    self.matrix[x][y] = title
                    break

    # Gets the last movie
    def get_last(self, row):
        for y in range(24):
            if self.matrix[row][y] == "-":
                return self.matrix[row][y-1]
        return False

    # Removes the last movie added
    def remove_last(self):
        for row in range(7):
            for y in range(24):
                if self.matrix[row][y] == "-":
                    self.matrix[row][y - 1] = "-"

    def get_movie(self, x, y):
        return self.matrix[x][y]

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

    def move_movie(self, row, col, x, y):
        old_mov = self.matrix[y][x]
        if x < row: # Distinguishes between down and up drags
            for z in range(x, row):
                self.matrix[col][z] = self.matrix[col][z+1]
            self.matrix[col][row] = old_mov
        else:
            for z in range(x, row, -1):
                self.matrix[col][z] = self.matrix[col][z-1]
            self.matrix[col][row] = old_mov

    # used for recap
    def update_order(self, cat, movies):
        for z in range(24):
            self.matrix[cat][z] = movies[z]

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

    def get_color(self, hue):
        return self.color_dict[hue]
