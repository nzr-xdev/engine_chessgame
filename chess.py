from abc import ABC, abstractmethod
import pygame

class figure(ABC):

    def __init__(self, color, position):
        self.color = color #white / black
        self.position = position #(0,0) 
        self.has_moved = False
        self.actual_moves = []

    @abstractmethod
    def get_valid_moves(self, matrix, game):

        self.actual_moves = []

        pass

    def get_attack_zones(self, matrix):
        self.attack_zones = []
        
        if hasattr(self, 'directions'):
            for dy, dx in self.directions:
                pos1, pos2 = self.position[0] + dy, self.position[1] + dx
                while 0 <= pos1 < 8 and 0 <= pos2 < 8:
                    target = matrix[pos1][pos2]
                    self.attack_zones.append((pos1, pos2))
                    if target is not None:
                        break
                    pos1 += dy
                    pos2 += dx
        
        elif hasattr(self, 'accesability'):
            for dy, dx in self.accesability:
                pos1, pos2 = self.position[0] + dy, self.position[1] + dx
                if 0 <= pos1 < 8 and 0 <= pos2 < 8:
                    self.attack_zones.append((pos1, pos2))

    def longrangefigure(self, matrix):
        for dy, dx in self.directions:
            pos1, pos2 = self.position[0] + dy, self.position[1] + dx

            while 0 <= pos1 < 8 and 0 <= pos2 < 8:
                target = matrix[pos1][pos2]
                
                if target is None:
                    self.actual_moves.append((pos1, pos2))
                else:
                    if self.color != target.color:
                        self.actual_moves.append((pos1, pos2))
                    break
                
                pos1 += dy
                pos2 += dx

    def __str__(self):
        return self.symbol

class Pawn(figure):

    def __init__(self, color:str, position: tuple[int, int]):

        super().__init__(color, position)

        if self.color == 'White':
            self.img = 'assets/wp.png'
            self.accesability = [(-1, 0), (-1, -1), (-1, 1)]
        else: 
            self.img = 'assets/bp.png'
            self.accesability = [(1, 0), (1, -1), (1, 1)]

    def get_attack_zones(self, matrix):
        self.attack_zones = []
        moves = [(-1, -1), (-1, 1)] if self.color == 'White' else [(1, -1), (1, 1)]
        for dy, dx in moves:
            pos1, pos2 = self.position[0] + dy, self.position[1] + dx
            if 0 <= pos1 < 8 and 0 <= pos2 < 8:
                self.attack_zones.append((pos1, pos2))

    def check_for_promotion(self, screen):

        if self.position[0] == 0:
            #rectangle
                w, h = 410, 120
                if self.color == 'White':
                    rec_y = 50+100-10
                else: 
                    rec_y = 50+100-10+500
                
                pos2=4
                if pos2 in [0,1,2,3]:
                    rec_x = 50+100*(pos2)
                else:
                    d = pos2 - 4
                    rec_x = 900-50-710+100*(d)
                
                win_overlay = pygame.Surface((w, h), pygame.SRCALPHA) 
                win_overlay.fill((70, 70, 70, 240)) 
                screen.blit(win_overlay, (rec_x, rec_y))
                # figures
                
                if self.color == 'White': fig_to_chose = ['assets/wq.png', 'assets/wn.png', 'assets/wr.png', 'assets/wb.png']
                else: fig_to_chose = ['assets/bq.png', 'assets/bn.png', 'assets/br.png', 'assets/bb.png']

                for i in range(4):
                    x = rec_x+10+100*i
                    y = rec_y-10
                    img_path = fig_to_chose[i]
                    try:

                        img = pygame.image.load(img_path)
                        img_width, img_height = img.get_size()

                        target_size = 100
                        ratio = target_size / max(img_width, img_height)
                        img_width, img_height = int(img_width * ratio), int(img_height * ratio)
                        img = pygame.transform.smoothscale(img, (img_width, img_height))

                        screen.blit(img, (x, y))
                    except Exception as e:
                        print(f'Помилка: {e}')

    def get_valid_moves(self, matrix, game):

        super().get_valid_moves(matrix, game)
        new_accesability = list(self.accesability)
        if not self.has_moved:
            if self.color == 'White': new_accesability.append((-2, 0))
            else: new_accesability.append((2, 0))            
        
        if game.en_passant_target:
            target_y, target_x = game.en_passant_target
            if abs(self.position[1] - target_x) == 1:
                if (self.color == 'White' and self.position[0] == 3 and target_y == 2) or \
                    (self.color == 'Black' and self.position[0] == 4 and target_y == 5):
                    self.actual_moves.append((target_y, target_x))

        for choosed_move in new_accesability:
            pos1, pos2 = self.position[0] + choosed_move[0], self.position[1] + choosed_move[1]

            if 0 <= pos1 < 8 and 0 <= pos2 < 8:
                target = matrix[pos1][pos2]

                if target == None:

                    if choosed_move in [(-1, 0), (1, 0)]:
                        self.actual_moves.append((pos1, pos2))
                    
                    elif choosed_move in [(-2, 0), (2, 0)]:

                        mid_row = pos1 + (1 if self.color == 'White' else -1)
                        if matrix[mid_row][pos2] is None:
                            self.actual_moves.append((pos1, pos2))
                else:
                    if choosed_move in [(-1, -1), (-1, 1), (1, 1), (1, -1)] and self.color != target.color:
                        self.actual_moves.append((pos1, pos2))


        pass

