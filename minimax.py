def get_ai_move(board, depth=15):
    """
    Determines the best move for the AI using the minimax algorithm.

    Parameters:
        board (Board): The current game board.
        depth (int): The maximum depth for the minimax search.

    Returns:
        tuple: The best move as ((start_row, start_col), (end_row, end_col)), or None if no move is possible.
    """
    _, best_move = minimax(board, depth, float('-inf'), float('inf'), maximizing_player=True)
    return best_move


def minimax(board, depth, alpha, beta, maximizing_player):
    """
    Minimax algorithm with alpha-beta pruning to find the optimal move.

    Parameters:
        board (Board): The current game board state.
        depth (int): Remaining depth to evaluate.
        alpha (float): Best already explored option along the path to the root for the maximizer.
        beta (float): Best already explored option along the path to the root for the minimizer.
        maximizing_player (bool): True if it's AI's turn (white), False for the player (black).

    Returns:
        tuple: (evaluation score, best move)
            - evaluation score (int): Numerical value of board state.
            - best move (tuple): Best move as ((start_row, start_col), (end_row, end_col)), or None.
    """
    if depth == 0 or board.game_over():
        # Base case: reached depth limit or game is over
        return board.evaluate_board(), None

    color = 'white' if maximizing_player else 'black'  # Determine player color
    best_move = None
    moves = board.get_all_moves(color)  # List of possible legal moves

    if not moves:
        # No legal moves available, return neutral score
        return 0, None

    if maximizing_player:
        max_eval = float('-inf')
        for move in moves:
            new_board = board.copy()
            new_board.move_piece(*move)
            eval, _ = minimax(new_board, depth - 1, alpha, beta, False)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Prune the search tree
        return max_eval, best_move

    else:
        min_eval = float('inf')
        for move in moves:
            new_board = board.copy()
            new_board.move_piece(*move)
            eval, _ = minimax(new_board, depth - 1, alpha, beta, True)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Prune the search tree
        return min_eval, best_move
