import pygame
import sys
import chess

WIDTH, HEIGHT = 480, 480
SQ_SIZE = WIDTH // 8
FPS = 60

LIGHT_SQ = (240, 217, 181)
DARK_SQ = (181, 136, 99)

BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (255, 255, 255)
ROOK_COLOR = (255, 165, 0)
KING_COLOR = (0, 100, 255)

HIGHLIGHT_COLOR = (50, 205, 50, 100)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT + 40))
pygame.display.set_caption("IA Blancas vs Usuario Negras")
clock = pygame.time.Clock()

font = pygame.font.SysFont('arial', 20)

def draw_board():
    for r in range(8):
        for c in range(8):
            color = LIGHT_SQ if (r + c) % 2 == 0 else DARK_SQ
            pygame.draw.rect(screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_piece(piece, row, col):
    center = (col * SQ_SIZE + SQ_SIZE // 2, row * SQ_SIZE + SQ_SIZE // 2)
    radius = SQ_SIZE // 3
    if piece.piece_type == chess.KING:
        color = WHITE_COLOR if piece.color == chess.WHITE else BLACK_COLOR
        pygame.draw.circle(screen, color, center, radius)
        pygame.draw.circle(screen, KING_COLOR, center, radius - 8, 3)
    elif piece.piece_type == chess.ROOK:
        color = ROOK_COLOR if piece.color == chess.WHITE else BLACK_COLOR
        rect = pygame.Rect(0, 0, SQ_SIZE // 2, SQ_SIZE // 2)
        rect.center = center
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK_COLOR, rect, 3)

def draw_pieces(board):
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row = 7 - (square // 8)
            col = square % 8
            draw_piece(piece, row, col)

def highlight_squares(selected_square, legal_moves):
    if selected_square is not None:
        row = 7 - (selected_square // 8)
        col = selected_square % 8
        s = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
        s.fill(HIGHLIGHT_COLOR)
        screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))

        for move in legal_moves:
            to_sq = move.to_square
            r = 7 - (to_sq // 8)
            c = to_sq % 8
            s.fill((50, 205, 50, 150))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

def draw_text(text, pos, color=BLACK_COLOR):
    img = font.render(text, True, color)
    screen.blit(img, pos)

PIECE_VALUES = {
    chess.KING: 0,
    chess.ROOK: 5,
}

def evaluate_board(board):
    if board.is_checkmate():
        return 9999 if board.turn == chess.BLACK else -9999
    elif board.is_stalemate():
        return 0

    value = 0
    king_square_black = None

    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            val = PIECE_VALUES.get(piece.piece_type, 0)
            if piece.color == chess.WHITE:
                value += val
                row, col = divmod(sq, 8)
                if 2 <= row <= 5 and 2 <= col <= 5:
                    value += 0.5
                if king_square_black is not None:
                    dist = chess.square_distance(sq, king_square_black)
                    value += max(0, (7 - dist) * 0.2)
            else:
                value -= val
                if piece.piece_type == chess.KING:
                    king_square_black = sq

    if king_square_black:
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if piece and piece.color == chess.WHITE:
                dist = chess.square_distance(sq, king_square_black)
                value += max(0, (7 - dist) * 0.2)

    return value

def minimax(board, depth, alpha, beta, is_maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    best_move = None
    if is_maximizing:
        max_eval = -float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval, _ = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval, _ = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

def main():
    board = chess.Board(None)  

   
    board.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
    board.set_piece_at(chess.A1, chess.Piece(chess.ROOK, chess.WHITE))

    board.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))

    board.turn = chess.WHITE  

    player_turn = False  
    selected_square = None
    legal_moves = []
    game_over = False
    result_msg = ""

    
    _, move = minimax(board, depth=3, alpha=-float('inf'), beta=float('inf'), is_maximizing=True)
    if move:
        board.push(move)
    player_turn = True  

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and player_turn and not game_over:
                x, y = pygame.mouse.get_pos()
                if y <= HEIGHT:
                    col = x // SQ_SIZE
                    row = y // SQ_SIZE
                    square = chess.square(col, 7 - row)
                    piece = board.piece_at(square)

                    if selected_square is None:
                        if piece and piece.color == chess.BLACK:
                            selected_square = square
                            legal_moves = [m for m in board.legal_moves if m.from_square == square]
                    else:
                        move = chess.Move(selected_square, square)
                        if move in legal_moves:
                            board.push(move)
                            player_turn = False
                        selected_square = None
                        legal_moves = []

        if not player_turn and not game_over:
            _, move = minimax(board, depth=3, alpha=-float('inf'), beta=float('inf'), is_maximizing=True)
            if move:
                board.push(move)
            player_turn = True

        draw_board()
        highlight_squares(selected_square, legal_moves)
        draw_pieces(board)

        if game_over:
            draw_text(result_msg, (10, HEIGHT + 10), (200, 0, 0))
        else:
            turn_text = "Turno: Usuario (Negras)" if player_turn else "Turno: (Blancas)"
            draw_text(turn_text, (10, HEIGHT + 10))

        pygame.display.flip()
        clock.tick(FPS)

        if not game_over:
            if board.is_checkmate():
                winner = "Usuario (Negras)" if board.turn == chess.WHITE else " (Blancas)"
                result_msg = f"¡Jaque mate! Gana {winner}."
                game_over = True
            elif board.is_stalemate():
                result_msg = "¡Empate por ahogado! Fin del juego."
                game_over = True

if __name__ == "__main__":
    main()


