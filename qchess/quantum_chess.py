import PySimpleGUI as sg
import os
import time

from .engines.qiskit.qiskit_engine import QiskitEngine
from .point import Point
from .piece import *
from .pawn import Pawn

class QChess:
    def __init__(self, width, height, game_mode=None):
        #default values
        self.current_turn = Color.WHITE
        self.pawn_double_step_allowed = True

        if game_mode:
            assert('board' in game_mode)

            #the color of the current player
            if 'starting_color' in game_mode:
                if game_mode['starting_color'] == 'Black':
                    self.current_turn = Color.BLACK

            #some modes with smaller boards may disable pawn's double step
            if 'pawn_double_step_allowed' in game_mode:
                self.pawn_double_step_allowed = game_mode['pawn_double_step_allowed']

            height = len(game_mode['board'])
            assert(height > 0)
            width = len(game_mode['board'][0])
        
        self.width = width
        self.height = height

        self.board = [[NullPiece for y in range(height)] for x in range(width)]

        #default engine is QiskitEngine
        #TODO: Read engine from game_mode dict
        self.engine = QiskitEngine(self, width, height)
        
        #holds the position of the captureable en passant pawn
        #none if the last move wasn't a pawn's double step
        self.ep_pawn_point = None
        self.just_moved_ep = False

        self.ended = False

        self.move_types = [
            {'name': 'Standard', 'move_number': 2, 'func': QChess.standard_move},
            {'name': 'Split', 'move_number': 3, 'func': QChess.split_move},
            {'name': 'Merge', 'move_number': 3, 'func': QChess.merge_move}
        ]

        if game_mode:
            #populate board
            for j, row in enumerate(game_mode['board']):
                for i, notation in enumerate(row):
                    if notation == '0': continue

                    self.add_piece(i, j, Piece.from_notation(notation))

    def is_game_over(qchess):
        black_king_count = 0
        white_king_count = 0

        msg = None

        for i in range(qchess.width * qchess.height):
            piece = qchess.get_piece(i)

            if piece.type == PieceType.KING:
                if piece.color == Color.WHITE:
                    white_king_count += 1
                elif piece.color == Color.BLACK:
                    black_king_count += 1

        if black_king_count + white_king_count == 0:
            msg = 'Draw!'

        elif black_king_count == 0:
            msg = 'White wins!'

        elif white_king_count == 0:
            msg = 'Black wins!'

        if msg:
            print(msg)

            return True
        else:
            return False

    def in_bounds(self, x, y):
        if x < 0 or x >= self.width:
            return False
        
        if y < 0 or y >= self.height:
            return False

        return True

    def is_occupied(self, x, y):
        if self.board[x][y] != NullPiece:
            return True
        return False

    def get_array_index(self, x, y):
        return self.width * y + x

    def get_board_point(self, index):
        return Point(index%self.width, int(index/self.width))

    def get_piece(self, index):
        pos = self.get_board_point(index)
        return self.board[pos.x][pos.y]

    def add_piece(self, x, y, piece):
        if not self.in_bounds(x, y): return

        if self.is_occupied(x, y):
            print("add piece error - there is already a piece in that position")
            return

        if piece.type == PieceType.PAWN and not self.pawn_double_step_allowed:
            piece.double_step_allowed = False

        self.board[x][y] = piece

        self.engine.on_add_piece(x, y, piece)

    def get_path_points(self, source, target):
        #not including source or target
        path = []
        
        if not self.in_bounds(source.x, source.y): return path 
        if not self.in_bounds(target.x, target.y): return path
        if source == target: return path

        vec = target - source
        if vec.x != 0 and vec.y != 0 and vec.x != vec.y: return path

        x_iter = y_iter = 0

        if vec.x != 0:
            x_iter = vec.x/abs(vec.x)
        if vec.y != 0:
            y_iter = vec.y/abs(vec.y)

        for i in range(1, max(abs(vec.x), abs(vec.y))):
            path.append(source + Point(x_iter * i, y_iter * i))

        return path

    def get_path_pieces(self, source, target):
        pieces = []

        for point in self.get_path_points(source, target):
            if self.board[point.x][point.y] != NullPiece:
                pieces.append(self.board[point.x][point.y])
        
        return pieces

    #a1 to Point(0, 0)
    def string_to_point(self, string):
        #check correct length of 2
        if len(string) != 2:
            return None

        #check first character is a lowercase letter
        if ord(string[0]) < 97 or ord(string[0]) > 122:
            return None

        #check second character is a number
        if ord(string[1]) < 49 or ord(string[1]) > 57:
            return None

        result = Point(ord(string[0]) - 97, self.height - int(string[1]))

        if not self.in_bounds(result.x, result.y):
            return None 

        return result

    #a2b3, a2^b3b4, etc to a set of (source, target) or (source1, target1, target2), etc
    #if check_current_turn is set to True, an error will occur if the turn 
    def command_to_move_points(self, command, check_current_turn=False):
        move_points = None
        move_index = None

        if len(command) == 4:
            #standard move
            source = self.string_to_point(command[0:2])
            target = self.string_to_point(command[2:4])

            if source and target:
                if (
                    check_current_turn and
                    self.board[source.x][source.y].color != self.current_turn
                ):
                    print("It's " + self.current_turn.name.lower() + "'s turn to move.")
                    return move_index, None

                move_points = [source, target]
                move_index = 0

        elif len(command) == 7:
            if command[2] == '^':
                #split move
                source = self.string_to_point(command[0:2])
                target1 = self.string_to_point(command[3:5])
                target2 = self.string_to_point(command[5:7])

                if source and target1 and target2:
                    if (
                        check_current_turn and
                        self.board[source.x][source.y].color != self.current_turn
                    ):
                        print("It's " + self.current_turn.name.lower() + "'s turn to move.")
                        return move_index, None

                    move_points = [source, target1, target2]
                    move_index = 1

            elif command[4] == '^':
                #merge move
                source1 = self.string_to_point(command[0:2])
                source2 = self.string_to_point(command[2:4])
                target = self.string_to_point(command[5:7])

                if source1 and source2 and target:
                    if (
                        check_current_turn and
                        (self.board[source1.x][source1.y].color != self.current_turn or
                        self.board[source2.x][source2.y].color != self.current_turn)
                    ):
                        print("It's " + self.current_turn.name.lower() + "'s turn to move.")
                        return move_index, None

                    move_points = [source1, source2, target]
                    move_index = 2
            
        return move_index, move_points

    def perform_command_move(self, command):
        success = False

        move_index, move_points = self.command_to_move_points(command, check_current_turn=True)

        if move_points:
            success = self.move_types[move_index]['func'](self, *move_points)
        else:
            print('Invalid move.')

        return success

    def ascii_render(self):
        s = ""

        for j in range(self.height):
            for i in range(self.width):
                piece = self.board[i][j]
                if piece:
                    s += piece.as_notation() + ' '
                else:
                    s += '0 '
            s += '\n'

        print(s)

    def render_square(self, image, key, location):
        if (location[0] + location[1]) % 2:
            color = self.square_colors['Default']['dark']
        else:
            color = self.square_colors['Default']['light']

        return sg.RButton('', image_filename=image, size=(1, 1),
                        border_width=0, button_color=('white', color),
                        pad=(0, 0), key=key)

        return square

    #change square to selected (by changing to different color)
    def select_button(self, i, j, color):
        if color in self.square_colors:
            new_color = None
            
            if (i + j) % 2:
                new_color = self.square_colors[color]['dark']
            else:
                new_color = self.square_colors[color]['light']

            self.window[(i, j)].update(button_color = ('white', new_color))

    def generate_initial_render_layout(self):
        IMAGE_PATH = 'images'

        #load the .png files
        self.images = {}

        sg.change_look_and_feel('BlueMono')
        sg.set_options(margins=(0, 3), border_width=1)

        #load the images of the pieces
        for color in Color:
            for piece_type in PieceType:
                if (
                    piece_type == PieceType.NONE or 
                    color == Color.NONE
                ):
                    self.images['0'] = os.path.join(IMAGE_PATH, 'None.png')
                    continue

                key = Piece(piece_type, color).as_notation()
                self.images[key] = os.path.join(IMAGE_PATH, key + '.png')

        #generate the layout
        board_layout = []

        for j in range(self.height):
            row = []

            for i in range(self.width):
                key = self.board[i][j].as_notation()

                row.append(self.render_square(self.images[key], 
                            key=(i, j), location=(i, j)))

                #this invisible button will be used to get right click events
                row.append(sg.Button(key=(i, j, 'RIGHT'), visible=False))

            board_layout.append(row)

        move_type_button = sg.Button(self.move_types[self.current_move]['name'],
                                        key='MOVE-TYPE')
        
        
        layout = [[sg.Column(board_layout)], [move_type_button]]

        return layout

    def create_window(self):
        self.current_move = 0

        #each turn will be filled with (source, target) or (source1, source2, target) etc
        self.current_move_points = []
        self.prev_move_points = []

        self.square_colors = {
            'Default': {'light': '#F0D9B5', 'dark': '#B58863'},
            'Green': {'light': '#E8E18E', 'dark': '#B8AF4E'},
            'Purple': {'light': '#8EA3E8', 'dark': '#7072CA'},
        }

        self.showing_entanglement = False

        layout = self.generate_initial_render_layout()

        self.window = sg.Window('Quantum Chess',
                           layout, default_button_element_size=(12, 1),
                           auto_size_buttons=False, return_keyboard_events=True,
                           finalize=True)

        self.bind_right_click()

    #reset all squares to default color
    #or reset only the squares with a specific color
    def redraw_board(self, only_color=None):
        for i in range(self.width):
            for j in range(self.height):
                elem = self.window[(i, j)]

                if only_color != None:
                    #only reset the squares with color == only_color
                    if elem.ButtonColor[1] not in self.square_colors[only_color].values():
                        continue  

                color = self.square_colors['Default']['dark'] if (i + j) % 2 else \
                        self.square_colors['Default']['light']

                key = self.board[i][j].as_notation()
                
                elem.update(button_color=('white', color),
                            image_filename=self.images[key])

    #bind the right click hotkey
    def bind_right_click(self):
        for i in range(self.width):
            for j in range(self.height):
                left_click = self.window[(i, j)]
                right_click = self.window[(i, j, 'RIGHT')]

                left_click.Widget.bind("<Button-3>", right_click.ButtonReboundCallback)

    def main_loop(self):
        self.ended = False

        while True:
            event, value = self.window.read(timeout=50)

            if event in (None, 'Exit'):
                break

            #change move type (standard, split, merge)
            elif event == 'MOVE-TYPE' or 's' in event:
                self.current_move = (self.current_move + 1) % 3
                new_text = self.move_types[self.current_move]['name']

                self.window['MOVE-TYPE'].update(text=new_text)

                #deselect move buttons
                for p in self.current_move_points:
                    self.select_button(p.x, p.y, 'Default')

                self.current_move_points = []
                
            #square was pressed
            elif type(event) is tuple:
                a = Point(event[0], event[1])
                move_type = self.move_types[self.current_move]

                #left click event has length 2
                if len(event) == 2 and not self.ended:
                    #a couple of checks for the first square selection (the source)
                    if not self.current_move_points:
                        piece = self.board[a.x][a.y]

                        #source can never be null
                        if piece == NullPiece:
                            #deselect all entangled points
                            if self.showing_entanglement:
                                self.redraw_board(only_color='Purple')

                                #select the previous move again
                                for p in self.prev_move_points:
                                    self.select_button(p.x, p.y, 'Green')

                                self.showing_entanglement = False

                            continue
                        
                        #source can never be a different team
                        if piece.color != self.current_turn:
                            continue
                    
                    #add pressed button and select it in green
                    self.current_move_points.append(a)
                    self.select_button(a.x, a.y, 'Green')

                    #if the move is ready to be performed
                    if len(self.current_move_points) == move_type['move_number']:
                        success = move_type['func'](self, *self.current_move_points)

                        if success:
                            #deselect all squares after a move
                            self.redraw_board()
                            self.current_turn = Color.opposite(self.current_turn)
                            
                            #select only the squares involved in the move
                            for p in self.current_move_points:
                                self.select_button(p.x, p.y, 'Green')

                            self.prev_move_points = self.current_move_points

                            #check if there are no kings left for a color
                            if self.is_game_over():
                                self.ended = True
                        else:
                            #deselect only the squares involved in the move,
                            #because it wasn't succesful
                            for p in self.current_move_points:
                                self.select_button(p.x, p.y, 'Default')

                        self.current_move_points = []

                #right click has length 3
                elif len(event) == 3 and event[2] == 'RIGHT':
                    if self.board[a.x][a.y] == NullPiece and self.showing_entanglement:
                        #deselect all entangled points
                        self.redraw_board(only_color='Purple')

                        #select the previous move again
                        for p in self.prev_move_points:
                            self.select_button(p.x, p.y, 'Green')

                        self.showing_entanglement = False

                    elif self.board[a.x][a.y] != NullPiece:
                        #deselect previous selected entangled points
                        self.redraw_board(only_color='Purple')

                        #select the previous move again
                        for p in self.prev_move_points:
                            self.select_button(p.x, p.y, 'Green')

                        #select all entangled points
                        points = self.engine.get_all_entangled_points(a.x, a.y)

                        if points:
                            self.showing_entanglement = True

                        for p in points:
                            self.select_button(p.x, p.y, 'Purple')

        self.window.close()

    def ascii_main_loop(self):
        #clear for unix based systems, cls for windows
        clear_command = 'cls' if os.name == 'nt' else 'clear'

        os.system(clear_command)
        print('\n')
        self.ascii_render()

        while True:
            command = input('')

            os.system(clear_command)

            success = self.perform_command_move(command)

            print('')
            #if move wasn't succesful then an error was printed
            if success: 
                #if it was succesful we print a blank line to keep
                #the board in the same position
                print('')

                self.current_turn = Color.opposite(self.current_turn)

            self.ascii_render()

            if self.is_game_over():
                break

    def get_simplified_matrix(self):
        m = []

        for j in range(self.height):
            row = []
            for i in range(self.width):
                row.append(self.board[i][j].as_notation())
            m.append(row)

        return m

    def standard_move(self, source, target, force=False):
        if not self.in_bounds(source.x, source.y):
            print('Invalid move - Source square not in bounds')
            return False

        if not self.in_bounds(target.x, target.y):
            print('Invalid move - Target square not in bounds')
            return False
        
        if not self.is_occupied(source.x, source.y):
            print('Invalid move - Source square is empty')
            return False

        piece = self.board[source.x][source.y]

        if not force:
            if piece.type == PieceType.PAWN:
                move_type, ep_point = piece.is_move_valid(source, target, qchess=self)
                
                if move_type == Pawn.MoveType.INVALID:
                    print('Invalid move - Incorrect move for piece type pawn')
                    return False

            elif not piece.is_move_valid(source, target):
                print('Invalid move - Incorrect move for piece type ' + piece.type.name.lower())
                return False

        self.engine.standard_move(source, target, force=force)

        #update pawn information if move was succesful
        if piece.type == PieceType.PAWN and not piece.has_moved:
            piece.has_moved = True

            if move_type == Pawn.MoveType.DOUBLE_STEP:
                self.ep_pawn_point = target
                self.just_moved_ep = True

        return True

    def split_move(self, source, target1, target2, force=False):
        if not self.in_bounds(source.x, source.y):
            print('Invalid move - Source square not in bounds')
            return False

        if not self.in_bounds(target1.x, target1.y) or not self.in_bounds(target2.x, target2.y):
            print('Invalid move - Target square not in bounds')
            return False
        
        if not self.is_occupied(source.x, source.y):
            print('Invalid move - Source square is empty')
            return False

        if target1 == target2:
            print("Invalid move - Both split targets are the same square")
            return False

        piece = self.board[source.x][source.y]

        if not force:
            if piece.type == PieceType.PAWN:
                print("Invalid move - Pawns can't perform split moves")
                return False

            if (
                not piece.is_move_valid(source, target1) or 
                not piece.is_move_valid(source, target2)
            ):
                print('Invalid move - Incorrect move for piece type ' + piece.type.name.lower())
                return False

        target_piece1 = self.board[target1.x][target1.y]
        target_piece2 = self.board[target2.x][target2.y]

        if target_piece1 != NullPiece and target_piece1 != piece:
            print("Invalid move - Target square is not empty")
            return False

        if target_piece2 != NullPiece and target_piece2 != piece:
            print("Invalid move - Target square is not empty")
            return False

        self.engine.split_move(source, target1, target2)

        return True
    
    def merge_move(self, source1, source2, target, force=False):
        if not self.in_bounds(source1.x, source1.y):
            print('Invalid move - Source square not in bounds')
            return False

        if not self.in_bounds(source2.x, source2.y):
            print('Invalid move - Source square not in bounds')
            return False

        if not self.in_bounds(target.x, target.y):
            print('Invalid move - Target square not in bounds')
            return False

        if source1 == source2:
            print('Invalid move - Both merge sources are the same squares')
            return False
        
        piece1 = self.board[source1.x][source1.y]
        piece2 = self.board[source2.x][source2.y]

        if not force:
            if piece1.type == PieceType.PAWN or piece2.type == PieceType.PAWN:
                print("Invalid move - Pawns can't perform merge moves")
                return False

            if (
                not piece1.is_move_valid(source1, target) or 
                not piece2.is_move_valid(source2, target)
            ):
                print('Invalid move - Incorrect move for piece type ' + piece1.type.name.lower())
                return False

        if piece1 != piece2:
            print('Invalid move - Different type of merge source pieces')
            return False

        target_piece = self.board[target.x][target.y]

        if target_piece != NullPiece and target_piece != piece1:
            print('Invalid move - Target square is not empty')
            return False

        self.engine.merge_move(source1, source2, target)

        return True
