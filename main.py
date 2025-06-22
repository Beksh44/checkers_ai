from front import load_piece_images, GameGUI
import tkinter as tk

# You can change the board size using BOARD_SIZE = '4x4' or BOARD_SIZE = '8x8'
BOARD_SIZE = '8x8'


def calculate_cell_size(screen_width, screen_height):
    usable_width = int(screen_width * 0.9)
    usable_height = int(screen_height * 0.9)
    if BOARD_SIZE == '8x8':
        rows, cols = 8, 8
    else:
        rows, cols = 4, 4
    return min(usable_width // cols, usable_height // rows)

if __name__ == "__main__":
    root = tk.Tk()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    cell_size = calculate_cell_size(screen_width, screen_height)

    load_piece_images(cell_size)

    gui = GameGUI(root, cell_size, board=BOARD_SIZE)
    root.mainloop()
