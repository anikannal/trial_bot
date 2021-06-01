# -*- coding: utf-8 -*-
"""
Created on Sat May 29 11:48:43 2021

@author: anika
"""
import json
import random

class Riddle():
    def __init__(self,_type,_time,_clues,_answer):
        self.type = _type
        self.time = _time
        self.answer = _answer
        self.clues = _clues
        self.counter = len(self.clues)
    
    def next_clue(self):
        if self.counter == 0:
            return 0
        else:
            clue = self.clues[len(self.clues)-self.counter]
            self.counter = self.counter-1
            return clue
        
    def get_answer(self):
        return self.answer
    
    def get_type(self):
        return self.type
    
    def get_time(self):
        return int(self.time)
        
class Riddler():
    def __init__(self):
        f = open('../datafile.json',)
        self.riddles = json.load(f)
        f.close()
        self.answer = 0
    
    def get_riddle(self,_id=0):
        if _id==0:
            temp = random.choice(self.riddles)   
        else:
            for i in self.riddles:
                if i['id']==str(_id):
                    temp = i
                    break
                    
        _type = temp['type']
        _time = temp['time']
        _clues = [[clue['clue'],clue['illustration']] for clue in temp['clues']]
        _answer = temp['answer']    
        riddle = Riddle(_type,_time,_clues,_answer)
        return riddle