from os.path import isdir
from random import choice as ch
from os.path import isdir
from os import listdir
import math, pygame
from FM import *

mixer.pre_init(44100,-16,3,512)

pygame.init()

THEME_COLORS ={         #bg,main,sub,sub2,text
    "BLACK/ORANGE":[(0,0,15),(255,70,1),(207,18,72),(255,170,101),(255,255,255)],
    "BLACK/WHITE":[(0,0,15),(225,225,225),(152,170,185),(91,104,114),(0,0,0)],
    "BLUE/RED":[(8,32,48),(172,50,50),(154,34,34),(103,157,193),(255,255,255)],
    "PURPLE/GREEN":[(38,10,55),(20,64,75),(37,75,20),(92,138,149),(255,255,255)],
}

def gtc(i):         #get theme color -> color of the choose theme
    if i == 0: return THEME_COLORS["BLACK/ORANGE"]
    elif i == 1: return THEME_COLORS["BLACK/WHITE"]
    elif i == 2: return THEME_COLORS["BLUE/RED"]
    elif i == 3: return THEME_COLORS["PURPLE/GREEN"]

def load():         # -> data in save-file
    ret = []
    with open('assets/data.txt',mode='r',encoding='utf-8') as file:
        while True:
            n = file.readline()
            if n != '':
                try:
                    ret.append(float(n))
                except:
                    ret.append(80)
            else:
                break

    print(ret)
    return ret

def get_distance(p1,p2):        # -> distance between two points
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def clamp(value,min_,max_):         # -> the changes value
    return max(min(value,max_),min_)


class Image():
    def __init__(self, image:pygame.Surface):
        self.image = image

    def W(self):
        return self.image.get_width()

    def H(self):
        return self.image.get_height()

    def fill_bg(self,color=(0,0,0)):
        srf = pygame.Surface(self.image.get_size())
        srf.fill(color)
        srf.blit(self.image,(0,0))
        return Image(srf)

    def re_size(self,nw,nh):
        return pygame.transform.scale(self.image,(nw,nh))

    def re_size_k(self,k):
        return pygame.transform.scale(self.image,(self.W()*k,self.H()*k))

    def rotate(self,angle):
        return pygame.transform.rotate(self.image,angle/math.pi*180)

    def clamp(self,w,h,offset_x,offset_y,color = (0,0,0)):
        srf = pygame.Surface((w,h))
        srf.fill(color)
        srf.blit(self.image,(offset_x,offset_y))
        return srf

def sqrt(x): return x**0.5
def linear(x): return abs(x)
def quadratic(x): return x**2
def cubic(x): return abs(x**3)
def easeInOutQuad(x):
    if (x < 0.5): return 2.0 * x * x
    z = 1 - x
    return 1 - 2.0 * z * z
def easeInOutBack(x):
    c1 = 1.70158
    c2 = c1 * 1.525

    return (math.pow(2 * x, 2) * ((c2 + 1) * 2 * x - c2)) / 2 if x < 0.5 else (math.pow(2 * x - 2, 2) * (
                (c2 + 1) * (x * 2 - 2) + c2) + 2) / 2
def easeOutElastic(x):
    c4 = (2 * math.pi) / 3

    if x == 0:return 0
    if x == 1: return 1
    return math.pow(2, -10 * x) * math.sin((x * 10 - 0.75) * c4) + 1
def easeInElastic(x):
    c4 = (2 * math.pi) / 3

    if x == 0: return 0
    if x == 1: return 1
    return -math.pow(2, 10 * x - 10) * math.sin((x * 10 - 10.75) * c4)

