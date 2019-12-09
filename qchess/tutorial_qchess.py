from .quantum_chess import QChess
from .point import Point
from .piece import PieceType

#for every object in obj_list, perform action to them
#if the result is None, the object is invalid and None is returned
#otherwise the object is added to the modified list,
#which is returned at the end if all are objects valid
def _perform_check_action(obj_list, action):
    modified_list = []

    for obj in obj_list:
        new_obj = action(obj)

        if new_obj:
            modified_list.append(action(obj))
        else:
            return None

    return modified_list

class TutorialQChess(QChess):
    def __init__(self, tutorial_mode):
        super().__init__(0, 0, game_mode=tutorial_mode)

        self.move_types = [
            {'name': 'Standard', 'move_number': 2, 'func': TutorialQChess.standard_move},
            {'name': 'Split', 'move_number': 3, 'func': TutorialQChess.split_move},
            {'name': 'Merge', 'move_number': 3, 'func': TutorialQChess.merge_move}
        ]

        #the json file must have these parameters
        assert('initial_message' in tutorial_mode)
        assert('tutorial_steps' in tutorial_mode)

        #used to properly format tutorial messages when rendering the board as ascii
        self.is_board_ascii = False

        #in that case, all messages are printed at the same time after the board is rendered
        self.combined_message = ''

        #keeps track of the current step of the tutorial
        self.step_index = -1

        #displayed at the start of the tutorial
        self.initial_message = ' '.join(tutorial_mode['initial_message'])

        self.tutorial_steps = []

        #load all the steps checking they're valid first
        #and converting to appropiate types (PieceType, Point)
        for json_step in tutorial_mode['tutorial_steps']:
            step = {}
            step['message'] = ' '.join(json_step['message'])

            json_valid_moves = json_step['valid_moves']
            valid_moves = {}

            #check all piece types are valid and transform them to PieceType instances
            if 'source_piece_type' in json_valid_moves:
                #json move array
                json_move = json_valid_moves['source_piece_type']

                #if action returns None, then the piece is not valid
                def action(json_piece):
                    for piece in PieceType:
                        #source piece can never be Null
                        if piece == PieceType.NONE: continue
                        
                        if piece.name == json_piece:
                            return piece

                    return None

                #return transformed pieces (from string to PieceType instance)
                source_pieces = _perform_check_action(json_move, action)

                if source_pieces:
                    #if all pieces are valid, add them
                    valid_moves['source_piece_type'] = source_pieces
                else:
                    #otherwise raise an error
                    raise ValueError('Invalid source piece type')

            #check all piece types are valid and transform them to PieceType instances
            if 'target_piece_type' in json_valid_moves:
                json_move = json_valid_moves['target_piece_type']

                #if action returns None, then the piece is not valid
                def action(json_piece):
                    for piece in PieceType:
                        if piece.name == json_piece:
                            return piece

                    return None

                #return transformed pieces (from string to PieceType instance)
                target_pieces = _perform_check_action(json_move, action)

                if target_pieces:
                    #if all pieces are valid, add them
                    valid_moves['target_piece_type'] = target_pieces
                else:
                    #otherwise raise an error
                    raise ValueError('Invalid target piece type')

            #check move type is Standard, Split or Merge
            if 'move_type' in json_valid_moves:
                json_move = json_valid_moves['move_type']

                valid_move_type = ['Standard', 'Split', 'Merge']

                #check all json move types are valid
                for move_type in json_move:
                    if not move_type in valid_move_type:
                        raise ValueError('Invalid move type')
                    
                valid_moves['move_type'] = json_move

            #check points have a valid name, are valid and are in bounds
            possible_point_names = ['source', 'source1', 'source2', 'target', 'target1', 'target2']

            for point_name in possible_point_names:
                if point_name in json_valid_moves:
                    json_move = json_valid_moves[point_name]

                    #transform the point to Point() class instance
                    def action(json_point):
                        return self.string_to_point(json_point)

                    #return transformed points (from string (a1, b3, etc) to Point instance)
                    points = _perform_check_action(json_move, action)

                    if points:
                        #if all points are valid, add them
                        valid_moves[point_name] = points
                    else:
                        #otherwise raise error
                        raise ValueError('Invalid {} squares'.format(point_name))

            if 'collapse' in json_valid_moves:
                if not type(json_valid_moves['collapse']) == bool:
                    raise ValueError('Invalid collapse (must be bool)')

                valid_moves['collapse'] = json_valid_moves['collapse']

            step['valid_moves'] = valid_moves
            self.tutorial_steps.append(step)

        self.set_collapse_allowed()

        #if there are no steps, end the game
        if not self.tutorial_steps:
            self.ended = True

    #print formating for the step
    def print_step(self, msg):
        msg = '{}.- {}'.format(self.step_index + 2, msg)

        if self.is_board_ascii:
            self.combined_message += msg + '\n\n'
        else:
            print()
            print(msg)
        
        self.step_index += 1

    def ascii_render(self):
        super().ascii_render()

        print(self.combined_message)

    #sets collapsed_allowed if it's allowed next move
    def set_collapse_allowed(self):
        if self.step_index < len(self.tutorial_steps):
            step = self.tutorial_steps[self.step_index]

            if 'valid_moves' in step:
                valid_moves = step['valid_moves']

                if 'collapse' in valid_moves:
                    self.collapse_allowed = valid_moves['collapse']
                    return

        self.collapse_allowed = False


    def create_window(self):
        super().create_window(create_collapse_button=True)

    def main_loop(self):
        self.print_step(self.initial_message)

        super().main_loop(check_current_turn=False, check_game_over=False)

    def ascii_main_loop(self):
        self.combined_message += '{}.- {}\n\n'.format(self.step_index + 2, self.initial_message)
        self.step_index += 1

        self.is_board_ascii = True

        super().ascii_main_loop(check_current_turn=False, check_game_over=False)

    def next_step(self):
        self.set_collapse_allowed()

        #end the game if we've reached the last step
        if self.step_index == len(self.tutorial_steps):
            self.ended = True

            msg = 'Tutorial completed.'
            if self.is_board_ascii:
                self.combined_message += msg
            else:
                print('\n' + msg)

    def collapse_board(self):
        super().collapse_board()

        self.print_step(self.tutorial_steps[self.step_index]['message'])
        
        self.next_step()

    def standard_move(self, source, target):
        step = self.tutorial_steps[self.step_index]

        #if valid_moves in empty, any move is valid
        if 'valid_moves' in step:
            valid_moves = step['valid_moves']

            source_piece = self.board[source.x][source.y]
            target_piece = self.board[target.x][target.y]

            #check the type of the source piece
            if 'source_piece_type' in valid_moves:
                move = valid_moves['source_piece_type']

                if not source_piece.type in move:
                    return False

            #check the type of the target piece
            if 'target_piece_type' in valid_moves:
                move = valid_moves['target_piece_type']

                if not target_piece.type in move:
                    return False

            #check the move type
            if 'move_type' in valid_moves:
                move = valid_moves['move_type']

                if not 'Standard' in move:
                    return False

            #check source square
            if 'source' in valid_moves:
                move = valid_moves['source']

                if not source in move:
                    return False

            #check target square
            if 'target' in valid_moves:
                move = valid_moves['target']

                if not target in move:
                    return False

        if super().standard_move(source, target):
            self.print_step(step['message'])

            self.next_step()

            return True

        return False

    def split_move(self, source, target1, target2):
        step = self.tutorial_steps[self.step_index]

        #if valid_moves in empty, any move is valid
        if 'valid_moves' in step:
            valid_moves = step['valid_moves']

            source_piece = self.board[source.x][source.y]
            target_piece1 = self.board[target1.x][target1.y]
            target_piece2 = self.board[target2.x][target2.y]

            #check the type of the source piece
            if 'source_piece_type' in valid_moves:
                move = valid_moves['source_piece_type']

                if not source_piece.type in move:
                    return False

            #check the type of the target pieces
            if 'target_piece_type' in valid_moves:
                move = valid_moves['target_piece_type']

                if not target_piece1.type in move:
                    return False

                if not target_piece2.type in move:
                    return False

            #check the move type
            if 'move_type' in valid_moves:
                move = valid_moves['move_type']

                if not 'Split' in move:
                    return False

            #check source square
            if 'source' in valid_moves:
                move = valid_moves['source']

                if not source in move:
                    return False

            #check first target square
            if 'target1' in valid_moves:
                move = valid_moves['target1']

                if not target1 in move:
                    return False
            
            #check second target square
            if 'target2' in valid_moves:
                move = valid_moves['target2']

                if not target2 in move:
                    return False

        if super().split_move(source, target1, target2):
            self.print_step(step['message'])

            self.next_step()

            return True

        return False

    def merge_move(self, source1, source2, target):
        step = self.tutorial_steps[self.step_index]

        #if valid_moves in empty, any move is valid
        if 'valid_moves' in step:
            valid_moves = step['valid_moves']

            source_piece1 = self.board[source1.x][source1.y]
            source_piece2 = self.board[source2.x][source2.y]
            target_piece = self.board[target.x][target.y]

            #check the type of the source pieces
            if 'source_piece_type' in valid_moves:
                move = valid_moves['source_piece_type']

                if not source_piece1.type in move:
                    return False
                
                if not source_piece2.type in move:
                    return False

            #check the type of the target piece
            if 'target_piece_type' in valid_moves:
                move = valid_moves['target_piece_type']

                if not target_piece.type in move:
                    return False

            #check the move type
            if 'move_type' in valid_moves:
                move = valid_moves['move_type']

                if not 'Merge' in move:
                    return False

            #check first source square
            if 'source1' in valid_moves:
                move = valid_moves['source1']

                if not source1 in move:
                    return False
            
            #check second source square
            if 'source2' in valid_moves:
                move = valid_moves['source2']

                if not source2 in move:
                    return False

            #check target square
            if 'target' in valid_moves:
                move = valid_moves['target']

                if not target in move:
                    return False

        if super().merge_move(source1, source2, target):
            self.print_step(step['message'])

            self.next_step()

            return True

        return False
