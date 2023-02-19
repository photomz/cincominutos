#!/usr/bin/env python3
# -*- coding: <utf-8> -*-

'''File for creating Conjugation''' 
import bs4
import threading
from requests import get
from re import compile

from data import Data

class Conjugation:
    '''Conjugation() -> Conjugation class
    Class for finding verb conjugations from SpanishDict and WordReference'''

    def __init__(self, website_order, master):
        self.offline, self.verb, self.input = False, None, None
        self.master = master
        self.conj = False
        self.meaning, self.source = '',''
        self.website_order = website_order
        dataFile = Data()
        self.odr, self.subOdr, self.estar = dataFile.order, dataFile.subOrder, dataFile.estar

    def _get(self, link:str):
        self.html = get(link)

    def _online_get(self, verb: str, site: str):
        '''self._online_get(verb, site) -> part 1 of web-scraping method
        makes requests to server and web-scrapes into messy lists
        part one of finding conjugation - needs to pass through if statement in calling method
        Uses bs4 and requests'''
        site = site.lower()
        assert site == "spanishdict" or site == "wordreference"
        if site == 'spanishdict': 
            try: 
                thread = threading.Thread(self._get("http://www.spanishdict.com/conjugate/{}".format(verb)))
                self.master.after(5000, lambda: thread.join())
                thread.start()
                thread.join()
            except: # any exception gets handled
                self.offline = True # assumes a network problem
                return [] # returns empty list
            self.offline = False
            soup = bs4.BeautifulSoup(self.html.content, 'html.parser')
            content = []
            for conj in soup.find_all(class_='vtable-word-text'):
                # removes tag class into str if not already str and joins list together
                content.append(''.join([each if not isinstance(each,bs4.element.Tag) else \
                each.get_text() for each in list(conj.children)]))
            # web-scrape definition of verb
            try: content.append(''.join([each if not isinstance(each,bs4.element.Tag) else \
                each.get_text() for each in soup.find(class_='el')]))
            except TypeError: return [] # if spanishdict re-directed to some weird page
            # makes sure verb displayed on website is same as args
            self.verb = soup.find(class_='source-text').get_text()
            return content # if all goes well, returns a proper list
            
        else:
            try:
                # 2 different websites for conjugation and definition
                thread = threading.Thread(self._get('http://www.wordreference.com/es/en/translation.asp?spen={}'.format(verb)))
                self.master.after(7000, lambda: thread.join())
                thread.start()
                thread.join()
                self.meaning = self.html
                thread = threading.Thread(self._get("http://www.wordreference.com/conj/EsVerbs.aspx?v={}".format(verb)))
                thread.start()
                thread.join()
            except: # any exception gets handled
                self.offline = True # assumes a network problem
                return [] # returns empty list
            self.offline = False
            # makes 2 bs4 objects
            soup = bs4.BeautifulSoup(self.html.content, 'html.parser')
            soup2 = bs4.BeautifulSoup(self.meaning.content, 'html.parser')
            content = []
            # class neoConj is all Indicative, Subjunctive, etc
            for conj in soup.find_all(class_='neoConj'):
                content.extend([each if not isinstance(each,bs4.element.Tag) else each.get_text() \
                for each in list(conj.find_all('td'))])
            # progressive and perfects only list participles
            # add padding of len 15 to get calling method to accept len of content
            content.extend(['' for i in range(15)])
            try: # finds participles and does some processing later
                # weird style for participles
                content.append([each if not isinstance(each,bs4.element.Tag) else each.get_text() \
                for each in list(soup.find('td', {'style':"vertical-align:top;padding-left: 4em;"}).children)])
                # takes first element of split (,)
                content[-1] = ''.join(['  ' if each == '' else each for each in content[-1]]).split('  ')[1].split(', ')[0]
            except AttributeError: return [] # if doesn't exist because of some weird re-direct
            meanings = []
            # classes even and odd are some weird wordReference organization of definitions
            for td in soup2.find_all(class_='even')+soup2.find_all(class_='odd'):
                # find class within first class
                if td.find(class_='ToWrd') is not None:
                    tagAndStr = list(td.find(class_='ToWrd').children)
                    if isinstance(tagAndStr[0], bs4.element.Tag): # if first element is tag
                        meanings.append(tagAndStr[1]) # then get second element
                    else: meanings.append(tagAndStr[0])
            # last element is definition
            content.append(', '.join(meanings[:5])) # join together all meanings, with max of 5
            if not len(content[-1]): # sometimes definitions appear weirdly
                meaning = soup2.find(id='clickableHC')
                try: meaning = list(meaning.find_all(text = compile('to'))) # find all with "to"
                except AttributeError: return []
            # odd html stuff - makes sure verb on webpage is same as args
            self.verb = soup.find('span', id='noteImport2').next_sibling.next_sibling.get_text()
            return content
        return [] # if not either ifs then it is weird and return empty list

    def _online_parse(self, verb: str, site: str, content: list):
        '''self._online_parse(verb, site, content) -> part 2 of web-scraping method
        reorganizes and reindexes unorganized content list into a good list'''
        if site.lower() == 'spanishdict':
            # first separate by top-level order - Indicative, Subjuctive, etc
            unformatted = {self.odr[0]: content[:30],
                           self.odr[1]: content[30:54],
                           self.odr[2]: content[54:64],
                           self.odr[3]: content[64:94],
                           self.odr[4]: content[94:124],
                           self.odr[5]: content[124:-1]
                           }
            conjugation = {category: {} for category in self.odr} # create blank dicts
            for current in unformatted:
                for index in range(len(self.subOdr[current])):
                    # skips over indexes and reorganizes from Yo-starting lists to Present-starting lists

                    # como, comí, comía, comería, comeré  ->  como, comes, come, comemos, coméis, comen
                    conjugation[current][self.subOdr[current][index]] = [unformatted[current][conj].lower() for conj\
                     in range(index, len(unformatted[current]), len(self.subOdr[current]))] # skip by length of sub-category

        elif site.lower() == 'wordreference':
            refl = verb[-2:] == 'se' and content[0][:3] == 'me ' #reflexive or not - important in adding estar conjugations to progressive
            content = [item.lower() for item in content]
            # Gigantic unorganized list in need of better organzing
            # Dict comp and list comp is used when possible
            conjugation = {self.odr[0]: # Indicative
                                {self.subOdr[self.odr[0]][0]: content[:6], self.subOdr[self.odr[0]][1]: content[14:20], 
                                self.subOdr[self.odr[0]][2]: content[7:13], self.subOdr[self.odr[0]][3]: content[28:34], 
                                self.subOdr[self.odr[0]][4]: content[21:27]},
                           self.odr[1]: # Subjunctive
                                {self.subOdr[self.odr[1]][0]: content[63:69], 
                                # separate -ra and -se imperfect subjunctive conjugations
                                self.subOdr[self.odr[1]][1]: [conj.split(' o ')[0] for conj in content[70:76]],
                                # also might use "u" to serpate as well as "o" - really just many if and elif statements in list comp
                                self.subOdr[self.odr[1]][2]: [conj.split(' u ')[1] if len(conj.split(' o ')) == 1 and \
                                    len(conj.split(' u ')) == 2 else conj.split(' o ')[1] if len(conj.split(' o ')) == 2 else conj \
                                    for conj in content[70:76]], 
                                self.subOdr[self.odr[1]][3]: content[77:83]},
                           self.odr[2]: # Imperative
                                {self.subOdr[self.odr[2]][0]: content[106:111], self.subOdr[self.odr[2]][1]: content[113:118]},
                           self.odr[3]: # Progressive
                                # content[-2] is gerund (-ando) and does dict comp and list comp
                                # if refl is False, goes to non-reflexive list, and reflexive otherwise
                                {self.subOdr[self.odr[3]][i]: [j + ' ' + content[-2] for j in \
                                    self.estar[refl][i]] for i in range(len(self.subOdr[self.odr[3]]))},
                           self.odr[4]: # Perfect
                                {self.subOdr[self.odr[4]][0]: content[35:41], self.subOdr[self.odr[4]][1]: content[119:125],
                                self.subOdr[self.odr[4]][2]: content[42:48], self.subOdr[self.odr[4]][3]: content[56:62], 
                                self.subOdr[self.odr[4]][4]: content[49:55]},
                           self.odr[5]: # Perfect Subjunctive
                                {self.subOdr[self.odr[5]][0]: content[84:90], 
                                # same as sunjunctive
                                self.subOdr[self.odr[5]][1]: [conj.split(' o ')[0] + ' ' + conj.split(' o ')[1].split()[1] for conj in content[91:97]],
                                self.subOdr[self.odr[5]][2]: content[98:104]}
                           }
        # meaning is last index
        self.meaning = content[-1]
        return conjugation

    def find(self, verb: str):
        '''self.find(verb) -> method for finding conjugation in list
        calls _online_get and _online_parse
        tries to find conjugation in file first if offline mode is on and selected to use
        otherwiese will iterate and use first selected source by user if possible'''
        self.input = verb
        for site in self.website_order: # iterate through each site
            # first do request handling
            content = self._online_get(verb, site.lower())
            # make sure that len if correct and conjugation is accurate
            if len(content) == 143:
                # if user-entered verb is reflexive but the conjugation is not, then use other site
                if verb[-2:] == 'se' and content[0][:3] != 'me ': continue
                # then organize list'''
                self.conj = self._online_parse(verb, site.lower(), content)
                self.source = site
                break
        else: self.conj = None # nothing if all else fail

    def __str__(self):
        '''self.__str__() -> method for turning list into strings
        used for conjugation and prettifying list'''
        if self.conj is None: return None
        strConj = ''
        for dct in self.conj:
            strConj += '\n{}\n'.format(dct.upper())
            for lst in self.conj[dct]:
                strConj += "{:12} {}\n".format(lst + ':', ', '.join(self.conj[dct][lst]))
        else: strConj += '\n\nData retrieved from {}'.format(self.source)
        return strConj

if __name__ == "__main__":
    import tkinter as tk
    conj = Conjugation(["SpanishDict", "WordReference"], tk.Tk())
    conj.find(input("Conjugate a Verb: ").lower())
    print(str(conj))