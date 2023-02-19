#!/usr/bin/env python3
# -*- coding: <utf-8> -*-

'''File for ScrollFrame'''
import sys
import tkinter as tk


class ScrollFrame(tk.Frame):
    '''ScrollFrame(master) -> ScrollFrame object
        Creates a canvas for Tkinter GUI - subclass
        Used for displaying conjugation of verb in pretty format
        Has x and y scrollbars and fancy fonts'''
    
    def __init__(self, master, width=500, height=600, *args, **kwargs):
        '''self.__init__(master, width=100, height=50, *args, **kwargs) -> class init
        Creates a frame to put the canvas and scroll bars in, and the 
        canvas creates another frame window to put labels and
        objects in. *args and **kwargs get passed into master frame
        Note - DO NOT PUT TKINTER OBJECTS INTO MASTER FRAME
        Master of Tkinter objects must be self.get_master_frame()'''

        self.frame = tk.Frame(master, *args, **kwargs)
        '''self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)'''
        self.master = master
        self.width, self.height = width, height
        # Canvas from master frame - master is master frame
        self.canvas = tk.Canvas(self.frame) # dimensions passed
        self.canvas.grid(row=0,column=0)

        # Scrollbars - master is master frame
        # But command changes canvas view
        self.scrolly = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrolly.grid(row=0, column=1, sticky=tk.NS) # Y
        self.canvas.configure(yscrollcommand=self.scrolly.set)

        self.scrollx = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scrollx.grid(row=1, column=0, sticky=tk.EW) # X
        self.canvas.configure(xscrollcommand=self.scrollx.set)

        # Sub-frame - master is canvas
        # Actually used for gridding objects - self is subframe
        tk.Frame.__init__(self, self.canvas, bd=2)
        # Canvas creates frame as window
        self.canvas.create_window((0,0),window=self,anchor='n')
        self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL),width=self.width,height=self.height)

        # Scroll bindings
        self.bind("<Configure>",self._config)
        self.bind("<MouseWheel>", self._on_mousewheel)
        self.bind("<Button-2>", self._on_mousewheel)
        self.bind("<Button-1>", self._on_mousewheel)
    
    def _config(self, event):
        '''self._config(event) -> protected handler bind method
        handles Configure binding'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"),width=self.width,height=self.height)

    def _on_mousewheel(self, event, *args, **kwargs):
        '''self._on_mousewheel(event) -> protected handler bind method
        handles MouseWheel & others binding'''
        if sys.platform == 'win32':
            self.canvas.yview_scroll(-1*(event.delta/120), "units")
        elif sys.platform == 'darwin':
            self.canvas.yview_scroll(-1*(event.delta), "units")
    
    def get_master_frame(self):
        '''self.get_master_frame() -> get callable for actual master frame'''
        return self.frame
