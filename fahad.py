import pygame
import sys

# AUDIO SETTINGS 

BACKGROUND_MUSIC = r"D:\Tic tac toe CSE200L\background_music.mp3"
CLICK_SOUND = r"D:\Tic tac toe CSE200L\click.wav"
WIN_SOUND = r"D:\Tic tac toe CSE200L\win.wav"

try:
    pygame.mixer.init()
except Exception as e:
    print("Warning: mixer init failed:", e)

try:
    pygame.mixer.music.load(BACKGROUND_MUSIC)
    pygame.mixer.music.play(-1)
except Exception:

    print("Background music missing or failed to load.")

try:
    click_sfx = pygame.mixer.Sound(CLICK_SOUND)
except Exception:
    click_sfx = None
    print("Click sound missing.")

try:
    win_sfx = pygame.mixer.Sound(WIN_SOUND)
except Exception:
    win_sfx = None
    print("Win sound missing.")

# DISPLAY SETTINGS 

# RGB color codes : Red (255, 0, 0), Green (0, 255, 0), Blue (0, 0, 255),
# Pink (255, 192, 203), White (255, 255, 255), Yellow (255, 255, 0), Violet (238, 130, 238),
# Indigo (75, 0, 130), Orange (255, 165, 0), Black (0, 0, 0), Gray (128, 128, 128),
# Brown (165, 42, 42), Purple (128, 0, 128), Cyan (0, 255, 255), Magenta (255, 0, 255),
# Sky Blue (135, 206, 235), Lime (0, 255, 0), Gold (255, 215, 0), Silver (192, 192, 192).


WIDTH = 600
HEIGHT = 650
CELL_SIZE = WIDTH // 3
LINE_WIDTH = 5

BG_COLOR = (192, 192, 192)
WHITE = (255, 255, 255)
BLACK = (165, 42, 42)
GRAY = (180, 180, 180)

X_COLOR = (75, 0,130)
O_COLOR = (0, 128, 0)

BUTTON_WIDTH = 100
BUTTON_HEIGHT = 55
BUTTON_COLOR = (230, 230, 230)
BUTTON_BORDER = BLACK
BUTTON_HOVER = (200, 200, 200)
BUTTON_TEXT = BLACK

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe")

FONT_LARGE = pygame.font.SysFont(None, 72)
FONT_MED = pygame.font.SysFont(None, 36)
FONT_SMALL = pygame.font.SysFont(None, 28)

clock = pygame.time.Clock()

# GAME STATE 

board = [[None] * 3 for _ in range(3)]
current_player = "X"
game_over = False
winner = None
winning_line = None
show_popup = False
popup_start_time = 0
POPUP_DURATION = 2


# MENU

def draw_button(text, x, y, width, height):
    mouse = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, width, height)
    hovered = rect.collidepoint(mouse)

    color = BUTTON_HOVER if hovered else BUTTON_COLOR
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BUTTON_BORDER, rect, 2)

    txt = FONT_MED.render(text, True, BUTTON_TEXT)
    screen.blit(txt, txt.get_rect(center=rect.center))
    return rect


