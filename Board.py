from checkers import Man, King
import copy

class Board:
    """
    Represents the game state of a 4x4 checkers game.

    Responsibilities:
    - Maintains the 2D board and active pieces
    - Handles move execution, capturing, and promotion
    - Provides board evaluation and move generation for AI
    - Detects game over and draw states
    Attributes:
        white_pieces (list): List of all white pieces on the board.
        black_pieces (list): List of all black pieces on the board.
        last_move_color (str): Color ('white' or 'black') of the player who made the last move.
        board (list of lists): 2D array representing the game board.
        no_progress_counter (int): Counter tracking number of moves without capture or promotion.
    """
    def __init__(self, board = '8x8'):
        self.white_pieces = []
        self.black_pieces = []
        self.last_move_color = 'black'

        if board == '4x4':
            self.board = self.create_board_4x4()
        elif board == '8x8':
            self.board = self.create_board_8x8()

        self.no_progress_counter = 0 # For detecting draw by inactivity

    def create_board_4x4(self) -> list:
        """
        Initializes a 4x4 board with two white and two black pieces in starting positions.
         Returns:
            list: The initialized 4x4 board.
        """
        board = [[None for _ in range(4)] for _ in range(4)]

        # Place white pieces
        for col in [0, 2]:
            man = Man('white', (0, col), self)
            board[0][col] = man
            self.white_pieces.append(man)

        # Place black pieces
        for col in [1, 3]:
            man = Man('black', (3, col), self)
            board[3][col] = man
            self.black_pieces.append(man)

        return board

    def create_board_8x8(self) -> list:
        """
        Initializes a 8x8 board with two white and two black pieces in starting positions.
         Returns:
            list: The initialized 8x8 board.
        """
        board = [[None for _ in range(8)] for _ in range(8)]

        # Place white pieces
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:
                    man = Man('white', (row, col), self)
                    board[row][col] = man
                    self.white_pieces.append(man)

        # Place black pieces
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    man = Man('black', (row, col), self)
                    board[row][col] = man
                    self.black_pieces.append(man)

        return board

    def move_piece(self, start_pos, end_pos):
        """
        Attempts to move a piece from start_pos to end_pos.
        Args:
            start_pos (tuple): (row, col) of the starting position.
            end_pos (tuple): (row, col) of the ending position.

        Returns:
            dict: A dictionary with keys:
                - 'moved' (bool): Whether the move was successful.
                - 'start' (tuple): Starting position.
                - 'end' (tuple): Ending position.
                - 'captured' (Piece or None): Captured piece, if any.
                - 'promoted' (Piece or None): Promoted piece, if any.
                - 'game_over_text' (str or None): Game over message, if game ends.
        """
        result = {
            "moved": False,
            "start": start_pos,
            "end": end_pos,
            "captured": None,
            "promoted": None,
            "game_over_text": None
        }

        start_row, start_col = start_pos
        end_row, end_col = end_pos
        start_piece = self.board[start_row][start_col]

        # Validation
        if start_piece is None:
            print("No piece at starting position.")
            return result
        if self.last_move_color == start_piece.color:
            print("Not your turn.")
            return result
        if not start_piece.is_legal_move(end_pos, self.board):
            print("Illegal move.")
            return result

        result["moved"] = True

        # Handle capture
        if abs(end_row - start_row) == 2 and abs(end_col - start_col) == 2:
            mid_row = (start_row + end_row) // 2
            mid_col = (start_col + end_col) // 2
            captured = self.board[mid_row][mid_col]
            if captured:
                if captured.color == 'white':
                    self.white_pieces.remove(captured)
                else:
                    self.black_pieces.remove(captured)
                self.board[mid_row][mid_col] = None
                result["captured"] = captured

        # Move piece
        self.board[end_row][end_col] = start_piece
        self.board[start_row][start_col] = None
        start_piece.position = (end_row, end_col)

        # Handle promotion
        if isinstance(start_piece, Man):
            should_promote = (
                    (start_piece.color == "black" and end_row == 0) or
                    (start_piece.color == "white" and end_row == len(self.board) - 1)
            )
            if should_promote:
                promoted_king = King(start_piece.color, (end_row, end_col), self)
                self.board[end_row][end_col] = promoted_king
                result["promoted"] = promoted_king
                piece_list = self.white_pieces if start_piece.color == 'white' else self.black_pieces
                piece_list.remove(start_piece)
                piece_list.append(promoted_king)

        self.last_move_color = start_piece.color

        # Game state checks
        if self.game_over():
            winner = 'white' if self.white_pieces else 'black'
            result["game_over_text"] = f"{winner} won!"
        elif self.draw():
            result["game_over_text"] = "Draw!"

        # Update no-progress counter
        if result["captured"] or result["promoted"]:
            self.no_progress_counter = 0
        else:
            self.no_progress_counter += 1

        return result

    def print_board(self):
        """
        Prints the current board state to the console.
        """
        for row in self.board:
            print(' '.join(str(piece) if piece else '..' for piece in row))
        print()

    def evaluate_board(self) -> int:
        """
        Evaluates the board score from white's perspective.

        Returns:
            int: Positive score favors white, negative favors black.
        """
        score = 0
        for row in self.board:
            for piece in row:
                if piece is None:
                    continue
                value = 2 if isinstance(piece, King) else 1
                score += value if piece.color == 'white' else -value
        return score

    def get_all_moves(self, color) -> list:
        """
        Gets all legal moves for a given color.

        Args:
            color (str): 'white' or 'black'

        Returns:
            list of tuples: Each move is ((start_row, start_col), (end_row, end_col))
        """
        moves = []
        pieces = self.white_pieces if color == 'white' else self.black_pieces

        for piece in pieces:
            start_pos = piece.position
            for end_pos in piece.get_legal_moves(self.board):
                moves.append((start_pos, end_pos))

        return moves

    def game_over(self):
        """
        Checks whether the game is over (one player has no pieces).

        Returns:
            bool: True if game is over.
        """
        return len(self.white_pieces) == 0 or len(self.black_pieces) == 0

    def draw(self) -> bool:
        """
        Determines if the game is a draw (no legal moves or stagnation).

        Returns:
            bool: True if draw.
        """
        if (not self.get_all_moves('white') and self.last_move_color == 'black') or \
                (not self.get_all_moves('black') and self.last_move_color == 'white'):
            return True
        return self.no_progress_counter >= 20

    def copy(self):
        """
        Returns a deep copy of the board.

        Returns:
            Board: A deep copied board instance.
        """
        return copy.deepcopy(self)


