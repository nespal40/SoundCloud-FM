from math import pow
import pygame.mixer as mixer
from random import randint as rn

import pygame.time


class Sound():
    def __init__(self,sound_name,sample_rate=44100):
        self.sound = mixer.Sound(sound_name)
        self.sample_rate = sample_rate
        self.sound_name = sound_name

        self.length = self.sound.get_length()
        self.play_sound = None

    def set_volume(self,volume):
        self.sound.set_volume(volume)

    def play(self,loops = 0):
        self.sound.play(loops=loops)

    def stop(self):
        self.sound.stop()

class Mark():
    def __init__(self,list_sounds:list[str],frequency,strength):
        self.tracklist = [Sound(name_) for name_ in list_sounds]
        self.queue_played = []
        self.index_play = rn(0,len(self.tracklist)-1)

        self.frequency = frequency
        self.strength = strength

        self.now_play = self.tracklist[self.index_play]
        self.last_play = None
        self.now_play.set_volume(0)
        self.now_play.play(loops=0)
        self.offset_sound = pygame.time.get_ticks()/1000   #seconds

        self.active = False
        self.volume = 0
        self.save_volume = 0

    def get_music(self):
        pass

    def update(self):
        sec = pygame.time.get_ticks()/1000

        if sec - self.offset_sound <= 2:        #доделат
            kn = pow((sec - self.offset_sound)/2,2)
            kl = pow((sec - self.offset_sound-2)/2, 2)

            self.upd_volume(self.volume,kn,1)
            if self.last_play != None:
                self.upd_volume(self.volume,kl,2)
                if kl <=0.2:
                    self.last_play.stop()
                    self.upd_volume(self.volume, 1, 1)

        elif sec - self.offset_sound >= self.now_play.length-2:
            self.last_play = self.now_play
            if len(self.tracklist) >1:
                self.queue_played.append(self.index_play)
                old_i = self.index_play

                if len(self.tracklist) == len(self.queue_played):
                    self.queue_played = []

                    while old_i == self.index_play:
                        self.index_play = rn(0, len(self.tracklist) - 1)
                else:
                    while self.index_play in self.queue_played:
                        self.index_play = rn(0, len(self.tracklist) - 1)

            self.now_play = self.tracklist[self.index_play]
            self.upd_volume(self.volume)
            self.now_play.play(loops=0)

            self.offset_sound = sec

    def upd_volume(self,volume,k=1.0,channel = 1):    #0-1(float)
        self.volume = volume

        if channel == 1:
            self.now_play.set_volume(self.volume*k)
        elif channel == 2:
            self.last_play.set_volume(volume*k)

    def stop(self):
        self.now_play.stop()

class FM():
    def __init__(self,volume,frequency,marks:list[Mark]=None):
        self.volume = volume
        self.frequency = frequency

        self.noise = Sound('assets/musics/noise.mp3')
        self.marks = marks

        self.noise.play(-1)
        self.set_volume(self.volume)

    def set_volume(self,volume):
        self.volume = volume
        self.set_frequency(0,-1)

    def update(self):
        for mark in self.marks:
            mark.update()

    def set_frequency(self,frequency,df=0):
        if df == 0:
            self.frequency = frequency
        near_up = [-1,0,0]      #индекс, расстояние, сила
        near_down = [-1,0,0]

        for mark in self.marks:
            mark.active = False

            df = self.frequency-mark.frequency
            if df>=0:
                if near_down[1] >df or near_down[0] == -1:
                    near_down[0] = self.marks.index(mark)
                    near_down[1] = df
                    near_down[2] = max(mark.strength-abs(df),0)/mark.strength
            else:
                if near_up[1] <df or near_up[0] == -1:
                    near_up[0] = self.marks.index(mark)
                    near_up[1] = df
                    near_up[2] = max(mark.strength-abs(df),0)/mark.strength

        if near_up[0] != -1:
            if self.marks[near_up[0]].volume >self.volume/100*near_up[2]:
                self.marks[near_up[0]].active = True
                print(near_up)
            self.marks[near_up[0]].upd_volume(self.volume/100*near_up[2])
        if near_down[0] != -1:
            if self.marks[near_down[0]].volume >self.volume/100*near_down[2]:
                self.marks[near_down[0]].active = True
                print(near_down)
            self.marks[near_down[0]].upd_volume(self.volume/100*near_down[2])

        self.noise.set_volume((1-max(near_up[2],near_down[2]))*self.volume/100*2)