def menu_screen():
    while True:
        screen.fill(BG_COLOR)
        title = FONT_LARGE.render("Tic Tac Toe", True, BLACK)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 120)))

        start_btn = draw_button("Start Game", WIDTH // 2 - 100, 300, 200, 60)
        quit_btn = draw_button("Quit", WIDTH // 2 - 100, 380, 200, 60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_btn.collidepoint(event.pos):
                    return
                if quit_btn.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        clock.tick(60)


# GAME FUNCTIONS

def reset_game():
    global board, current_player, game_over, winner, winning_line, show_popup
    board = [[None] * 3 for _ in range(3)]
    current_player = "X"
    game_over = False
    winner = None
    winning_line = None
    show_popup = False


def draw_grid():
    pygame.draw.line(screen, BLACK, (CELL_SIZE, 0), (CELL_SIZE, WIDTH), LINE_WIDTH)
    pygame.draw.line(screen, BLACK, (CELL_SIZE * 2, 0), (CELL_SIZE * 2, WIDTH), LINE_WIDTH)
    pygame.draw.line(screen, BLACK, (0, CELL_SIZE), (WIDTH, CELL_SIZE), LINE_WIDTH)
    pygame.draw.line(screen, BLACK, (0, CELL_SIZE * 2), (WIDTH, CELL_SIZE * 2), LINE_WIDTH)


def draw_marks():
    for r in range(3):
        for c in range(3):
            if board[r][c] == "X":
                draw_x(r, c)
            elif board[r][c] == "O":
                draw_o(r, c)


def draw_x(row, col):
    pad = 50
    x1 = col * CELL_SIZE + pad
    y1 = row * CELL_SIZE + pad
    x2 = (col + 1) * CELL_SIZE - pad
    y2 = (row + 1) * CELL_SIZE - pad
    pygame.draw.line(screen, X_COLOR, (x1, y1), (x2, y2), LINE_WIDTH)
    pygame.draw.line(screen, X_COLOR, (x1, y2), (x2, y1), LINE_WIDTH)


def draw_o(row, col):
    center = (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2)
    pygame.draw.circle(screen, O_COLOR, center, CELL_SIZE // 2 - 20, LINE_WIDTH)


def check_winner():
    # rows
    for r in range(3):
        if board[r][0] == board[r][1] == board[r][2] != None:
            return board[r][0], ('row', r)

    # columns
    for c in range(3):
        if board[0][c] == board[1][c] == board[2][c] != None:
            return board[0][c], ('col', c)

    # diagonals
    if board[0][0] == board[1][1] == board[2][2] != None:
        return board[0][0], ('diag1',)

    if board[0][2] == board[1][1] == board[2][0] != None:
        return board[0][2], ('diag2',)

    # DRAW CHECK
    for row in board:
        if None in row:
            return None, None  # not a draw yet

    return "Draw", None


def draw_winning_line(line_info):
    if not line_info:
        return

    kind = line_info[0]

    if kind == "row":
        r = line_info[1]
        y = r * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.line(screen, (0, 255, 0), (15, y), (WIDTH - 15, y), 10)

    elif kind == "col":
        c = line_info[1]
        x = c * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.line(screen, (0, 255, 0), (x, 15), (x, WIDTH - 15), 10)

    elif kind == "diag1":
        pygame.draw.line(screen, (0, 255, 0), (15, 15), (WIDTH - 15, WIDTH - 15), 10)

    elif kind == "diag2":
        pygame.draw.line(screen, (0, 255, 0), (WIDTH - 15, 15), (15, WIDTH - 15), 10)


def draw_restart_button():
    mouse = pygame.mouse.get_pos()
    x = WIDTH // 2 - BUTTON_WIDTH // 2
    y = HEIGHT - BUTTON_HEIGHT - 15
    rect = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)

    hover = rect.collidepoint(mouse)
    color = BUTTON_HOVER if hover else BUTTON_COLOR

    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)

    txt = FONT_SMALL.render("Restart", True, BLACK)
    screen.blit(txt, txt.get_rect(center=rect.center))

    return rect


def draw_popup(text):
    popup_w = 420
    popup_h = 140
    popup_x = (WIDTH - popup_w) // 2
    popup_y = (HEIGHT - popup_h) // 2

    box = pygame.Rect(popup_x, popup_y, popup_w, popup_h)
    pygame.draw.rect(screen, BLACK, box)

    txt = FONT_MED.render(text, True, WHITE)
    screen.blit(txt, txt.get_rect(center=box.center))


# MAIN LOOP

menu_screen()

running = True
while running:
    screen.fill(BG_COLOR)
    draw_grid()
    draw_marks()

    restart_btn = draw_restart_button()

    if game_over and winner != "Draw":
        draw_winning_line(winning_line)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # Restart button
            if restart_btn.collidepoint(mx, my):
                reset_game()
                if click_sfx:
                    click_sfx.play()
                continue

            if not game_over:
                row = my // CELL_SIZE
                col = mx // CELL_SIZE

                if 0 <= row < 3 and 0 <= col < 3 and board[row][col] is None:
                    board[row][col] = current_player
                    if click_sfx:
                        click_sfx.play()

                    winner, winning_line = check_winner()
                    if winner:
                        game_over = True
                        show_popup = True
                        popup_start_time = pygame.time.get_ticks()
                        if win_sfx:
                            win_sfx.play()
                    else:
                        current_player = "O" if current_player == "X" else "X"

    # SHOW POPUP (WIN or DRAW)
    if show_popup:
        if winner == "Draw":
            draw_popup("It's a Draw!")
        else:
            draw_popup(f"Player {winner} Wins!")

        if pygame.time.get_ticks() - popup_start_time > POPUP_DURATION * 1000:
            show_popup = False

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
