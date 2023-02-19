=======
INSTALL
=======
Welcome to CincoMinutos! You are only one step away from finalizing your installation. Read the directions below to finish installing.

#######################################################################################
SYSTEM REQUIREMENTS
	* Mac running OS X 10.10+
	* An installation of Python 3 (located under /Library/Frameworks/Python.framework/Versions)
		* If you are unsure whether you have Python 3 installed, go to Terminal and type in "python3 -V". If it says invalid command, you must install Python 3.
		* If not installed, please download and install the .pkg file from this link - https://www.python.org/ftp/python/3.6.7/python-3.6.7-macosx10.9.pkg - or go to the Python foundation website and download the MacOS version.

#######################################################################################
INSTRUCTIONS
Follow these instructions to complete the installation of CincoMinutos:
	* Open setup.command - You must go to System Preferences > Security & Privacy and click on the button "Open Anyway" to allow the installation to execute.
	* Open CincoMinutos.app - now under the Applications folder - and go through the same dialogs as in step 1 to execute.
	* Add to dock (Optional) - for easy access for verb checks

#######################################################################################
WARNINGS
	* Do not run setup.command if CincoMinutos installation folder is not under the Downloads folder
	* Do not abort WiFi connection while executing setup.command
	* Do not edit verbconjugations.json
	* Do not mess with python source code or json files if not proficient in code
	* Do not run CincoMinutos with multiple installations of Python 3 - this can cause problems - if you are unsure about this, open Terminal and type in "open /Library/Frameworks/Python.framework/Versions"
#######################################################################################



===========
REPORT BUGS
===========
To report a bug, please send a screenshot to <markuszhang8@gmail.com> of the error with detailed instructions on how you arrived at the error. Also send a screenshot of the settings dialog in the application, along with any other information you might find useful. Any reported bugs would come a long way in improving the product.



========
AUTHORS
========
Primary Author - Markus Zhang



=======
THANKS
=======
To Español 2M Honores of the class of 2023 of the Harker School

To Señora Pinzás, whose verb checks inspired me to create this application.

To all my friends who provided me with resources to complete the project and encouraged me to create this application.

A special thanks to my parents for relentlessly supporting me in anything I do, whether it be front-end development or just programming in general.



=======
LICENSE
=======
Copyright © 2018 <Markus Zhang>
CincoMinutos is licensed under an MIT License.
In layman's terms, this is a very permissive license that gives you the right to edit, modify, repurpose, and relicense the Software with attribution to the original Author. The Author is not responsible for any damage caused to the System by the Software.
For more details, see LICENSE.txt



=========
CHANGELOG
=========
2018-07-02 Markus Zhang <markuszhang8@gmail.com>
	* version0
	* Offline conjugation script created
	* (Now Incompatible)

2018-07-17 Markus Zhang <markuszhang8@gmail.com>
	* version1
	* Web-scraping function created (from SpanishDict), uses bs4

2018-07-23 Markus Zhang <markuszhang8@gmail.com>
	* version2
	* Tkinter GUI created - one dialog
	* Conjugation now displays on tkinter Label

2018-07-29 Markus Zhang <markuszhang8@gmail.com>
	* version3
	* Conjugation function separated to systemConj1 & systemConj2
	* version3 (systemConj1) - site names are arguments
	* version3 (self.c_estar) - estar conj for WordReference progressive

2018-08-17 Markus Zhang <markuszhang8@gmail.com>
	* version4 (funcOffline) - parses list of verbs and runs findConj through each
	* version4 (__init__) - retrieves settings from settings.json
	* settings.txt (~160B) - saves settings in file
	* verbConjugations.txt (~23MB) - saves 8000 verbs and conjugations in file
	* version4 (findConj) - attempts to find verb from verbConjugations.txt if offlineMode is selected in settings.txt

2018-08-30 Markus Zhang <markuszhang8@gmail.com>
	* version5.0 (m_init) - multiple dialogs
	* version5.0 (s_init) - Dialog for changing settings

2018-09-07 Markus Zhang <markuszhang8@gmail.com>
	* version5.1 - python3 encoding specified - first 2 lines
	* version5.1 (m_accentInit) - adds accent buttons and binds to callback
	* version5.1 (m_accentAdd) - callback bind and adds to whatever entry
	* version5.1 (t_m_init) - main dialog created, similar to c_init
	* version5.1 (t_m_scopeInit) - collection of checkbuttons to choose what to test 
	* version5.1 (t_in_init, t_su_init, t_im_init, etc.) - repetitive dialogs for each main category of conjugations

2018-09-26 Markus Zhang <markuszhang8@gmail.com>
	* version5.2 - commenting and docstrings created
	* version5.2 (t_in_init, t_su_init, etc -> t_t_init) - concentrates each dialog into one big function, abbreviation passed in as arguments, t_t_initInfo used as gridding information
	* version5.2 (t_focusSet) - many arguments passed to make sure correct entry is focused in <Return> bind
	* version5.2 (t_r_init) - reviewing dialog with score and button to review mistakes
	* version5.2 (t_r_checkAns) - corroborates user input with c_conj
	* version5.2 (t_c_init) - same as t_t_init except to review mistakes - Labels instead of Entries & accent buttons

2018-10-08 Markus Zhang <markuszhang8@gmail.com>
	* version6 - gridding under _objects
	* version6 (s_init) - dynamically created radio buttons
	* version6 (t_c_init) - merged with t_t_init and reviewState arg passed
	* version6 (t_t_init) - objects called under name, abbrev incompatible
	* version6 (t_r_checkAns) - shortens and more efficient
	* version6 - Imperative & scope incompatibility solved

2018-10-29 Markus Zhang <markuszhang8@gmail.com>
	* version7 - settings.txt -> settings.json
	* version7 - verbConjugations.txt -> verbconjugations.json
	* version7 (class ScrollFrame) - scrollable frame
	* version7 (c_init) - displays conjugation under scrollable frame

2018-11-16 Markus Zhang <markuszhang8@gmail.com>
	* version8 - new initialization method - initializes ALL objects at start and grids then later
	* version8 - test def of verb & edit def
	* version8 - verb check under ScrollFrame
	* version8 - all objects are gridded at index
	* version8 - (m_init -> m_grid, t_m_init -> t_m_grid, etc)
	* version8 - (m_init, t_m_init, etc)
	* version8 (f_c_init, f_c_grid) - category for conjugation scroll frame objects
	* version8 (t_t_init -> f_t_grid, t_m_continue -> t_t_grid)
	* version8 (t_t_focus_set) - highly simplified, simply grids next index
	* version8 - _objects -> _obj

2018-11-18 Markus Zhang <markuszhang8@gmail.com>
	* release1.0 - modularization
	* scrollframe.py - class ScrollFrame
	* conjugation.py - class Conjugation for finding conjugation
	* data.py - class Data for any python lists/dicts to store
	* __init__.py - detailed documentation & validates directory
	* setup.command - bash script for installing CincoMinutos
	* LICENSE.txt - MIT License
	* CincoMinutos.app - Automator application & calls __main__.py

2018-11-19 Markus Zhang <markuszhang8@gmail.com>
	* CincoMinutos-master created
	* About dialog in CincoMinutos created

2018-11-20 Markus Zhang <markuszhang8@gmail.com>
	* conjugation.py (_online_get) - now uses multithreading and tinter after
	* __main__.py (s_conj_download) - now uses multithreading to keep maintop active