class Knight(figure):

    def __init__(self, color:str, position: tuple[int, int]):

        super().__init__(color, position)

        if self.color == 'White':
            self.img = 'assets/wn.png'
        else: 
            self.img = 'assets/bn.png'

        self.accesability = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
    

    def get_valid_moves(self, matrix, game):

        super().get_valid_moves(matrix, game)

        for choosed_move in self.accesability:
            
            pos1, pos2 = self.position[0]+choosed_move[0], self.position[1]+choosed_move[1]

            if pos1 in range(8) and pos2 in range(8): #заборона виступу за дошку
                
                target = matrix[pos1][pos2]

                if target == None:
                    
                    self.actual_moves.append((pos1, pos2))
                    
                else:
                    if self.color != target.color:
                        self.actual_moves.append((pos1, pos2))



            else:
                pass
        

        pass

class Bishop(figure):

    def __init__(self, color:str, position: tuple[int, int]):

        super().__init__(color, position)

        if self.color == 'White':
            self.img = 'assets/wb.png'
        else: 
            self.img = 'assets/bb.png'

        self.directions = [(1, 1), (-1, -1), (-1, 1), (1, -1)]
    

    def get_valid_moves(self, matrix, game):
        super().get_valid_moves(matrix, game)
        self.longrangefigure(matrix)

class Rook(figure):

    def __init__(self, color:str, position: tuple[int, int]):

        super().__init__(color, position)

        if self.color == 'White':
            self.img = 'assets/wr.png'
        else: 
            self.img = 'assets/br.png'

        self.directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]


    def get_valid_moves(self, matrix, game):
        super().get_valid_moves(matrix, game)
        self.longrangefigure(matrix)

