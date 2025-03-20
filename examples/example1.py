from charset import charset

if __name__ == "__main__":

    for c in charset("ansi", random=False):
        print(c, c.name)
