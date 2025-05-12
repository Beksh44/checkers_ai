class Piece:
    """
    Base class for all checkers pieces (Man and King).

    Attributes:
        color (str): The piece's color, either 'white' (AI) or 'black' (player).
        position (tuple[int, int]): The (row, col) position on the board.
        is_king (bool): Whether the piece is a king.
        board (Board): Reference to the board the piece belongs to.
    """

    def __init__(self, color, position, board):
        self.color = color
        self.position = position
        self.is_king = False
        self.board = board

    def get_legal_moves(self, board):
        """Abstract method for getting legal moves. Must be implemented in subclasses."""
        raise NotImplementedError("Must be implemented in subclasses")

    def is_legal_move(self, end_pos, board):
        """Abstract method for checking if the move is legal. Must be implemented in subclasses."""
        raise NotImplementedError("Must be implemented in subclasses")

    def __str__(self):
        """Returns a string representation for printing the piece."""
        if self.color == 'white':
            return 'WM' if not self.is_king else 'WK'
        else:
            return 'BM' if not self.is_king else 'BK'


class Man(Piece):
    """
    Represents a non-king (basic) checkers piece.

    Attributes:
        color (str): The color of the piece ('white' or 'black').
        position (tuple[int, int]): The piece's current (row, col) position.
        board (Board): Reference to the game board this piece belongs to.

    Methods:
        get_legal_moves(board) -> list[tuple[int, int]]:
            Returns a list of legal destination positions.
            - If a capture is available, only capture moves are returned.
            - Otherwise, normal one-step diagonal moves are returned.

        is_legal_move(end_pos, board) -> bool:
            Checks whether the proposed move from current position to end_pos is valid.
    """

    def __init__(self, color, position, board):
        super().__init__(color, position, board)

    def get_legal_moves(self, board):
        """
        Returns a list of legal move positions for the Man.

        Prioritizes capture moves if any exist.
        - A Man can move diagonally forward one square if it's empty.
        - A Man can jump diagonally forward two squares if an opponent is in between.
        """
        row, col = self.position

        # Direction depends on color: black goes up, white goes down
        directions = [(-1, -1), (-1, 1)] if self.color == 'black' else [(1, -1), (1, 1)]

        captures = []  # List of possible capture moves
        moves = []  # List of possible normal moves

        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc

            # Check if destination is on the board and empty (normal move)
            if 0 <= new_row < len(board) and 0 <= new_col < len(board[0]):
                if board[new_row][new_col] is None:
                    moves.append((new_row, new_col))

            # Check for potential capture over opponent
            cap_row = row + 2 * dr
            cap_col = col + 2 * dc
            mid_row = row + dr
            mid_col = col + dc

            if (0 <= cap_row < len(board) and 0 <= cap_col < len(board[0]) and
                    board[cap_row][cap_col] is None):
                mid_piece = board[mid_row][mid_col]
                if mid_piece and mid_piece.color != self.color:
                    captures.append((cap_row, cap_col))

        # If captures are available, those must be played according to checkers rules
        return captures if captures else moves

    def is_legal_move(self, end_pos, board):
        """
        Checks whether a given move is legal.

        Parameters:
            end_pos (tuple[int, int]): Target position for the move.
            board (list[list[Piece or None]]): The current board state.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        start_row, start_col = self.position
        end_row, end_col = end_pos

        # Must stay on the board
        if not (0 <= end_row < len(board) and 0 <= end_col < len(board[0])):
            return False

        # Can't move to an occupied square
        if board[end_row][end_col] is not None:
            return False

        # Determine forward direction
        dir = -1 if self.color == "black" else 1

        # Regular one-step forward diagonal move
        if end_row == start_row + dir and abs(end_col - start_col) == 1:
            return True

        # Capture move (two-step jump over opponent)
        if end_row == start_row + 2 * dir and abs(end_col - start_col) == 2:
            mid_row = (start_row + end_row) // 2
            mid_col = (start_col + end_col) // 2
            mid_piece = board[mid_row][mid_col]
            if mid_piece and mid_piece.color != self.color:
                return True

        return False


class King(Piece):
    """
    Represents a king piece in checkers.

    Kings can move diagonally in all four directions (forward and backward),
    unlike normal pieces which can only move forward.

    Attributes:
        color (str): 'white' or 'black'
        position (tuple[int, int]): Current (row, col) position of the king on the board
        board (Board): Reference to the game board object
        is_king (bool): Always True for King pieces

    Methods:
        get_legal_moves(board) -> list[tuple[int, int]]:
            Returns all valid moves for this king, prioritizing captures if available.

        is_legal_move(end_pos, board) -> bool:
            Checks if the proposed move to end_pos is allowed for a king.
    """

    def __init__(self, color, position, board):
        super().__init__(color, position, board)
        self.is_king = True  # Ensure this piece is recognized as a king

    def get_legal_moves(self, board):
        """
        Returns all legal move destinations for this king piece.

        Kings move one step diagonally in any direction.
        If a capture (jump over opponent) is available, only capture moves are returned.

        Parameters:
            board (list[list[Piece or None]]): The current state of the board

        Returns:
            list[tuple[int, int]]: List of valid destination coordinates
        """
        row, col = self.position
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # All diagonal directions
        captures = []
        moves = []

        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc

            # Normal one-step move
            if 0 <= new_row < len(board) and 0 <= new_col < len(board[0]):
                if board[new_row][new_col] is None:
                    moves.append((new_row, new_col))

            # Check for capture
            cap_row = row + 2 * dr
            cap_col = col + 2 * dc
            mid_row = row + dr
            mid_col = col + dc

            if (0 <= cap_row < len(board) and 0 <= cap_col < len(board[0]) and
                    board[cap_row][cap_col] is None):
                mid_piece = board[mid_row][mid_col]
                if mid_piece and mid_piece.color != self.color:
                    captures.append((cap_row, cap_col))

        # If any captures are available, return only those (enforced rule)
        return captures if captures else moves

    def is_legal_move(self, end_pos, board):
        """
        Determines whether a proposed move is legal for a king.

        Kings:
            - Move one square diagonally (any direction), or
            - Jump over an adjacent opposing piece into an empty square beyond (capture)

        Parameters:
            end_pos (tuple[int, int]): The target row and column
            board (list[list[Piece or None]]): The current board configuration

        Returns:
            bool: True if the move is valid, False otherwise
        """
        start_row, start_col = self.position
        end_row, end_col = end_pos

        # Target must be on the board
        if not (0 <= end_row < len(board) and 0 <= end_col < len(board[0])):
            return False

        # Target square must be empty
        if board[end_row][end_col] is not None:
            return False

        row_diff = end_row - start_row
        col_diff = end_col - start_col

        # Must move diagonally (equal row/col difference)
        if abs(row_diff) != abs(col_diff):
            return False

        # One-step diagonal move is valid
        if abs(row_diff) == 1:
            return True

        # Two-step diagonal jump: possible capture
        if abs(row_diff) == 2:
            mid_row = (start_row + end_row) // 2
            mid_col = (start_col + end_col) // 2
            mid_piece = board[mid_row][mid_col]
            if mid_piece and mid_piece.color != self.color:
                return True

        return False
