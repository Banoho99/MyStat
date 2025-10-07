#!/usr/bin/env python3
import curses
import random
import time

# --- Config ---
BOARD_HEIGHT = 20
BOARD_WIDTH = 40
INITIAL_SPEED_MS = 120    # plus petit = plus rapide
SPEEDUP_EVERY = 5         # accélère tous les X points
SPEED_INCREMENT = 5       # ms en moins à chaque palier

# Directions (dy, dx)
DIRS = {
    curses.KEY_UP:    (-1, 0),
    curses.KEY_DOWN:  (1, 0),
    curses.KEY_LEFT:  (0, -1),
    curses.KEY_RIGHT: (0, 1),
}

def new_food(snake, h, w):
    cells = {(y, x) for y in range(1, h - 1) for x in range(1, w - 1)}
    free = list(cells - set(snake))
    return random.choice(free) if free else None

def draw_border(win):
    win.border()
    win.refresh()

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)
    curses.use_default_colors()

    # Fenêtre de jeu centrée
    max_y, max_x = stdscr.getmaxyx()
    top = (max_y - BOARD_HEIGHT) // 2
    left = (max_x - BOARD_WIDTH) // 2
    win = curses.newwin(BOARD_HEIGHT, BOARD_WIDTH, top, left)
    win.keypad(True)
    win.nodelay(True)

    # Écran d’accueil
    title = "S N A K E"
    stdscr.addstr(top - 2, max(0, (max_x - len(title)) // 2), title)
    stdscr.addstr(top + BOARD_HEIGHT + 1, max(0, (max_x - 38) // 2),
                  "Flèches pour bouger • q pour quitter • Entrée pour jouer")
    stdscr.refresh()
    draw_border(win)

    # Attente démarrage
    while True:
        k = stdscr.getch()
        if k in (ord('\n'), curses.KEY_ENTER):
            break
        if k in (ord('q'), ord('Q')):
            return
        time.sleep(0.01)

    # État initial du serpent
    mid_y, mid_x = BOARD_HEIGHT // 2, BOARD_WIDTH // 2
    snake = [(mid_y, mid_x - 1), (mid_y, mid_x), (mid_y, mid_x + 1)]
    direction = DIRS[curses.KEY_LEFT]  # commence vers la gauche
    last_key = curses.KEY_LEFT
    score = 0
    best = 0
    speed_ms = INITIAL_SPEED_MS

    food = new_food(snake, BOARD_HEIGHT, BOARD_WIDTH)

    def render():
        win.clear()
        draw_border(win)

        # Affichage score
        header = f"Score: {score}   Record: {best}"
        stdscr.addstr(top - 1, max(0, (max_x - len(header)) // 2), header)
        stdscr.refresh()

        # Nourriture
        if food:
            fy, fx = food
            try:
                win.addch(fy, fx, '✱')
            except curses.error:
                pass

        # Serpent
        for i, (y, x) in enumerate(snake):
            ch = '■' if i == len(snake) - 1 else '●'
            try:
                win.addch(y, x, ch)
            except curses.error:
                pass

        win.refresh()

    render()
    last_move = time.time()

    while True:
        # Lecture des entrées
        k = win.getch()
        if k in (ord('q'), ord('Q')):
            return
        if k in DIRS:
            # Empêche demi-tour instantané
            ny, nx = DIRS[k]
            cy, cx = direction
            if (ny, nx) != (-cy, -cx):
                direction = (ny, nx)
                last_key = k

        # Déplacement selon la vitesse
        if (time.time() - last_move) * 1000.0 < speed_ms:
            time.sleep(0.001)
            continue
        last_move = time.time()

        # Calcul nouvelle tête
        dy, dx = direction
        head_y, head_x = snake[-1]
        new_head = (head_y + dy, head_x + dx)

        # Collisions murs
        if (new_head[0] <= 0 or new_head[0] >= BOARD_HEIGHT - 1 or
            new_head[1] <= 0 or new_head[1] >= BOARD_WIDTH - 1):
            best = max(best, score)
            break

        # Collisions corps
        if new_head in snake:
            best = max(best, score)
            break

        # Avance
        snake.append(new_head)

        # Manger
        if food and new_head == food:
            score += 1
            # Accélération progressive
            if score % SPEEDUP_EVERY == 0 and speed_ms > 30:
                speed_ms = max(30, speed_ms - SPEED_INCREMENT)
            food = new_food(snake, BOARD_HEIGHT, BOARD_WIDTH)
        else:
            snake.pop(0)  # pas mangé → enlève la queue

        render()

    # Écran de fin
    msg = f"Game Over  •  Score: {score}  •  Record: {best}"
    prompt = "Appuie sur Entrée pour rejouer, q pour quitter"
    stdscr.addstr(top + BOARD_HEIGHT // 2, max(0, (max_x - len(msg)) // 2), msg)
    stdscr.addstr(top + BOARD_HEIGHT // 2 + 2, max(0, (max_x - len(prompt)) // 2), prompt)
    stdscr.refresh()

    # Attente rejouer/quitter
    while True:
        k = stdscr.getch()
        if k in (ord('q'), ord('Q')):
            return
        if k in (ord('\n'), curses.KEY_ENTER):
            return main(stdscr)  # relance une partie
        time.sleep(0.01)

if __name__ == "__main__":
    curses.wrapper(main)


