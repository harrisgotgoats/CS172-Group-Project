import curses

screen = curses.initscr()

windows = curses.newwin(2, 20, 0, 0)

i = 1


for i in range(20000):
    screen.clear()
    screen.addstr(0, 0, f"String {i}")
    screen.addstr(1, 0, f"String {i + 1}")

    screen.refresh()

curses.endwin()