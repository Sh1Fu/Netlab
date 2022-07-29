from __future__ import print_function
import PyInquirer


class App:
    def auth(self):
        '''
        Scan credentials from input to B2B service
        '''
        question = [{
            'type': 'input',
            'message': 'Enter your Netlab login:',
            'name': 'username'
        },
            {
            'type': 'password',
            'message': 'Enter your Netlab password:',
            'name': 'password'
        }]

        answer = PyInquirer.prompt(questions=question)
        return answer

    def main_choice(self):
        '''
        Selecting the desired function 
        '''
        choice = [{
            'type': 'list',
            'message': 'Price Update',
            'name': 'price',
            'choices': [
                PyInquirer.Separator('= Select Function ='),
                {
                    'name': 'Only default price'
                },
                {
                    'name': 'Only configuration price',

                },
                {
                    'name': 'Default price with images',

                }
            ],
            'validate': lambda answer: 'You must choose at least one topping.'
            if len(answer) == 0 else True
        }]

        choice_res = PyInquirer.prompt(questions=choice)
        return choice_res