class Queen(figure):

    def __init__(self, color:str, position: tuple[int, int]):

        super().__init__(color, position)

        if self.color == 'White':
            self.img = 'assets/wq.png'
        else: 
            self.img = 'assets/bq.png'

        self.directions = [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
    

    def get_valid_moves(self, matrix, game):
        super().get_valid_moves(matrix, game)
        self.longrangefigure(matrix)

class King(figure):

    def __init__(self, color:str, position: tuple[int, int]):

        super().__init__(color, position)

        if self.color == 'White':
            self.img = 'assets/wk.png'
        else: 
            self.img = 'assets/bk.png'

        self.accesability = [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
    

    def get_valid_moves(self, matrix, game):
        super().get_valid_moves(matrix, game)
        y = 7 if self.color == 'White' else 0
        opp_color = 'Black' if self.color == 'White' else 'White'

        if not self.has_moved and not game.is_attacked(self.position, opp_color, matrix):
            left_rook = matrix[y][0]
            if isinstance(left_rook, Rook) and not left_rook.has_moved:
                if all(matrix[y][i] is None for i in range(1, 4)):
                    if not any(game.is_attacked((y, i), opp_color, matrix) for i in range(2, 4)):
                        self.actual_moves.append((y, 2))

            right_rook = matrix[y][7]
            if isinstance(right_rook, Rook) and not right_rook.has_moved:
                if all(matrix[y][i] is None for i in range(5, 7)):
                    if not any(game.is_attacked((y, i), opp_color, matrix) for i in range(5, 7)):
                        self.actual_moves.append((y, 6))

        for dy, dx in self.accesability:
            pos1, pos2 = self.position[0] + dy, self.position[1] + dx
            if 0 <= pos1 < 8 and 0 <= pos2 < 8:
                target = matrix[pos1][pos2]
                if target is None or target.color != self.color:
                    self.actual_moves.append((pos1, pos2))
        

        pass


class board:

    def __init__(self):
        self.matrix = [[None for _ in range(8)] for _ in range(8)]
        self.setup_pieces()
    
    def setup_pieces(self):

        # Pawns White[6, 0-7] Black[1, 0-7]

        for pos in range(8):
            self.matrix[6][pos] = Pawn('White', (6,pos))
        for pos in range(8):
            self.matrix[1][pos] = Pawn('Black', (1,pos))

        #Knights White [7, 1], [7, 6], Black [0, 1] [0, 6]

        self.matrix[7][1] = Knight('White', (7, 1))
        self.matrix[7][6] = Knight('White', (7, 6))
        self.matrix[0][1] = Knight('Black', (0, 1))
        self.matrix[0][6] = Knight('Black', (0, 6))

        #Bishops White [7, 2], [7, 5], Black [0, 2] [0, 5]

        self.matrix[7][2] = Bishop('White', (7, 2))
        self.matrix[7][5] = Bishop('White', (7, 5))
        self.matrix[0][2] = Bishop('Black', (0, 2))
        self.matrix[0][5] = Bishop('Black', (0, 5))

        #Rooks White [7, 7], [7, 0], Black [0, 0] [0, 7]

        self.matrix[7][7] = Rook('White', (7, 7))
        self.matrix[7][0] = Rook('White', (7, 0))
        self.matrix[0][0] = Rook('Black', (0, 0))
        self.matrix[0][7] = Rook('Black', (0, 7))

        # Queen White [7, 3], Black [0, 3]
        self.matrix[7][3] = Queen('White', (7, 3))
        self.matrix[0][3] = Queen('Black', (0, 3))

        # King White [7, 4], Black [0, 4]
        self.matrix[7][4] = King('White', (7, 4))
        self.matrix[0][4] = King('Black', (0, 4))

        pass
    
    def update_move(self, current_pos, move_pos, game):
        piece = self.matrix[current_pos[0]][current_pos[1]]

        if isinstance(piece, Pawn) and move_pos == game.en_passant_target:
            self.matrix[current_pos[0]][move_pos[1]] = None

        game.en_passant_target = None
        if isinstance(piece, Pawn) and abs(current_pos[0] - move_pos[0]) == 2:
            game.en_passant_target = ((current_pos[0] + move_pos[0]) // 2, current_pos[1])

        if isinstance(piece, King) and abs(current_pos[1] - move_pos[1]) == 2:
            y = move_pos[0]
            if move_pos[1] == 2: 
                rook = self.matrix[y][0]
                self.matrix[y][3], self.matrix[y][0] = rook, None
                rook.position = (y, 3)
                rook.has_moved = True
            elif move_pos[1] == 6: 
                rook = self.matrix[y][7]
                self.matrix[y][5], self.matrix[y][7] = rook, None
                rook.position = (y, 5)
                rook.has_moved = True

        piece.has_moved = True
        piece.position = move_pos
        self.matrix[move_pos[0]][move_pos[1]] = piece
        self.matrix[current_pos[0]][current_pos[1]] = None
    

    def display(self):
        for row in self.matrix:
            print("".join([str(p) if p else "." for p in row]))

class Game:

    def __init__(self):
        self.turn = 'White'
        self.selected_piece = None
        self.game_active = True
        self.game_winner = 'No one'
        self.promotion_pending = False
        self.promotion_pawn = None
        self.prom_pawm_check = None
        self.pat_win = False
        self.en_passant_target = None

    def change_turn(self):
        if self.turn == 'White': self.turn = 'Black'
        else: self.turn = 'White'

    def draw_board(self, screen, matrix):

        colours = {
            'WHITE' : (255, 255, 255),
            'LIGHT_BROWN' : (240, 217, 181),
            'DARK_BROWN': (112, 84, 62), 
            'BLACK' : (0, 0, 0)
            }

        pygame.font.init()
        font = pygame.font.SysFont('Arial', 20, bold=True)

        screen.fill(color=colours['WHITE'])
        offset = 50
        cell_size = 100

        for row in range(8):
            for col in range(8): 
                if (row + col) % 2 == 0:
                    color = colours['LIGHT_BROWN']
                else:
                    color = colours['DARK_BROWN']
                
                pygame.draw.rect(screen, color, (offset + col * cell_size, offset + row * cell_size, cell_size, cell_size))

        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        numbers = ['8', '7', '6', '5', '4', '3', '2', '1']

        for i in range(8):
            char_surface = font.render(letters[i], True, colours['BLACK'])

            screen.blit(char_surface, (offset + i * cell_size + 40, 15))
            screen.blit(char_surface, (offset + i * cell_size + 40, 15))
            screen.blit(char_surface, (offset + i * cell_size + 40, offset + 8 * cell_size + 10)) 

            num_surface = font.render(numbers[i], True, colours['BLACK'])
            screen.blit(num_surface, (15, offset + i * cell_size + 35)) 
            screen.blit(num_surface, (offset + 8 * cell_size + 20, offset + i * cell_size + 35))


        pass

    def draw_pieces(self, screen, matrix):
        
        offset = 50
        cell_size = 100

        for row in range(8):
            for col in range(8):
                item = matrix[row][col]
                if item != None:
                    img_path = item.img
                    try:

                        img = pygame.image.load(img_path)
                        img_width, img_height = img.get_size()
                        target_size = 100
                        ratio = target_size / max(img_width, img_height)

                        img_width, img_height = int(img_width * ratio), int(img_height * ratio)
                        img = pygame.transform.smoothscale(img, (img_width, img_height))

                        cell_x = offset + col * cell_size
                        cell_y = offset + row * cell_size

                        p_x = cell_x + (cell_size - img_width) // 2
                        p_y = cell_y + (cell_size - img_height) // 2

                        screen.blit(img, (p_x, p_y))
                        
                    except Exception as e:
                        print(f'Помилка: {e}')

        pass

    def is_attacked(self, pos, color, matrix):
        for row in matrix:
            for item in row:
                if item is not None and item.color == color:
                    item.get_attack_zones(matrix)
                    if pos in item.attack_zones:
                        return True
        return False

    def find_king(self, color, matrix):
        for r in range(8):
            for c in range(8):
                piece = matrix[r][c]
                if piece and piece.color == color and piece.__class__.__name__ == 'King':
                    return (r, c)
        return None
    
    def actual_moves_filter(self, piece, matrix):
        valid_moves = []
        opponent_color = 'White' if self.turn == 'Black' else 'Black'
    
        for move in piece.actual_moves:
            original_pos = piece.position
            target_piece = matrix[move[0]][move[1]]
            
            matrix[move[0]][move[1]] = piece
            matrix[original_pos[0]][original_pos[1]] = None
            piece.position = move
            
            king_pos = self.find_king(self.turn, matrix)
            if not self.is_attacked(king_pos, opponent_color, matrix):
                valid_moves.append(move)
                
            matrix[original_pos[0]][original_pos[1]] = piece
            matrix[move[0]][move[1]] = target_piece
            piece.position = original_pos

        piece.actual_moves = valid_moves

    def draw_promotion_menu(self, screen, pawn):

        w, h = 410, 120
        rec_y = 50+100-10 if pawn.color == 'White' else 50+100-10+500
        pos2 = pawn.position[1] 
        rec_x = 50+100*pos2 if pos2 <= 4 else 900-50-710+100*(pos2-4)
        
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((70, 70, 70, 240))
        screen.blit(overlay, (rec_x, rec_y))
        
        fig_types = ['Queen', 'Knight', 'Rook', 'Bishop']
        imgs = ['wq.png', 'wn.png', 'wr.png', 'wb.png'] if pawn.color == 'White' else ['bq.png', 'bn.png', 'br.png', 'bb.png']
        
        buttons = []
        for i in range(4):
            x = rec_x + 10 + 100 * i
            y = rec_y + 10
            
            img = pygame.image.load(f'assets/{imgs[i]}')
            img = pygame.transform.smoothscale(img, (100, 100))
            screen.blit(img, (x, y))
            
            buttons.append((pygame.Rect(x, y, 100, 100), fig_types[i]))
        
        return buttons

    def handle_click(self, pos, Board):
        col = (pos[0] - 50) // 100
        row = (pos[1] - 50) // 100

        if not (0 <= row < 8 and 0 <= col < 8):
            return

        matrix = Board.matrix
        target = matrix[row][col]

        if hasattr(self, 'selected_piece') and self.selected_piece:

            if (row, col) in self.selected_piece.actual_moves:
                Board.update_move(self.selected_piece.position, (row, col), chess_game)
                if isinstance(self.selected_piece, Pawn) and (row == 0 or row == 7):
                    self.promotion_pending = True
                    self.promotion_pawn = self.selected_piece
                else:
                    self.change_turn()
                self.selected_piece = None

                return

            if target and target.color == self.turn:
                self.selected_piece = target
                target.get_valid_moves(matrix, chess_game)
                self.actual_moves_filter(target, matrix)
                return
            
            self.selected_piece = None

        else:
            if target != None and target.color == self.turn:

                target.get_valid_moves(matrix, chess_game)
                self.actual_moves_filter(target, matrix)

                if target.actual_moves:

                    self.selected_piece = target 

    def check_for_winner(self, matrix):
        opponent_color = 'White' if self.turn == 'Black' else 'Black'
        king_pos = self.find_king(self.turn, matrix)
        
        for row in matrix:
            for fig in row:
                if fig and fig.color == self.turn: 
                    fig.get_valid_moves(matrix, chess_game)       
                    self.actual_moves_filter(fig, matrix) 
                        
                    if len(fig.actual_moves) != 0:
                        return False
        if self.is_attacked(king_pos, opponent_color, matrix):
            return True
        else:
            self.pat_win = True
            return True

                        
    def promote_pawn(self, Board, pawn, fig_type):
        r, c = pawn.position
        color = pawn.color
        if fig_type == 'Queen': new_fig = Queen(color, (r, c))
        elif fig_type == 'Knight': new_fig = Knight(color, (r, c))
        elif fig_type == 'Rook': new_fig = Rook(color, (r, c))
        elif fig_type == 'Bishop': new_fig = Bishop(color, (r, c))
        
        Board.matrix[r][c] = new_fig

    def start_game(self):
        Board = board()

        pygame.init()
        screen = pygame.display.set_mode((900, 900))
        pygame.display.set_caption("Chess game")
        try: pygame.display.set_icon(pygame.image.load('assets/icon.png').convert_alpha())
        except Exception as e: print(f"Помилка: {e}")
        clock = pygame.time.Clock()

        win_overlay = pygame.Surface((500, 200), pygame.SRCALPHA)
        win_font = pygame.font.SysFont('Arial', 64, bold=True)

        active_game = True
        while active_game:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    active_game = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    
                    click_pos = pygame.mouse.get_pos()

                    if self.promotion_pending:
                
                        buttons = self.draw_promotion_menu(screen, self.promotion_pawn)
                        for rect, fig_type in buttons:
                            if rect.collidepoint(click_pos):
                                self.prom_pawm_check = (self.promotion_pawn)
                                self.promote_pawn(Board, self.promotion_pawn, fig_type)
                                self.promotion_pending = False
                                
                                self.change_turn() 
                    else:
                        self.handle_click(click_pos, Board)

                    pass
            
            if self.check_for_winner(Board.matrix):

                self.game_active = False
                if not self.pat_win:
                    self.game_winner = 'White' if self.turn=='Black' else 'Black'
                else:
                    self.game_winner = 'No one won'
                pass

            screen.fill((255, 255, 255))
            self.draw_board(screen, Board.matrix)

            if self.selected_piece:

                selected_figure_pos = self.selected_piece.position
                center_x = 50 + selected_figure_pos[1] * 100 + 50
                center_y = 50 + selected_figure_pos[0] * 100 + 50

                pygame.draw.circle(screen, (80, 180, 200), (center_x, center_y), 45)
                pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), 16, 2)

                for move in self.selected_piece.actual_moves:

                    center_x = 50 + move[1] * 100 + 50
                    center_y = 50 + move[0] * 100 + 50
                    if Board.matrix[move[0]][move[1]]:
                        pygame.draw.circle(screen, (200, 80, 80), (center_x, center_y), 45)
                        pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), 16, 2)
                    else:
                        pygame.draw.circle(screen, (80, 200, 80), (center_x, center_y), 15) 
                        pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), 16, 2)

            self.draw_pieces(screen, Board.matrix)

            if not self.game_active:
                w, h = 500, 200
                x = (900 - w) // 2
                y = (900 - h) // 2
                
                won = 'WON'
                if self.pat_win:
                    won = 'Stalemate'

                win_overlay = pygame.Surface((w, h), pygame.SRCALPHA) 
                win_overlay.fill((133, 133, 133, 200)) 
                screen.blit(win_overlay, (x, y))
                text1 = win_font.render(str(self.game_winner), True, (255, 255, 255))
                text1_rect = text1.get_rect(center=(450, 420)) 
                text2 = win_font.render(won, True, (0, 255, 0))
                text2_rect = text2.get_rect(center=(450, 480)) 
                screen.blit(text1, text1_rect)
                screen.blit(text2, text2_rect)

            if self.promotion_pending:
                _ = self.draw_promotion_menu(screen, self.promotion_pawn)

            pygame.display.flip()
            clock.tick(60)
        

chess_game = Game()
chess_game.start_game() 