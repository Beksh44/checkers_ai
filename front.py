from Board import Board
from PIL import Image, ImageTk
from minimax import get_ai_move
import tkinter as tk
import time

images = {}
ROWS, COLS = 4, 4


def load_piece_images(cell_size):
    """
    Loads and resizes piece images for the game and stores them in a global dictionary.

    Args:
        cell_size (int): The size (in pixels) of each board cell used to resize the images.

    Side Effects:
        Populates the global `images` dictionary with ImageTk.PhotoImage objects for:
        - "white"
        - "black"
        - "white_king"
        - "black_king"
    """
    global images
    image_dir = "images"
    for name in ["white", "black", "white_king", "black_king"]:
        path = f"{image_dir}/{name}.png"
        img = Image.open(path).resize((cell_size - 10, cell_size - 10), Image.LANCZOS)
        images[name] = ImageTk.PhotoImage(img)


class GameGUI:
    """
    The main GUI controller for the checkers game. Handles:
    - Drawing the board
    - Mapping backend pieces to visual ones
    - Running the AI
    - Handling game resets and end popups
    """

    def __init__(self, root, cell_size):
        """
        Initializes the game interface.

        Args:
            root (tk.Tk): The root window for the application.
            cell_size (int): The pixel dimension of each board square.
        """
        self.canvas = tk.Canvas(root, width=COLS * cell_size, height=ROWS * cell_size)
        self.canvas.pack()
        self.cell_size = cell_size

        self.draw_grid()  # Draw checkered board
        self.board = Board()  # Initialize game logic
        self.piece_map = {}  # Maps backend pieces to GraphicalPiece objects

        self.game_over = False

        # Show start screen and trigger delayed AI move
        self.popup(lambda: self.canvas.after(2000, self.ai_move), start_menu=True, text=None)

        # Create graphical pieces
        for row in self.board.board:
            for piece in row:
                if piece:
                    gpiece = GraphicalPiece(self.canvas, piece, self)
                    self.piece_map[piece] = gpiece

    def ai_move(self):
        """
        Executes a move for the AI player (white). Updates the canvas and logic state accordingly.
        If a promotion occurs, replaces the piece. Triggers end popup if the game ends.
        """
        if self.game_over:
            return

        best_move = get_ai_move(self.board)
        if not best_move:
            return

        start_pos, end_pos = best_move
        piece_to_change = self.board.board[start_pos[0]][start_pos[1]]  # Needed in case of promotion
        result = self.board.move_piece(start_pos, end_pos)

        if not result["moved"]:
            return

        new_row, new_col = end_pos
        moving_piece_backend = self.board.board[new_row][new_col]

        # Handle promotion
        if result["promoted"]:
            self.replace_piece(piece_to_change, result["promoted"])
            moving_piece = self.piece_map[moving_piece_backend]
        else:
            moving_piece = self.piece_map.get(moving_piece_backend)

        # Move the piece visually on the canvas
        if moving_piece:
            self.canvas.coords(
                moving_piece.piece_id,
                new_col * self.cell_size + self.cell_size // 2,
                new_row * self.cell_size + self.cell_size // 2
            )
            moving_piece.piece.position = (new_row, new_col)

        # Remove captured piece
        if result["captured"]:
            self.remove_piece(result["captured"])

        # End-of-game popup
        if result['game_over_text']:
            time.sleep(1)
            self.popup(self.reset_game, start_menu=False, text=result['game_over_text'])
            return

    def gui_lookup(self, backend_piece):
        """
        Looks up the graphical representation of a backend piece.

        Args:
            backend_piece (Piece): The logic (backend) piece object.

        Returns:
            GraphicalPiece or None: The GUI object mapped to the backend piece, if it exists.
        """
        return self.piece_map.get(backend_piece)

    def remove_piece(self, backend_piece):
        """
        Removes a graphical piece from the canvas and internal map.

        Args:
            backend_piece (Piece): The piece object to remove.

        Side Effects:
            - Deletes the image from the canvas.
            - Removes the mapping from piece_map.
        """
        gpiece = self.gui_lookup(backend_piece)
        if gpiece:
            gpiece.remove_from_board()
            del self.piece_map[backend_piece]

    def replace_piece(self, old_piece, new_piece):
        """
        Replaces a backend piece on the board (typically due to promotion) and updates GUI.

        Args:
            old_piece (Piece): The original piece to remove.
            new_piece (Piece): The new piece (e.g., King) to display in its place.

        Side Effects:
            - Removes the old graphical piece.
            - Creates a new one for the promoted piece.
            - Updates the piece_map accordingly.
        """
        self.remove_piece(old_piece)
        gpiece = GraphicalPiece(self.canvas, new_piece, self)
        self.piece_map[new_piece] = gpiece
        self.piece_map[new_piece].gui = self

    def draw_grid(self):
        """
        Draws the checkered board onto the canvas using alternating gray and white squares.
        """
        for row in range(ROWS):
            for col in range(COLS):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                color = "gray" if (row + col) % 2 == 0 else "white"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

    def popup(self, func, start_menu, text):
        """
        Displays a popup overlay window, either for starting or ending the game.

        Args:
            func (callable): A function to call when the popup is dismissed.
            start_menu (bool): Whether this is the initial welcome screen or an endgame screen.
            text (str or None): If not a start menu, displays a message (e.g. "White won!", "Draw").

        Side Effects:
            - Blocks interaction with canvas until user clicks the popup button.
            - Calls `func()` after closing the popup.
        """
        screen = tk.Frame(
            self.canvas.master,
            width=COLS * self.cell_size,
            height=ROWS * self.cell_size,
            bg="#1c1c1c"
        )
        screen.place(relx=0.5, rely=0.5, anchor="center")
        inner_frame = tk.Frame(screen, bg="#1c1c1c")
        inner_frame.pack(expand=True)

        # Title text
        title_text = "Welcome to Checkers" if start_menu else f"{text}!"
        title = tk.Label(
            inner_frame,
            text=title_text,
            font=("Helvetica", 36, "bold"),
            fg="white",
            bg="#222"
        )
        title.pack(pady=(60, 30))

        # Subtitle text
        subtitle_text = "Click to start a new game" if start_menu else "Would you like to play again?"
        subtitle = tk.Label(
            inner_frame,
            text=subtitle_text,
            font=("Helvetica", 18),
            fg="lightgray",
            bg="#222"
        )
        subtitle.pack(pady=(0, 40))

        # Button
        button_text = "Start Game" if start_menu else "Play again"
        button = tk.Button(
            inner_frame,
            text=button_text,
            font=("Helvetica", 18, "bold"),
            bg="#4CAF50",
            fg="black",
            padx=30,
            pady=15,
            relief="flat",
            activebackground="#388e3c",
            activeforeground="white",
            command=lambda: [screen.destroy(), func()]
        )
        button.pack(pady=10)
        screen.lift()

    def reset_game(self):
        """
        Resets the entire game state:
        - Clears the canvas.
        - Reinitializes the board and GUI pieces.
        - Triggers an AI move after 2 seconds.

        Side Effects:
            - Modifies canvas, board, and piece_map.
        """
        self.canvas.delete("all")
        self.board = Board()
        self.piece_map.clear()
        self.draw_grid()

        for row in self.board.board:
            for piece in row:
                if piece:
                    gpiece = GraphicalPiece(self.canvas, piece, self)
                    self.piece_map[piece] = gpiece

        self.canvas.after(2000, self.ai_move)


