#!/usr/bin/env python3
# -*- coding: <utf-8> -*-

'''File with preset conjugations and information'''

from copy import deepcopy

class Data:
    def __init__(self):
        self.order = ['Indicative', 'Subjunctive', 'Imperative', 'Progressive', 'Perfect', 'Perfect Subjunctive']
        self.subOrder = {'Indicative': ['Present','Preterite','Imperfect','Conditional','Future'],
                        'Subjunctive': ['Present','Imperfect (-ra)','Imperfect (-se)','Future'],
                        'Imperative': ['Affirmative','Negative'],
                        'Progressive': ['Present','Preterite','Imperfect','Conditional','Future'],
                        'Perfect': ['Present','Preterite','Past','Conditional','Future'],
                        'Perfect Subjunctive': ['Present','Past','Future']
                        }
        self.estar = [[['estoy', 'estás', 'está', 'estamos', 'estáis', 'están'],
                        ['estuve', 'estuviste', 'estuvo', 'estuvimos', 'estuvisteis', 'estuvieron'],
                        ['estaba', 'estabas', 'estaba', 'estábamos', 'estabais', 'estaban'],
                        ['estaría', 'estarías', 'estaría', 'estaríamos', 'estaríais', 'estarían'],
                        ['estaré', 'estarás', 'estará', 'estaremos', 'estaréis', 'estarán']],
                        [['me estoy', 'te estás', 'se está', 'nos estamos', 'os estáis', 'se están'],
                        ['me estuve', 'te estuviste', 'se estuvo', 'nos estuvimos', 'os estuvisteis', 'se estuvieron'],
                        ['me estaba', 'te estabas', 'se estaba', 'nos estábamos', 'os estabais', 'se estaban'],
                        ['me estaría', 'te estarías', 'se estaría', 'nos estaríamos', 'os estaríais', 'se estarían'],
                        ['me estaré', 'te estarás', 'se estará', 'nos estaremos', 'os estaréis', 'se estarán']]
                        ]
        self.scope = deepcopy(self.subOrder)
        self.scope['Imperative'] = ['Tú', 'Ud.', 'Nosotros', 'Vosotros', 'Uds.']
        self.scopeVars = {'Indicative': [False, [True]*3+[False]*2], 
                        'Subjunctive': [False, [False]*4],
                        'Imperative': [False, [True]*2+[False]*2+[True]],
                        'Progressive': [False, [True]+[False]*4], 
                        'Perfect': [False, [False]*5], 
                        'Perfect Subjunctive': [False, [False]*3]
                        }
        self.columnHeader = ['Yo', 'Tú', 'Ud.', 'Nosotros', 'Vosotros', 'Uds.']
        self.responses = [["Keep going", "Don't give up", "Have faith"],
                        ["You're getting there", "You can do it", "Practice makes perfect"],
                        ["Almost there", "Real close", "Reaching greatness", "Well done"],
                        ["Absolutely fantastic", "Nailed it", "Superstar", "Brilliant", "Terrific"],
                        ["Winner Winner Chicken Dinner"]]
        self.defaultSettings = {'Primary Website Source': ["SpanishDict", "WordReference"],
                                'Offline Mode':False, 
                                'Use Offline Conjugation':True,
                                'Diacritic Sensitive': False,
                                'Inspirational Quote': True}
        self.objInfo = {"Primary Website Source": ["SpanishDict"]*2+["WordReference"]*2, 
                        "Offline Mode": [],
                        "Use Offline Conjugation": [],
                        "Diacritic Sensitive": [],
                        "Inspirational Quote": []}