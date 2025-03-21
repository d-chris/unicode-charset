from charset import charset


def main():
    """
    >>> for c in charset("ansi", n=10,  min=60, random=False):
    ...     print(c, c.name)
    ...
    < LESS-THAN SIGN
    = EQUALS SIGN
    > GREATER-THAN SIGN
    ? QUESTION MARK
    @ COMMERCIAL AT
    A LATIN CAPITAL LETTER A
    B LATIN CAPITAL LETTER B
    C LATIN CAPITAL LETTER C
    D LATIN CAPITAL LETTER D
    E LATIN CAPITAL LETTER E
    """

    for c in charset("ansi", n=10, min=60, random=False):
        print(c, c.name)


if __name__ == "__main__":
    main()
