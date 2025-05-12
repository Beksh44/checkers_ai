from front import load_piece_images, GameGUI
import tkinter as tk

ROWS, COLS = 4,4

def calculate_cell_size(screen_width, screen_height):
    usable_width = int(screen_width * 0.9)
    usable_height = int(screen_height * 0.9)
    return min(usable_width // COLS, usable_height // ROWS)

if __name__ == "__main__":
    root = tk.Tk()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    cell_size = calculate_cell_size(screen_width, screen_height)

    load_piece_images(cell_size)
    gui = GameGUI(root, cell_size)
    root.mainloop()
