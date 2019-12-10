import os
from shutil import copyfile
import json

from .tutorial_qchess import TutorialQChess

class TutorialProgress:
    def __init__(self, is_ascii):
        self.is_ascii = is_ascii

        self.config_path = 'tutorials/progress'
        self.template_path = 'tutorials/progress_template'

        self.resume_msg = 'Do you want to resume the tutorials where you left?'
        self.start_over_msg = 'Do you want to start over?'

        self.progress_table = {}

        #create the file based on the template if it doesn't exist
        if not os.path.isfile(self.config_path):
            #the template must exist
            assert(os.path.isfile(self.template_path))

            copyfile(self.template_path, self.config_path)

        self.load_config_file()

    def load_config_file(self):
        #read the file and load it to memory
        with open(self.config_path) as f:
            content = f.read().splitlines()

            for line in content:
                line = line.split(' ')

                #the first string is the tutorial filename, the second it's a bool
                #that's true if tutorial is already completed
                self.progress_table[line[0]] = bool(int(line[1]))

    def save_config_file(self):
        data = ''

        for tutorial_name, completed in self.progress_table.items():
            data += '{} {}\n'.format(tutorial_name, int(completed))

        with open(self.config_path, 'w') as f:
            f.write(data)

    #a simple prompt that asks for a yes or no answer and returns it as a bool
    def yes_no_prompt(self, msg):
        result = input('{} (y/n) \n'.format(msg)).lower()

        if result == 'y' or result == 'yes':
            return True
        else:
            return False

    #display each tutorial and if it's completed or not
    def display_progress(self):
        for tutorial_name, completed in self.progress_table.items():
            completed = 'Completed' if completed else 'Not completed'
            print('{} {}'.format(tutorial_name, completed))

    #returns true if all tutorials are completed, false otherwise
    def are_all_tutorials_completed(self):
        for tutorial_name, completed in self.progress_table.items():
            if not completed:
                return False

        return True

    #copy the template file to the progress file and loads it again
    def start_over(self):
        assert(os.path.isfile(self.template_path))
        copyfile(self.template_path, self.config_path)

        self.load_config_file()

    def main_loop(self):
        self.display_progress()
        print()

        all_completed = self.are_all_tutorials_completed()

        if all_completed:
            #if tutorials are completed, ask if player wants to start over
            print('All tutorials are completed.')
            start_over = self.yes_no_prompt(self.start_over_msg)

            if start_over:
                self.start_over()
                all_completed = False
        else:
            #if not, ask if player wants to resume previous session
            resume = self.yes_no_prompt(self.resume_msg)

            if not resume:
                start_over = self.yes_no_prompt(self.start_over_msg)

                if start_over:
                    self.start_over()
                    all_completed = False
                else:
                    return

        #if all tutorials are still completed, return
        if all_completed:
            return

        completed_tutorial_number = 0

        print('Remember to close the window when the tutorial is over to start the next tutorial.')

        #iterate all the tutorials
        for tutorial_name, completed in self.progress_table.items():
            #don't do anything if the tutorial is already completed
            if completed:
                completed_tutorial_number += 1
                continue

            #load the tutorial json file
            try:
                json_data = open(os.path.join('tutorials', tutorial_name + '.json'))
            except FileNotFoundError:
                print('Error while loading tutorial file {} - File not found'.format(first))
                return

            qchess = TutorialQChess(json.load(json_data))

            #run the main loop
            if self.is_ascii:
                completed = bool(qchess.ascii_main_loop())
            else:
                qchess.create_window()
                completed = bool(qchess.main_loop())

            if completed:
                completed_tutorial_number += 1

            #display the current progress, even if this tutorial was not completed
            print('Completed {}/{}.'.format(completed_tutorial_number, len(self.progress_table)))

            #stop the execution if a tutorial is not completed
            if not completed:
                break

            #if the tutorial was succesfully completed, save that information to memory
            self.progress_table[tutorial_name] = completed

            #update the config file
            self.save_config_file()

        if completed_tutorial_number == len(self.progress_table):
            print('\nAll tutorials completed.')