class GraphicalPiece:
    """
    Represents the graphical component of a checkers piece on the canvas.

    Attributes:
        canvas (tk.Canvas): The canvas where the piece is drawn.
        piece (Piece): The backend logic piece.
        gui (GameGUI): Reference to the main GUI for interaction.
        image (ImageTk.PhotoImage): The image used to represent the piece.
        piece_id (int): The canvas ID of the image object.
    """

    def __init__(self, canvas, piece, gui):
        """
        Initializes the graphical piece, places it on the canvas,
        and binds drag events if it's a player-controlled (black) piece.

        Args:
            canvas (tk.Canvas): The canvas to draw on.
            piece (Piece): The backend checkers piece.
            gui (GameGUI): The main GUI controller.
        """
        self.canvas = canvas
        self.piece = piece
        self.gui = gui
        self.image = images[f"{piece.color}" + ("_king" if self.piece.is_king else '')]

        # Draw the piece centered in the cell
        self.piece_id = self.canvas.create_image(
            piece.position[1] * self.gui.cell_size + self.gui.cell_size // 2,
            piece.position[0] * self.gui.cell_size + self.gui.cell_size // 2,
            image=self.image,
            anchor="center"
        )

        # Allow only black pieces (player-controlled) to be draggable
        if self.piece.color == "black":
            self.canvas.tag_bind(self.piece_id, "<ButtonPress-1>", self.on_drag_start)
            self.canvas.tag_bind(self.piece_id, "<B1-Motion>", self.on_drag)
            self.canvas.tag_bind(self.piece_id, "<ButtonRelease-1>", self.on_drag_end)

    def remove_from_board(self):
        """
        Deletes the piece's image from the canvas.
        """
        self.canvas.delete(self.piece_id)

    def on_drag_start(self, event):
        """
        Called when the player starts dragging a piece.

        Args:
            event (tk.Event): The mouse event with coordinates.
        """
        self.start_x = event.x
        self.start_y = event.y

    def on_drag(self, event):
        """
        Called during dragging. Moves the piece image on the canvas.

        Args:
            event (tk.Event): The current mouse event.
        """
        x = min(max(event.x, 0), self.gui.cell_size * 4)
        y = min(max(event.y, 0), self.gui.cell_size * 4)
        dx = x - self.start_x
        dy = y - self.start_y
        self.canvas.move(self.piece_id, dx, dy)
        self.start_x = x
        self.start_y = y

    def snap_back(self):
        """
        Moves the piece image back to its original grid position (used on illegal move).
        """
        self.canvas.coords(
            self.piece_id,
            self.piece.position[1] * self.gui.cell_size + self.gui.cell_size // 2,
            self.piece.position[0] * self.gui.cell_size + self.gui.cell_size // 2
        )

    def on_drag_end(self, event):
        """
        Called when the player drops a piece. Attempts to make the move.

        Args:
            event (tk.Event): The mouse release event.
        """
        max_row, max_col = 3, 3  # Grid limits for 4x4 board
        new_col = min(max(0, event.x // self.gui.cell_size), max_col)
        new_row = min(max(0, event.y // self.gui.cell_size), max_row)

        result = self.piece.board.move_piece(self.piece.position, (new_row, new_col))

        if not result["moved"]:
            self.snap_back()
            return
        else:
            # Move piece to new position visually
            self.canvas.coords(
                self.piece_id,
                new_col * self.gui.cell_size + self.gui.cell_size // 2,
                new_row * self.gui.cell_size + self.gui.cell_size // 2
            )
            self.piece.position = (new_row, new_col)

        # Remove captured piece visually
        if result["captured"]:
            self.gui.remove_piece(result["captured"])

        # Replace with king piece if promoted
        if result["promoted"]:
            self.gui.replace_piece(self.piece, result["promoted"])

        # Trigger AI move if player's move is complete
        if self.piece.board.last_move_color == 'black':
            self.canvas.after(150, self.gui.ai_move)

        # Handle game over
        if result['game_over_text']:
            self.gui.popup(self.gui.reset_game, False, result['game_over_text'])
            self.gui.game_over = True
            return