class Animation:
    def __init__(self,start,min_k,max_k,time_,FPS,func,clock:pygame.time.Clock):
        self.range_k = [min(min_k,max_k),max(min_k,max_k)]
        self.time = time_ if time_ >0 else 1
        self.FPS = FPS
        self.clock = clock

        self.ticks = self.time*FPS if time_>0 else 1
        self.c = 0 if start else self.ticks
        self.different_range = abs(self.range_k[1]-self.range_k[0])

        self.func = func
        self.forward = 0        # >0 - forward, 0 - pause, <0 - backward

    def __call__(self, *args, **kwargs):
        k = self.func(self.c/self.ticks)
        rk = self.range_k[0]+self.different_range*k

        return rk #self.k

    def update(self):
        if self.forward != 0:
            self.c += 1*self.forward
            target = 0 if self.forward<0 else self.ticks
            if self.c >self.ticks or self.c < 0:
                self.c = target

    def update_state(self,nstate):
        self.forward = nstate

class Slider():
    def __init__(self,rect,color,range_value,value,text,radius_button,image:Image=None,second_image:Image=None):
        self.x = rect[0]
        self.y = rect[1]
        self.width = rect[2]
        self.height = rect[3]
        self.kx = 10

        self.color = color

        self.radius_button = radius_button
        self.color_button = [min(c+15,255) for c in color]
        self.under_color_button = [min(c+45,255) for c in color]
        self.press_color_button = [max(c-45,0) for c in color]

        self.range_value = range_value
        self.value = value

        self.under_mouse = False
        self.press = False

        self.start_text = text
        if self.start_text:
            self.font = pygame.font.SysFont('comicsans', 15)
            self.text = self.font.render(self.start_text+str(round(self.get_value())),False,(255,255,255))

        self.image = image
        self.second_image = second_image
        if self.image != None:
            if self.value <= 0.05 and self.second_image != None:
                self.draw_image = self.second_image.image
            else:
                self.draw_image = self.image.clamp(self.image.W() * ((max(self.value + 0.15, 0.25)) // 0.25 * 0.25), self.image.H(), 0, 0)

    def repaint(self,index_gtc,image_volume=None,image_volume_mute=None):
        color = gtc(index_gtc)[1]

        self.color = color
        if self.second_image != None: self.second_image = image_volume_mute
        if self.image != None:
            self.image = image_volume

            if self.value <= 0.05 and self.second_image != None:
                self.draw_image = self.second_image.image
            else:
                self.draw_image = self.image.clamp(self.image.W() * ((max(self.value + 0.15, 0.25)) // 0.25 * 0.25),
                                                   self.image.H(), 0, 0)

        self.color_button = [min(c + 15, 255) for c in color]
        self.under_color_button = [min(c + 45, 255) for c in color]
        self.press_color_button = [max(c - 45, 0) for c in color]

    def get_value(self):
        return self.range_value[0]+self.value*(self.range_value[1]-self.range_value[0])

    def get_pos_button(self):
        return (self.x+self.kx + (self.width-self.kx*2)*self.value,self.y+self.height//2)

    def update(self,mp):
        if self.press:
            self.value = clamp(mp[0]-(self.x+self.kx),0,self.width-self.kx*2)/(self.width-self.kx*2)
            if self.start_text:
                self.text = self.font.render(self.start_text+str(round(self.get_value())),False,(255,255,255))
            if self.image!=None:
                if self.value <= 0.05 and self.second_image != None:
                    self.draw_image = self.second_image.image
                else:
                    self.draw_image = self.image.clamp(self.image.W()*((max(self.value+0.15,0.25))//0.25*0.25),self.image.H(),0,0)
        else:
            if get_distance(mp,self.get_pos_button()) < self.radius_button+3:
                self.under_mouse = True
            else:
                self.under_mouse = False

    def draw(self,surface):
        if self.image!=None:
            surface.blit(self.draw_image,self.draw_image.get_rect(bottomleft=(self.x+self.width-self.image.W()-5,self.y-12)))

        pygame.draw.rect(surface,self.color,(self.x,self.y,self.width,self.height),0,4)
        pygame.draw.rect(surface,[max(c-20,0) for c in self.color],(self.x+3,self.y+3,self.width-6,self.height-6),0,4)
        color_button = self.color_button
        if self.under_mouse: color_button = self.under_color_button
        if self.press: color_button = self.press_color_button

        pygame.draw.circle(surface,color_button,self.get_pos_button(),self.radius_button)
        pygame.draw.circle(surface,(0,0,0),self.get_pos_button(),self.radius_button*0.7)
        if self.start_text:
            surface.blit(self.text,(self.x,self.y+20))

class RotateButton():
    def __init__(self,rect,image:Image,range_angle,value,range_value,index_gtc):
        self.x,self.y = rect

        self.button_image = image
        self.draw_image = self.button_image.image
        self.theme_index = index_gtc
        self.range_value = range_value

        self.font = pygame.font.SysFont('comicsans', 24,True)
        self.image_pr = Image(pygame.Surface((5000,40)))
        self.image_pr.image.fill(gtc(self.theme_index)[1])
        for i in range(range_value[0]-8,range_value[1]+6):
            txt = self.font.render(str(i),False,gtc(self.theme_index)[4])
            x = (i-range_value[0]+8)/5*150
            if i%5==0:
                self.image_pr.image.blit(txt,txt.get_rect(center=(x,20)))
            else:
                pygame.draw.rect(self.image_pr.image,gtc(self.theme_index)[0],(x-2,10,4,20),0,5)
        self.draw_image_pr = self.image_pr.clamp(300,50,0,-5,gtc(self.theme_index)[2])

        self.value = value      #[-90,-1890]

        self.range_value = range_value

        self.range_angle = range_angle
        self.angle =  self.get_angle()
        self.offset_angle = 0
        self.last_delta_angle = 0

        self.set_value(value)

        self.under_mouse = False
        self.press = False
        self.update([0,0],True)

    def get_angle(self):
        return self.range_angle[0]+self.value*(self.range_angle[1]-self.range_angle[0])

    def repaint(self,index_gtc,image):
        self.theme_index = index_gtc

        self.button_image = image
        self.draw_image = self.button_image.image
        self.draw_image = self.button_image.rotate(self.angle)

        self.image_pr = Image(pygame.Surface((5000, 40)))
        self.image_pr.image.fill(gtc(self.theme_index)[1])
        for i in range(self.range_value[0] - 8, self.range_value[1] + 6):
            txt = self.font.render(str(i), False, gtc(self.theme_index)[4])
            x = (i - self.range_value[0] + 8) / 5 * 150
            if i % 5 == 0:
                self.image_pr.image.blit(txt, txt.get_rect(center=(x, 20)))
            else:
                pygame.draw.rect(self.image_pr.image, gtc(self.theme_index)[0], (x - 2, 10, 4, 20), 0, 5)
        self.draw_image_pr = self.image_pr.clamp(300, 50, 0, -5, gtc(self.theme_index)[2])
        self.update([0,0],True)

    def set_value(self,new_value):
        self.value = new_value
        self.angle = new_value*(-31.40947)-1.58153
        #print(self.angle,';',self.get_value(),';',new_value)

    def get_offset(self):
        return (self.angle)/math.pi*180

    def get_value(self):
        #print(self.value, ':', self.get_offset(), ':', self.angle)
        return self.value*(self.range_value[1]-self.range_value[0])+self.range_value[0]

    def set_offset(self,mp):
        self.offset_angle = -math.atan2(self.y-mp[1],self.x-mp[0])-self.angle

    def unpress(self):
        self.draw_image = self.button_image.rotate(self.angle)
        self.press = False

    def update(self,mp,prs=False):
        if self.press or prs:
            if self.press:
                dangle = (-math.atan2(self.y-mp[1],self.x-mp[0])-self.offset_angle)-self.angle

                if abs(self.last_delta_angle-dangle) > math.pi/2*3 and dangle != 0:
                    #print("!!!",self.last_delta_angle,dangle)
                    dangle += -(dangle/abs(dangle))*math.pi*2
                    self.set_offset(mp)

                self.angle += dangle
                self.last_delta_angle = dangle
                if -(self.get_offset()+90)/1800>=0 and -(self.get_offset()+90)/1800<=1:
                    pass
                else:
                    self.angle -= dangle
                self.draw_image = pygame.transform.rotate((self.button_image.re_size_k(0.95)),self.angle/math.pi*180)
            else:
                self.draw_image = self.button_image.rotate(self.angle)


            self.draw_image_pr = self.image_pr.clamp(300,50,self.get_offset(),5,gtc(self.theme_index)[2])
            self.value = -(self.get_offset()+90)/1800
        else:
            if get_distance(mp,(self.x,self.y)) <= min(self.button_image.W(),self.button_image.H())/2:
                self.under_mouse = True
            else:
                self.under_mouse = False

    def draw(self,surface):
        surface.blit(self.draw_image,self.draw_image.get_rect(center=(self.x,self.y)))

        surface.blit(self.draw_image_pr,self.draw_image_pr.get_rect(center=(self.x,self.y-115)))

        pygame.draw.polygon(surface,gtc(self.theme_index)[3],([self.x,self.y-135],[self.x-12,self.y-155],[self.x+12,self.y-155]),6)
        # pygame.draw.polygon(surface,gtc(self.theme_index)[1],([self.x,self.y-141],[self.x-8,self.y-151],[self.x+8,self.y-151]))

class SimpleButton:
    def __init__(self,rect,image:Image,func,params = None):
        self.x,self.y,self.w,self.h = rect
        self.image = Image(image.re_size(self.w,self.h))
        self.xw = self.x+self.w
        self.yh = self.y+self.h

        self.under_mouse = False
        self.clickable_func = func
        self.params = params

    def update(self,mp):
        if (mp[0] > self.x and mp[0] <self.xw
                and mp[1] >= self.y and mp[1] <= self.yh):
            self.under_mouse = True
        else:
            self.under_mouse = False

    def draw(self,surface:pygame.Surface):
        surface.blit(self.image.image,(self.x,self.y))


class Application():
    def __init__(self,W,H,FPS,v,f,rf,marks,theme_index):
        self.win = pygame.display.set_mode((W,H))
        self.clock = pygame.time.Clock()

        self.k_volume = 0.3             #ratio volume (0-mute,1-full)
        self.radio = FM(v*self.k_volume,f,marks)
        self.FPS = FPS
        self.W,self.H = W,H
        self.theme_index = theme_index

        self.main_surf = pygame.Surface((W,H))
        self.main_win_anim = Animation(False,0.85,1,0.2,FPS,sqrt,self.clock)

        self.settings_panel = pygame.Surface((W,H),pygame.SRCALPHA)
        self.settings_panel_anim = Animation(True,0,1,0.25,60,easeInOutBack,self.clock)
        self.settings_panel_sbuttons = []
        self.is_open_settings_panel = False

        self.font = pygame.font.SysFont('comicsans', 24,True)
        self.text = self.font.render("SoundCloud FM",False,(255,255,255))

        self.icon = Image(pygame.image.load('assets/images/icon.png'))
        self.draw_icon = self.icon.fill_bg(gtc(self.theme_index)[0]).re_size(160,160)
        pygame.display.set_icon(self.icon.fill_bg((0,0,10)).image)
        pygame.display.set_caption("SoundCloud FM")

        self.image_button = Image(Image(pygame.image.load('assets/images/button.png')).re_size(150,150))
        self.button_frequency = RotateButton((W//2,H//2+70),self.image_button.fill_bg(gtc(self.theme_index)[0]),(0,math.pi*6),f,rf,self.theme_index)
        self.rotate_buttons = [self.button_frequency]

        self.image_volume = Image(pygame.image.load('assets/images/volume.png'))
        self.image_volume_mute = Image(pygame.image.load('assets/images/volume_mute.png'))
        image_volume_draw = self.image_volume.fill_bg(gtc(self.theme_index)[0])
        image_volume_mute_draw = self.image_volume_mute.fill_bg(gtc(self.theme_index)[0])
        self.slider_volume = Slider((W//2-150,H//2+190,300,12),gtc(self.theme_index)[1],(0,100),v/100,'',13,image_volume_draw,image_volume_mute_draw)
        self.sliders = [self.slider_volume]

        self.button_settings = SimpleButton([self.W-50,10,40,40],Image(pygame.image.load('assets/images/button_settings.png')),self.open_settings_panel,True)
        self.simple_buttons = [self.button_settings]

        self.radio.set_frequency(self.button_frequency.get_value())

        self.animations = [self.main_win_anim,self.settings_panel_anim]

        self.change_theme(self.theme_index)

    def save(self):
        with open('assets/data.txt',mode='w',encoding='utf-8') as file:
            file.write(str(round(self.slider_volume.get_value()))+'\n')
            file.write(str(self.button_frequency.get_value())+'\n')
            file.write(str(self.theme_index))
        #print(self.button_frequency.get_value())

    def open_settings_panel(self,state):
        self.is_open_settings_panel = state

        if state:
            self.settings_panel_anim.update_state(1)
            self.main_win_anim.update_state(-1)
        else:
            self.settings_panel_anim.update_state(-1)
            self.main_win_anim.update_state(1)

    def change_theme(self,i):
        if i != self.theme_index or len(self.settings_panel_sbuttons) ==0:
            self.theme_index = i

            self.draw_icon = self.icon.fill_bg(gtc(self.theme_index)[0]).re_size(160,160)

            image_volume_draw = self.image_volume.fill_bg(gtc(self.theme_index)[0])
            image_volume_mute_draw = self.image_volume_mute.fill_bg(gtc(self.theme_index)[0])

            for slider in self.sliders:
                slider.repaint(self.theme_index,image_volume_draw,image_volume_mute_draw)
            for rbuttons in self.rotate_buttons:
                rbuttons.repaint(self.theme_index,self.image_button.fill_bg(gtc(self.theme_index)[0]))

            self.settings_panel_sbuttons = []
            for i in range(len(THEME_COLORS)):
                theme = gtc(i)
                image = pygame.Surface((48, 48), pygame.SRCALPHA)

                image1 = pygame.Surface((48, 48), pygame.SRCALPHA)
                image2 = pygame.Surface((48, 48), pygame.SRCALPHA)
                color = (25, 170, 10) if i == self.theme_index else (128, 22, 12)
                pygame.draw.circle(image, color, (24, 24), 24)

                # draw first half circle
                pygame.draw.circle(image1, theme[0], (24, 24), 20)
                pygame.draw.polygon(image1, (0, 0, 0, 0), ([0, 0], [48, 48], [48, 0]))

                # draw second half circle
                pygame.draw.circle(image2, theme[1], (24, 24), 20)
                pygame.draw.polygon(image2, (0, 0, 0, 0), ([0, 0], [48, 48], [0, 48]))

                image.blit(image1, (0, 0))
                image.blit(image2, (0, 0))

                self.settings_panel_sbuttons.append(SimpleButton((80+(self.W//2-80-24)*(i//2), 100 + 55 * (i%2), 48, 48), Image(image), self.change_theme, i))

    def draw(self):
        self.win.fill(gtc(self.theme_index)[0])
        self.main_surf.fill(gtc(self.theme_index)[0])
        #self.pos_back = [(self.pos_back[0]+self.slider_volume.get_value())%-self.imgsize[0],(self.pos_back[1]+self.slider_volume.get_value())%-self.imgsize[1]]
        #self.win.blit(self.back_surf,self.pos_back)

        for rbutton in self.rotate_buttons:
            rbutton.draw(self.main_surf)

        self.main_surf.blit(self.draw_icon,self.draw_icon.get_rect(center=(self.W//2,68)))
        self.main_surf.blit(self.text,self.text.get_rect(center=(self.W//2,118)))
        for slider in self.sliders:
            slider.draw(self.main_surf)

        for sbutton in self.simple_buttons:
             sbutton.draw(self.main_surf)

        if self.main_win_anim() != 1 or self.settings_panel_anim() != 0:
            k = self.main_win_anim()
            draw_surf = pygame.transform.scale(self.main_surf,(self.W*k,self.H*k))
            self.win.blit(draw_surf,draw_surf.get_rect(center=(self.W//2,self.H//2)))

            self.settings_panel.fill((0,0,0,0))
            pygame.draw.rect(self.settings_panel, (255, 255, 255, 120), (30, 50, self.W - 60, self.H - 100), 0, 10)
            for sbutton in self.settings_panel_sbuttons:
                sbutton.draw(self.settings_panel)
            k = max(self.settings_panel_anim(),0)
            draw_panel = pygame.transform.scale(self.settings_panel,(self.W*k,self.H*k))

            self.win.blit(draw_panel,draw_panel.get_rect(center=(self.W//2,self.H//2)))
        else:
            self.win.blit(self.main_surf,(0,0))

        pygame.display.update()

    def update(self):
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        find = False
                        if self.is_open_settings_panel:
                            for i in range(len(self.settings_panel_sbuttons)):
                                if self.settings_panel_sbuttons[i].under_mouse:
                                    self.settings_panel_sbuttons[i].clickable_func(self.settings_panel_sbuttons[i].params)
                                    find = True
                                    break
                            if not find:
                                self.open_settings_panel(False)

                        else:
                            for i in range(len(self.sliders)):
                                if self.sliders[i].under_mouse:
                                    self.sliders[i].press = True
                                    find = True
                                    break

                            if not find:
                                for i in range(len(self.rotate_buttons)):
                                    if self.rotate_buttons[i].under_mouse:
                                        self.rotate_buttons[i].press = True
                                        self.rotate_buttons[i].set_offset(pygame.mouse.get_pos())
                                        find = True
                                        break

                                if not find:
                                    for i in range(len(self.simple_buttons)):
                                        if self.simple_buttons[i].under_mouse:
                                            self.simple_buttons[i].clickable_func(self.simple_buttons[i].params)
                                            break


                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        find = False
                        for i in range(len(self.sliders)):
                            if self.sliders[i].press:
                                self.sliders[i].press = False
                                find = True
                                break

                        if not find:
                            for i in range(len(self.rotate_buttons)):
                                if self.rotate_buttons[i].press:
                                    self.rotate_buttons[i].unpress()
                                    #print(self.rotate_buttons[i].get_value())
                                    break

            mouse_pos = pygame.mouse.get_pos()
            for slider in self.sliders:
                slider.update(mouse_pos)
            for rbutton in self.rotate_buttons:
                rbutton.update(mouse_pos)
            for sbutton in self.simple_buttons:
                sbutton.update(mouse_pos)

            for anim in self.animations:
                anim.update()

            if self.is_open_settings_panel:
                for sbutton in self.settings_panel_sbuttons:
                    sbutton.update(mouse_pos)

            if self.slider_volume.press: self.radio.set_volume(round(self.slider_volume.get_value()*self.k_volume))
            if self.button_frequency.press: self.radio.set_frequency(round(self.button_frequency.get_value(),5))

            self.radio.update()
            self.draw()
            self.clock.tick(self.FPS)
            #pygame.display.set_caption(str(int(self.clock.get_fps())))

        self.save()

def main():
    W, H = 380, 500
    FPS = 60
    START_VOLUME, START_FREQUENCY,THEME_INDEX = load()
    RANGE_FREQUENCY = (70, 130)

    path_music = 'assets/musics/'
    dirs = [d for d in listdir(path_music) if isdir(f'{path_music}{d}')]

    MARKS = []
    for dir_ in dirs:
        dir_ = path_music+dir_
        files = listdir(dir_)
        if 'config.txt' in files:
            with open(f'{dir_}/config.txt', mode='r',encoding='utf-8') as cnfg:

                frequency = float(cnfg.readline())
                strength = float(cnfg.readline())
                musics = [f'{dir_}/{file}' for file in files[:] if file[-4:] == '.mp3']

                MARKS.append(Mark(musics,frequency,strength))
        else:
            continue

    app = Application(W, H, FPS, START_VOLUME,
                      (START_FREQUENCY - RANGE_FREQUENCY[0]) / (RANGE_FREQUENCY[1] - RANGE_FREQUENCY[0]),
                      RANGE_FREQUENCY, MARKS,THEME_INDEX)
    app.update()

    return

if __name__ == "__main__":
    main()