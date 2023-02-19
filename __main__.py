#!/usr/bin/env python3
# -*- coding: <utf-8> -*-

import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from os.path import expanduser
import json
import bs4
import threading
from requests import get
from os.path import expanduser
from functools import partial
from time import time, sleep
from random import randint, choice
#  á, é, í, ó, ú, ñ, ü

from data import Data
from conjugation import Conjugation
from scrollframe import ScrollFrame

class CincoMinutos(tk.Frame):
    '''CincoMinutos(master) -> CincoMinutos object
        Creates a class for Tkinter GUI - main class'''

    def __init__(self, master):
        '''self.__init__(master) -> class init
        Initializes the CincoMinutos class
        Does main setting init
        Does main variables init
        Does settings file and conjugation file init
        '''

        # --- SETTINGS INIT ---
        tk.Frame.__init__(self, master)
        self.master = master # master window
        self.grid()
        # creates Tk window before file handling starts
        # --- END SETTINGS INIT ---


        # --- FILE & SETTINGS VAR INIT ---
        dataFile = Data()
        self.s_defaultSettings = dataFile.defaultSettings
        self.s_settings = {}

        startT= time()
        with open(expanduser('~/Documents/CincoMinutos-master/settings.json'), 'a+') as f:
            f.seek(0,0) # places pointer at start of file
            corrupted = False
            try:
                # turns all json info into vars with load
                self.s_settings = json.load(f)
                self.s_allVerbs = []
                # --- OFFLINE MODE INIT ---
                if self.s_settings['Offline Mode']: # conjugation file reading only happens if setting is on
                    with open(expanduser('~/Documents/CincoMinutos-master/verbconjugations.json'), 'r+', encoding='utf-8') as f2: 
                        self.s_allVerbs = [json.loads(line) for line in f2]
                # --- END OFFLINE MODE INIT ---
                for key in self.s_settings:
                    if not isinstance(self.s_settings[key], type(self.s_defaultSettings[key])): corrupted = True
            except Exception as e: # if any unexpected error occurs
                corrupted = True
                print('File is corrupted!\n',e)
            if corrupted or not len(self.s_settings):
                f.truncate(0) # if there are any errors, reset & recreate the file
                json.dump(self.s_defaultSettings, f, indent=2, ensure_ascii=False)
                self.s_settings = {key: self.s_defaultSettings[key] for key in self.s_defaultSettings}
        # --- END FILE & SETTINGS VAR INIT ---
        print("Finished loading file in {:4f} seconds".format(time()-startT))

        # --- VAR INIT ---
        # store offline version of estar for WordReference web-scraping to do away with extra web-scraping        
        self.m_odr = dataFile.order
        self.m_subOdr = dataFile.subOrder
        self.c_estar = dataFile.estar
        self.t_m_scope = dataFile.scope
        self.t_m_scopeVars = dataFile.scopeVars
        self.t_colHead = dataFile.columnHeader
        self.t_r_responses = dataFile.responses
        self.s_objInfo = dataFile.objInfo

        self.conj = Conjugation(self.s_settings['Primary Website Source'], self.master)
        # --- END VAR INIT ---

        # --- STATES INIT ---
        self.m_states = {'c': {'foundOffline': False, 'offline': False, 'f_gridded': False, "many_verbs": False,
                                'verbs_list': None},
                        't': {'gridded': None},
                        's': {'downloading': False}}
        # --- END STATES INIT ---

        # --- CUSTOM INITS ---
        self.m_init()
        self.m_grid(startup=True)
        self.a_init()
        self.f_init()
        self.t_init()
        self.c_init()
        self.ab_init()
        # --- END CUSTOM INITS ---

    def m_init(self):
        self.m_obj = [tk.Button(self, text = 'Conjugator', command = self.c_grid, width = 10, font=("Times", 18, 'bold')),
                    tk.Button(self, text = 'Settings', command = self.s_init, width = 10, font=("Times", 18, 'bold')),
                    tk.Button(self, text = 'Verb Check', command = self.t_m_grid, width = 10, font=("Times", 18, 'bold')),
                    tk.Button(self, text = 'About', command = self.ab_grid, width = 10, font=("Times", 18, 'bold'))]
        if self.s_settings['Inspirational Quote']: 
            self.m_obj.append(tk.Label(self, text = self.m_get_quote(), font = ("Times", 14, "italic")))

    def m_grid(self, startup:bool=False, safe:bool=True):
        '''self.m_grid(safe) -> custom initializer
        Just grids all m_ objects in their respective locations
        If not safe, pops up messagebox'''
        if not safe and not messagebox.askyesno("Return To Home", \
        "Would you like to return to home? All current information will be lost."): return
        # everything here has not been init yet under startup
        if not startup:
            self.m_states['c']['f_gridded']=False
            self.m_states['t']['gridded']=None
            self.t_obj[1].unbind('<Return>')
            self.c_obj['m'][2].unbind('<Return>')
            for obj in self.f_frame.grid_slaves(): obj.grid_forget() # ungrids all on a_frame
            for obj in self.grid_slaves(): obj.grid_forget() # ungrids all on screen
        self.m_obj[0].grid(row = 1, column = 0, padx = 10, pady = 10)
        self.m_obj[1].grid(row = 2, column = 0, padx = 10, pady = 10)
        self.m_obj[2].grid(row = 1, column = 1, padx = 10, pady = 10)
        self.m_obj[3].grid(row = 2, column = 1, padx = 10, pady = 10)
        if self.s_settings['Inspirational Quote'] and not self.m_states['c']['offline']:
            self.m_obj[4].grid(row = 0, column = 0, padx = 10, pady = 10, columnspan = 2)

    def a_init(self):
        self.a_acc = ['á', 'é', 'í', 'ó', 'ú', 'ñ', 'ü']
        self.a_frame = tk.Frame(self)
        self.a_accButtons = [tk.Button(self.a_frame, text = acc, command = None) for acc in self.a_acc]

    def f_init(self):
        self.f_frame = ScrollFrame(self, height=700, width=750, borderwidth=2, relief=tk.RAISED)
        self.f_obj = {'c': [], 't': {name: {'m': []} for name in self.m_odr}, 's': {}}
        self.f_c_init()
        self.f_t_init()
        self.f_s_init()

    def f_c_init(self):
        '''self.f_c_init() -> custom init for Canvas objects
        Creates all elements on custom Canvas'''
        for name in self.m_odr:
            if name == 'Imperative': italHdrs = self.t_colHead[1:]
            else: italHdrs = self.t_colHead
            # main title label object
            self.f_obj['c'].append(tk.Label(self.f_frame, text = name, font = "Arial 28 bold"))
            # column italic headers on left
            self.f_obj['c'].extend([tk.Label(self.f_frame, text = i, font = ('Arial', 16, 'italic')) for i in italHdrs])
            for i in range(len(self.m_subOdr[name])): # row bold headers on top
                self.f_obj['c'].append(tk.Label(self.f_frame, text = self.m_subOdr[name][i], font = 'Arial 14 bold'))
                # actual text
                self.f_obj['c'].extend([tk.Label(self.f_frame, text = None) for j in range(len(italHdrs))])

    def f_t_init(self):
        '''self.f_t_init() -> custom init for Verb Check, all dialogs'''
        for name in self.m_odr:
            if name == 'Imperative': italHdrs = self.t_colHead[1:]
            else: italHdrs = self.t_colHead
            objs = self.f_obj['t'][name]
            # main title label object
            objs['m'] = [tk.Label(self.f_frame, font = "Arial 28 bold")]
            # column italic headers on left
            objs['m'].extend([tk.Label(self.f_frame, text = i, font = 'Arial 16 italic') for i in italHdrs])
            objs['r'], objs['e'] = [[] for i in self.m_subOdr[name]], [[] for i in self.m_subOdr[name]]
            for colNum in range(len(self.m_subOdr[name])):
                # row bold headers on top
                objs['m'].append(tk.Label(self.f_frame, text = self.m_subOdr[name][colNum], font = 'Arial 16 bold'))
                for row in italHdrs:
                    objs['r'][colNum].append(tk.Label(self.f_frame)) # dialog for reviewing mistakes
                    objs['e'][colNum].append(tk.Entry(self.f_frame, width = 10))

    def f_s_init(self):
        '''self.f_s_init() -> custom sub-init
        scope is choosing which conjugations you want to be tested upon
        thus the "scope" of the verb check'''
        # structure of scopeObj: {category: [main checkbutton, [list of subsection checkbuttons]]}
        for i in self.t_m_scope:  # i = category
            # big category checkbutton
            self.f_obj['s'][i] = [tk.Checkbutton(self.f_frame, text = i, \
                command = partial(self.t_m_check_bool, i), font='Helvetica 15 italic'), []]
            if self.t_m_scopeVars[i][0]: self.f_obj['s'][i][0].toggle()
            for j in range(len(self.t_m_scope[i])):
                boolChg = partial(self.t_m_bool_change, self.t_m_scopeVars[i][1], j) # small category checkbutton
                self.f_obj['s'][i][1].append(tk.Checkbutton(self.f_frame, text = self.t_m_scope[i][j], command = boolChg))
                if self.t_m_scopeVars[i][1][j]: self.f_obj['s'][i][1][j].toggle()

    def t_init(self):
        '''self.t_init() -> custom init
        initializes the entry point of VC dialog
        similar structure to self.c_init'''
        self.t_obj = [tk.Entry(self, width = 50), # verb entry
                tk.Button(self, text = 'Verify', command = self.t_m_refresh), # verify button
                tk.Button(self, text = 'Test Me!', command = self.t_t_grid, state=tk.DISABLED), # test button
                tk.Button(self, text = 'Return To Home', command = self.m_grid),
                tk.Label(self.f_frame, font=('Arial', 30, 'bold')),
                tk.Entry(self.f_frame, text = 'to ', width=10, font=('Arial', 24, 'bold'))] # Return button
    
    def c_init(self):
        '''self.c_init() -> custom init for Conjugation dialog
        self.f_frame is ScrollFrame, 1 is title label,
        2 is verb entry, 3 is Conjugate button, 4 is return button'''
        self.c_obj = {'c': [],
            'm': [tk.Label(self.f_frame, text = 'A Random Conjugated Verb', font = ['Times New Roman', 30, 'bold']),
            tk.Entry(self, width = 60), # verb entry
                tk.Button(self, text = '¡Conjugate!', command = self.c_refresh), # Conjugate button
                tk.Button(self, text = 'Return To Home', command = self.m_grid)]} # return button
        # title label inside scrollframe

    def ab_init(self):
        '''self.ab_init() -> custom init for About dialog
        pulls information from README.txt'''
        self.ab_obj = [scrolledtext.ScrolledText(self, wrap=tk.WORD, width=90, height=30),
                        tk.Button(self, text = 'Return To Home', command = self.m_grid)]
        with open(expanduser('~/Documents/CincoMinutos-master/README.txt'), 'r+', encoding='utf-8') as f: 
            self.ab_obj[0].insert(tk.INSERT, f.read())
            self.ab_obj[0].config(state=tk.DISABLED)

    
    def m_get_quote(self):
        '''self.m_get_quote() -> method for daily inspirational quote'''
        try: html = get("https://www.brainyquote.com/topics/daily")
        except: 
            self.m_states['c']['offline'] = True
            return None
        self.m_states['c']['offline'] = False
        soup = bs4.BeautifulSoup(html.content, 'html.parser')
        lst = list(soup.find_all(class_='b-qt'))
        while True:
            rand = randint(0, len(lst))
            quote = lst[rand].get_text()
            horLen = len(quote)-50
            if horLen > 500: continue
            while horLen > 50:
                quote = quote[:horLen] + '-\n' + quote[horLen:]
                horLen -= 50
            author = list(soup.find_all(class_='bq-aut'))[rand].get_text()
            return '"{}" \n- {}'.format(quote, author)
    

    
    def a_grid(self, row: int, column: int, arrangeMode: bool, menuMode: str):
        '''self.a_grid(row, column, arrangeMode, menuMode, stringVars=None, objects=None) -> accent buttons initializer
        adds all the accent buttons in a dialog based upon the mode, row, and column to be gridded'''
        #arrangeMode True is changing by row, False is changing by column
        assert isinstance(arrangeMode, bool)
        assert menuMode == 'c' or menuMode == 't' # two types of menuModes
        self.a_frame.grid(row= row, column = column)
        row, column = 0, 0
        for i in range(len(self.a_acc)):
            self.a_accButtons[i]['command'] = partial(self.a_handler, self.a_acc[i], menuMode)
            self.a_accButtons[i].grid(row = row, column = column, padx = 2, pady = 2)
            if not arrangeMode: column += 1 # depends upon option
            else: row += 1

    def a_handler(self, accent: str, menuMode: bool):
        '''self.a_handler(accent, menuMode, stringVars, objects) -> handler method
        Handler method for all accent buttons and adding to placement'''
        if menuMode == 'c': # adds accent to entry bar
            self.c_obj['m'][1].insert(self.c_obj['m'][1].index(tk.INSERT), accent)
        elif menuMode == 't':
            if self.t_obj[0] == self.t_obj[0].focus_get():
                self.t_obj[0].insert(self.t_obj[0].index(tk.INSERT), accent)
            else:
                for obj in self.t_t_entriesEnabled:
                    if obj== obj.focus_get(): obj.insert(obj.index(tk.INSERT), accent) # add accent to specific entry bar





    def f_c_grid(self):
        '''self.f_c_grid() -> handler method for self.c_refresh()
        Displays all elements on custom Canvas
        Updates conjugations to current verb'''
        i, row= 0, 1
        for name in self.m_odr:
            if name == 'Imperative': italHdrs = self.t_colHead[1:]
            else: italHdrs = self.t_colHead
            # main title label object - index is i and changes by order of creation
            if not self.m_states['c']['f_gridded']: 
                self.f_obj['c'][i].grid(row = row, column = 0, columnspan = 6, sticky = tk.W, padx = (20,5), pady = (30,5))
            i += 1 # only need to re-grid if not already gridded
            for j in range(len(italHdrs)): # column italic headers on left
                if not self.m_states['c']['f_gridded']: 
                    self.f_obj['c'][i].grid(row = j+2+row, column = 0, padx = (10,3), pady = 3)
                i += 1
            for j in range(len(self.m_subOdr[name])): # row bold headers on top
                if not self.m_states['c']['f_gridded']: 
                    self.f_obj['c'][i].grid(row = 1+row, column = j+1, padx = 3, pady=3)
                i += 1
                for h in range(len(italHdrs)):
                    self.f_obj['c'][i].config(text=self.conj.conj[name][self.m_subOdr[name][j]][h].lower())
                    if not self.m_states['c']['f_gridded']: 
                        self.f_obj['c'][i].grid(row = 2+h+row, column = j+1, pady = 3)
                    i += 1 # must regrid b/c different conj
            if name == 'Imperative': row += 7
            else: row += 8
        self.m_states['c']['f_gridded'] = True

    def f_c_grid_forget(self):
        '''self.f_c_grid_forget() -> handler method for self.c_refresh
        grid_forgets all canvas elements'''
        for obj in self.f_obj['c']: obj.grid_forget()
        self.m_states['c']['f_gridded'] = False

    def f_t_grid(self, state:str='testing'):
        '''self.f_t_grid(stare='testing') -> custom grid for Verb Check, all dialogs
        if reviewState is True: there will be text instead of entries'''
        assert state=='testing' or state=='review'
        self.t_t_entriesEnabled = []
        bindI = 0 # index used for binding and passing to self.t_t_focus_set
        Row = 1 # row counter - for gridding
        for name in self.m_odr:
            i = 0 # sub-main counter - used with each objs['m']
            if name == 'Imperative': italHdrs = self.t_colHead[1:] # del 'yo'
            else: italHdrs = self.t_colHead
            objs = self.f_obj['t'][name] # shorten
            # main title label object
            objs['m'][i].config(text = name)
            objs['m'][i].grid(row = Row, column = 0, columnspan = 6, sticky = tk.W, padx = (30,10), pady = (20,5))
            i += 1 # add after each use
            for j in range(len(italHdrs)): # column italic headers on left
                objs['m'][i].grid(row = Row+j+2, column = 0, padx = (10,3), pady = (3,3)) # grids element placed
                i += 1
            # only erase all objects if not using for correcting mistakes
            #if not reviewState: self.t_t_entriesEnabled[name] = []
            for j in range(len(self.m_subOdr[name])):
                # k bold headers on top
                objs['m'][i].grid(row = Row+1, column = j+1, padx = (3,3), pady = (3,3))
                i+=1
                #if not reviewState: self.t_t_entriesEnabled[name].append([])
                for k in range(len(italHdrs)):
                    if state=='review': # if dialog for reviewing mistakes
                        # make red if wrong
                        if not self.t_r_ans[name][j][k]: color = 'red'
                        else: color = 'black'
                        txt = objs['e'][j][k].get()
                        if txt == '': txt = "_____" # if blank, put underscores
                        objs['r'][j][k].config(text = txt, fg = color)
                        objs['r'][j][k].grid(row = Row+k+2, column = j+1, padx = 3, pady = 3)
                    elif state=='testing': # normal testing dialog
                        # enables only if selected to verb check in scope
                        # if is imperative must reorganize the structure
                        if name != 'Imperative' and self.t_m_scopeVars[name][1][j] or \
                            name == 'Imperative' and self.t_m_scopeVars[name][1][k]: 
                            entryState = tk.NORMAL
                            self.t_t_entriesEnabled.append(objs['e'][j][k])
                            objs['e'][j][k].bind('<Return>', partial(self.t_t_focus_set, bindI))
                            bindI+=1
                        else: entryState = tk.DISABLED
                        objs['e'][j][k].delete(0, tk.END)
                        objs['e'][j][k].config(state = entryState)
                        objs['e'][j][k].grid(row=Row+k+2, column=j+1, padx=3, pady=3)
                        #if len(italHdrs)-k == 1: objs['e'][j][k].grid_configure(pady = (3,10))
            if name == 'Imperative': Row += 7 # del 'yo'
            else: Row += 8

    def f_s_grid(self):
        '''self.f_s_grid() -> handler method for sub-init
        .grid() all the scope elements in self.f_obj['s']'''
        colNum = 1
        for i in self.t_m_scope:
            self.f_obj['s'][i][0].grid(row = 1, column = colNum, padx = 10, pady = (2,5), sticky = tk.W)
            for j in range(len(self.t_m_scope[i])):
                self.f_obj['s'][i][1][j].grid(row = 2+j, column = colNum, sticky = tk.E)
            colNum += 1

    def f_s_grid_forget(self):
        '''self.f_s_grid_forget() -> handler method for sub-init
        .grid_forget() all the scope elements in self.f_obj['s']'''
        for i in self.t_m_scope:
            self.f_obj['s'][i][0].grid_forget()
            for j in range(len(self.t_m_scope[i])):
                self.f_obj['s'][i][1][j].grid_forget()





    def t_m_grid(self):
        '''self.t_m_grid() -> custom gridding method
        grids the entry point of VC dialog'''
        for obj in self.m_obj: obj.grid_forget()
        # refreshes if enter bar pressed - enter bar configs
        self.t_obj[0].bind('<Return>', lambda e: self.t_m_bind_refresh())
        self.t_obj[0].delete(0, tk.END)
        self.t_obj[0].config(width=50)
        self.t_obj[0].grid(row = 0, column = 0, padx = 5, pady = 2)
        # verify button configs
        self.t_obj[1].grid(row = 0, column = 1, padx = 5, pady = 5)
        # test me! button configs
        self.t_obj[2].config(command=self.t_t_grid, text='Test Me!', state=tk.DISABLED)
        self.t_obj[2].grid(row=0, column=2, padx= 5, pady=5)
        # return to home button configs
        self.t_obj[3].grid(row = 0, column=3, padx = 2, pady = 5)
        self.a_grid(1, 0, False, 't') # accent init for entry bar
        self.f_frame.get_master_frame().grid(row=2, column=0, columnspan=4, padx=10, pady=20)
        self.m_states['t']['gridded'] = 'scope'
        self.t_obj[4].config(text="A Random Verb")
        self.t_obj[4].grid(row=0, column=0, columnspan=7, pady=20, padx=5)
        self.t_obj[5].config(fg='black')
        # scope grids
        self.f_s_grid()

    def t_m_bool_change(self, lst: list, index: int):
        '''self.t_m_bool_change(list, index) -> handler method for scope init
        toggles bool using power of lists and indexes'''
        lst[index] = not lst[index]

    def t_m_check_bool(self, cat):
        '''self.t_m_check_bool(category) -> handler method for scope init in main checkbuttons
        toggles all checkbuttons under subsection'''
        self.t_m_scopeVars[cat][0] = not self.t_m_scopeVars[cat][0]
        for subcat in range(len(self.t_m_scopeVars[cat][1])):
            if self.t_m_scopeVars[cat][0] != self.t_m_scopeVars[cat][1][subcat]: # toggle only if does not already match main checkbutton
                self.t_m_scopeVars[cat][1][subcat] = not self.t_m_scopeVars[cat][1][subcat]
                self.f_obj['s'][cat][1][subcat].toggle()
 
    def t_m_bind_refresh(self):
        '''self.t_m_bind_refresh() -> bind callback for <Return> button'''
        if self.t_obj[0] == self.t_obj[0].focus_get(): self.t_m_refresh()

    def t_m_refresh(self):
        '''self.t_m_refresh() -> handler method for Verify button'''
        if self.t_obj[0].get() == 'Type here!': return # do not execute if state is unchanged
        if not self.m_states['t']['gridded'] == 'scope':
            message = "Would you like to test with a new verb? All current information will be lost."
            if messagebox.askyesno("Reset Verb", message):
                for obj in self.f_frame.grid_slaves(): obj.grid_forget()
                self.t_m_grid()
        startT = time()
        self.c_conj(self.t_obj[0].get())
        print('Finished processing in {:4f} seconds.'.format(time()-startT))
        if self.conj.conj is None: # if verb not found
            if self.m_states['c']['offline']: self.t_obj[4]['text'] = "I'm offline! Please Connect To WiFi."
            else: self.t_obj[4]['text'] = 'Invalid Verb! Please Try Again.'
            self.t_obj[2].config(state = tk.DISABLED)
            self.t_obj[5].delete(0,tk.END)
            self.t_obj[5].grid_forget()
            self.t_obj[4].grid_configure(columnspan=7, sticky=None)
        else: 
            self.t_obj[4].config(text=self.conj.verb.title()+' - ')
            self.t_obj[4].grid_configure(columnspan=4, sticky=tk.E)
            self.t_obj[5].config(state=tk.NORMAL)
            self.t_obj[5].delete(0, tk.END)
            self.t_obj[5].insert(0, self.conj.meaning)
            self.t_obj[5].grid(row=0, column=4, columnspan=3, pady=20, padx=5, sticky=tk.W)
            self.t_obj[2].config(state = tk.NORMAL)


    def t_t_grid(self):
        '''self.t_t_grid() -> custom init for Test Me! button
        continues on to start verb check and initializes all needed to be done'''
        self.f_s_grid_forget()
        # test me button chg to Submit button
        self.t_obj[2].config(command=self.t_r_grid, text='Submit')
        self.m_states['t']['gridded'] = 'testing' # Set state
        # Return to home button with not safe
        self.t_obj[3].config(command = lambda: self.m_grid(safe=False))
        # change title and make room for entry bar

        self.conj.meaning = self.t_obj[5].get()
        self.t_obj[4].grid_configure(columnspan=3)
        self.t_obj[5].grid_configure(columnspan=4,column=3)
        self.t_obj[5].delete(0, tk.END)
        self.t_obj[5].insert(0, 'to ')
        self.t_obj[5].focus_set()
        self.t_obj[5].bind('<Return>', lambda e: self.t_t_focus_set(index=-1))
        self.f_t_grid() # main gridding for inside canvas

    def t_t_focus_set(self, index: int, event=None):
        '''self.t_t_focus_set(index) -> handler method for <Return> callback when in entries and f_t_grid
            moves focus to next index of self.t_t_entriesEnabled and r_init if creates error'''
        try: self.t_t_entriesEnabled[index+1].focus_set()
        except IndexError: self.t_r_grid() # reached end of list


    def t_r_grid(self):
        '''self.t_r_grid() -> custom init for Continue button
        displays results of score after verb check and options.'''
        self.t_r_check_ans() # separate method to check answers and correlate with c_conj
        self.m_states['t']['gridded'] = 'review' # update state
        self.t_obj[5].unbind('<Return>') # unbind stuffs
        self.t_obj[0].delete(0, tk.END)
        self.t_obj[0].insert(0, "{}! — {}%".format(self.t_r_get_response(), self.t_r_score))
        self.t_obj[0].config(width=45)
        self.t_obj[3].config(command=self.m_grid) # forego the unsafe
        if self.t_obj[5].get() == self.conj.meaning: self.t_obj[5].config(fg='red')
        self.t_r_mistakes()

    def t_r_mistakes(self):
        '''self.t_r_mistakes() -> 1st handler method for View Corrections button
        Displays user input and mistakes'''
        for obj in self.f_frame.grid_slaves(): obj.grid_forget()
        self.t_obj[2].config(text="View Corrections", command=self.t_r_corrections)
        self.t_obj[4].config(text=self.conj.verb.title()+' - ')
        self.t_obj[4].grid(row=0, column=0, columnspan=3, pady=20, padx=5, sticky=tk.E)
        self.t_obj[5].grid(row=0, column=3, columnspan=4, pady=20, padx=5, sticky=tk.W)
        self.t_obj[5].config(state=tk.DISABLED)   
        self.m_states['c']['f_gridded']=False     
        self.f_t_grid(state='review') # reviewState 

    def t_r_corrections(self):
        '''self.t_r_correct() -> 2nd handler method for View Corrections button
        Allows user to compare user input with actual conjugation
        Toggles back and forth'''
        for obj in self.f_frame.grid_slaves(): obj.grid_forget()
        self.t_obj[2].config(text="View Mistakes", command=self.t_r_mistakes)
        self.t_obj[4].config(text="{} - {}".format(self.conj.verb.title(), self.conj.meaning))
        self.t_obj[4].grid(row=0, column=0, columnspan=7, padx=30, pady=40) # title label
        self.f_c_grid()
    


    def t_r_get_response(self):
        '''self.t_r_get_response() -> return method for witty comments
        Gives some sort of encouragement text after verb check
        Randomly picks from list organized by final score'''
        if 0<=self.t_r_score<30: return choice(self.t_r_responses[0])
        elif 30<=self.t_r_score<60: return choice(self.t_r_responses[1])
        elif 60<=self.t_r_score<85: return choice(self.t_r_responses[2])
        elif 85<=self.t_r_score<100: return choice(self.t_r_responses[3])
        else: return self.t_r_responses[4][0]

    def t_r_check_ans(self):
        '''self.t_r_check_ans -> part of custom t_r_init
        special method just for correlating user input with answers'''
        self.t_r_ans = {name: [[] for i in self.m_subOdr[name]] for name in self.m_odr}
        numRight, numWrong = 0,0
        for name in self.m_odr:
            obj = self.f_obj['t'][name]['e']
            for i in range(len(self.m_subOdr[name])):
                for j in range(len(self.conj.conj[name][self.m_subOdr[name][i]])):
                    if obj[i][j]['state'] == 'disabled': 
                        self.t_r_ans[name][i].append(True)
                        continue
                    if obj[i][j].get() == self.conj.conj[name][self.m_subOdr[name][i]][j]: 
                        self.t_r_ans[name][i].append(True)
                        numRight+=1
                    else: 
                        self.t_r_ans[name][i].append(False)
                        numWrong += 1
        self.t_r_score = 100*(numRight/(numRight+numWrong))
        weight=20
        defAns = self.t_obj[5].get() == self.conj.meaning
        self.t_r_score = round((self.t_r_score*(100-weight)+defAns*100*weight)/100, 2)

        print(self.t_r_score)





    def s_init(self):
        '''self.s_init() -> custom init for Settings dialog
        initializes all objects and checkbuttons'''
        for obj in self.m_obj: obj.grid_forget()
    
        # named because settings will be tweaked later
        self.s_mainLabel = tk.Label(self, text = "CincoMinutos Settings", font = 'Arial 18 bold')
        self.s_mainLabel.grid(row = 0, column = 0, columnspan = 3, pady = (10,20))

        # info for buttons - defaults will be applied if left blank
        self.s_obj, self.s_tkVars = [self.s_mainLabel], [] # var inits
        i = 0
        for title in self.s_objInfo:
            # Title object
            self.s_obj.append(tk.Label(self, text = title, font = "Arial 14 bold"))
            self.s_obj[-1].grid(row = i+1, column = 0, padx = (10,5), pady = (5,5))
            # if info left blank, set for default
            if not len(self.s_objInfo[title]): self.s_objInfo[title].extend(["On", True, "Off", False])
            # either bool or str, booleanVar for bool and stringVar for str
            # creates new tkVar corresponding to radiobuttons
            if isinstance(self.s_settings[title], bool): 
                self.s_tkVars.append(tk.BooleanVar(value= self.s_settings[title]))
            elif isinstance(self.s_settings[title], list): 
                self.s_tkVars.append(tk.StringVar(value = self.s_settings[title][0]))
            # creates radiobuttons
            for j in range(0, len(self.s_objInfo[title]), 2): # indices skip by 2 because odd indices are values
                # Each radiobutton
                self.s_obj.append(tk.Radiobutton(self, text = self.s_objInfo[title][j],\
                variable = self.s_tkVars[i], value = self.s_objInfo[title][j+1]))
                # select if list value of radiobutton is same as current settings
                if self.s_tkVars[i].get() == self.s_objInfo[title][j+1]: self.s_obj[-1].select()
                self.s_obj[-1].grid(row=i+1, column=j//2+1, padx=(5,5), pady=(5,5)) # j//2 because of skipping by 2
            i += 1

    
        # Save button
        self.s_obj.append(tk.Button(self, text = "Save", command = self.s_save, font = 'Arial 16 bold'))
        self.s_obj[-1].grid(row = 7, column = 1)
        # Return button
        self.s_obj.append(tk.Button(self, text = 'Return To Home', command = self.m_grid))
        self.s_obj[-1].grid(row = 7, column = 2)
    
    def s_save(self):
        '''self.s_save() -> handler method for save button
        Triggers self.s_file_save one way or another
        Creates messagebox confirming selection if user triggers offline mode'''
        if self.s_tkVars[1].get() and not self.s_settings['Offline Mode']: # if user wants to download verbs
            notice = 'Warning: The process of downloading information from 15000 sites takes about 5 hours to complete.\n\n'
            notice += 'This will take 24MB of space on your computer. During this time, do not close the computer'
            notice += 'or disconnect from WiFi or this process will terminate.\n\nDo you wish to continue?'
            self.s_file_save()
            if messagebox.askyesno("Warning: Download Conjugation", notice): 
                self.m_states['s']['downloading'] = True
                thread = threading.Thread(self.s_conj_download())
                thread.start() # don't freeze tkinter mainloop
                thread.join() # ends thread execution
                # can still conjugate verbs and GUI works while downloading verbs
                self.m_states['s']['downloading'] = False
        else: self.s_file_save()

    def s_file_save(self):
        '''self.s_file_save() -> part of s_file_save method
        opens settings file and adds keys and values to file
        changes Primary Website Source to list and user selected order'''
        with open(expanduser('~/Documents/CincoMinutos-master/settings.json'), 'w+') as f:
            i=0
            for key in self.s_settings: # changes all user inputs to settings
                if key == "Primary Website Source":
                    self.s_settings[key] = self.s_defaultSettings[key].copy()
                    if self.s_defaultSettings[key][1] == self.s_tkVars[i].get(): 
                        self.s_settings[key].reverse() # reverse if list in wrong order
                else: self.s_settings[key] = self.s_tkVars[i].get() # otherwise just set
                i+=1
            json.dump(self.s_settings, f, indent=2, ensure_ascii=False)
            self.conj.website_order = self.s_settings['Primary Website Source']

    def s_conj_download(self):
        '''self.s_conj_download() -> method for downloading all verbs and conjugations
        Finds gigantic list of all verbs from cooljugator.com
        Shows progress through a constantly master.update()d mainLabel
        Takes around 5 hours to complete method - only attempt on good Wifi and battery'''
        self.s_mainLabel['text'] = 'Do Not Close Application Nor Disconnect From Wifi.\
        \nIf you do so, this process will be terminated.'
        # re-grid after grid_forgetting all objects
        self.s_mainLabel.grid(padx=20,pady=20)
        self.master.update()
        startT = time()
        try: html = get("https://cooljugator.com/es/list/all")
        except:
            self.m_states['c']['offline'] = True
            self.s_mainLabel['text'] = "I'm offline!\nPlease Connect To WiFi and Try Again."
            return
        self.m_states['c']['offline'] = False
        soup = bs4.BeautifulSoup(html.content, 'html.parser')
        # content is parsed list of all verbs - some are archaic and no longer used
        content = [list(verb.children)[0].get_text() for verb in list(soup.find('div', \
        class_='ui segment stacked').children)[0].children][:-1]
        # Good for testing network speed
        print('List of verbs gathered in {:4f} seconds'.format(time()-startT))
        # NOT using tkinter's after method because only tracking time and no action after
        startT = time()
        with open(expanduser('~/Documents/CincoMinutos-master/verbconjugations.json'), 'wb+') as f:
            # iterates over gigantic slow loop
            for verb in range(len(content)):
                # Shows progress and elasped time
                self.s_mainLabel['text'] = 'Downloading verb "{}", {} of {}.\nElasped: {:.2f} minutes.'\
                .format(content[verb], verb+1, len(content), (time()-startT)/60)
                self.master.update()
                # Makes request to site - site depends on user's choice
                self.conj.find(content[verb])
                if self.conj.offline: self.m_states['c']['offline'] = True
                else: self.m_states['c']['offline'] = False
                if self.conj.conj != None and self.conj.meaning != None:
                    outData = {'verb': self.conj.verb, 'definition':self.conj.meaning,'source':self.conj.source,'conjugation':self.conj.conj}
                    f.write(json.dumps(outData, ensure_ascii=False).encode('utf-8'))
                    f.write('\n'.encode('utf-8'))
                elif self.m_states['c']['offline']: # if no Wifi breaks out of gigantic loop and stops file handling
                    self.s_mainLabel = "I'm offline!\nPlease Connect To WiFi and Try Again.\
                    \nAll Downloaded Verbs Have Been Saved.\nThis Process Is Now Terminated."
                    break





    def c_grid(self):
        '''self.c_grid() -> custom gridding for all objects of Conjugation dialog'''
        for obj in self.m_obj: obj.grid_forget()
        self.m_states['c']['many_verbs']=False
        self.f_frame.get_master_frame().grid(row=2, column=0, columnspan=9, padx=10, pady= 10) # ScrollFrame
        self.c_obj['m'][0].config(text='A Random Conjugated Verb')
        self.c_obj['m'][0].grid(row=0, column=0, columnspan=7, padx=30, pady=40) # title label
        self.c_obj['m'][1].grid(row = 0, column = 0, padx = 10, pady = (10,2), columnspan=7) # verb entry
        self.c_obj['m'][1].bind('<Return>', lambda e: self.c_refresh())
        self.c_obj['m'][2].grid(row = 0, column = 7, padx = 10, pady = (10,2)) # Conjugate! button
        self.c_obj['m'][3].grid(row = 0, column = 8, padx = 20, pady = (10,2)) # Return button
        self.a_grid(1,0, False, 'c')

    def c_refresh(self):
        '''self.c_refresh() -> handler method for Conjugate! button
        Encloses many other functions and displays differently'''
        if self.c_obj['m'][1].get() == 'Type here!': return
        startT = time()
        if len(self.c_obj['m'][1].get().split(',')) > 1:
            if self.m_states['c']['verbs_list'] is None:
                self.m_states['c']['verbs_list'] = \
                    [''.join(item.split('(')[0].split('+')[0].split(';')[0].replace(' ', '')) \
                    for item in self.c_obj['m'][1].get().split(',')] # all the splitting stuff
            self.m_states['c']['many_verbs']=True
            self.c_conj(self.m_states['c']['verbs_list'].pop(0)) # conjugate first index and remove
            if not len(self.m_states['c']['verbs_list']): self.m_states['c']['verbs_list'] = None # if at end revert
        else: 
            self.c_conj(self.c_obj['m'][1].get())
            self.m_states['c']['many_verbs']=False
            self.m_states['c']['verbs_list'] = None
        print('Finished processing in {:4f} seconds.'.format(time()-startT))
        if self.conj.conj is None:
            if self.conj.offline: 
                self.c_obj['m'][0]['text'] = "I'm Offline! Please Connect To WiFi and Try Again."
                self.m_states['c']['offline'] = True
            else: 
                self.c_obj['m'][0]['text'] = 'Invalid Verb "{}"! Please Try Again.'.format(self.conj.input)
                self.m_states['c']['offline'] = False
            self.f_c_grid_forget()
        else:
            self.c_obj['m'][0]['text'] = "{} - {}".format(self.conj.verb.title(), self.conj.meaning)
            self.f_c_grid()

    def c_replace(self, verb: str):
        '''self.c_replace(verb) -> method if diacritic mode is on
        replaces all diacritics with non-diacritic replacements'''
        replacements = { 'á': 'a', 'é': 'e', 'í':'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n', 'ü': 'u'}
        for item in replacements: verb = verb.replace(item, replacements[item])
        return verb
    
    def c_conj(self, verb: str):
        '''self.c_conj(verb) -> method for finding conjugation in list
        calls find method in conjugation module
        tries to find conjugation in file first if offline mode is on and selected to use
        otherwiese will iterate and use first selected source by user if possible'''
        if self.s_settings['Offline Mode'] and self.s_settings['Use Offline Conjugation']: # both be true
            try:
                for dct in self.s_allVerbs: # look through whole file to see which matches
                    if not self.s_settings['Diacritic Sensitive'] and self.c_replace(dct['verb']) == verb.lower()\
                        or self.s_settings['Diacritic Sensitive'] and dct['verb'] == verb.lower(): 
                        self.conj.verb, self.conj.meaning = dct['verb'], dct['definition']
                        self.conj.source, self.conj.conj = dct['source'], dct['conjugation']
                        print('Found offline!')
                        self.m_states['c']['foundOffline'] = True
                        return # no need to lookup online
            except Exception as e: print(e)
        self.conj.find(verb)


    def ab_grid(self):
        '''self.ab_grid() -> custom gridding for About dialog'''
        for obj in self.grid_slaves(): obj.grid_forget()
        self.ab_obj[0].grid(row = 0, column = 0, padx = 10, pady = 10)
        self.ab_obj[1].grid(row = 1, column = 0, padx = 10, pady = 10)



if __name__ == '__main__':
    root = tk.Tk()
    root.title('¡Cinco Minutos!')
    root.bind("<Escape>", lambda e: root.destroy())
    # removes window if Esc button pressed
    frame = CincoMinutos(root)
    root.attributes("-topmost", True)
    root.attributes("-topmost", False)
    while True:
        try: 
            frame.mainloop()
            try: root.destroy()
            except: pass
            break
        except UnicodeDecodeError: pass
