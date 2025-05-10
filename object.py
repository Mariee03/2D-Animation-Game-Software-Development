import pygame, game

class Animation():
    def __init__(self, animation_file):
        with open(animation_file) as file:
            data = file.read()

        # remove comments and extra lines
        clean_data = ''
        last_c = ''
        appending = True
        for c in data:
            if c == '/' and last_c == '/':
                clean_data = clean_data[0:len(clean_data)-1]
                appending=False
            if last_c == '\n':
                if c=='\n':
                    clean_data = clean_data[0:len(clean_data)-1]
                appending = True
            if appending:
                clean_data = clean_data + c

            last_c = c
        
        # get path to sprite sheet
        path = clean_data.split('\n')[0]
        # get divions in sprite sheet
        divisions = [int(clean_data.split('\n')[1].split(',')[0]),int(clean_data.split('\n')[1].split(',')[1])]
        # get framerate
        rate = int(clean_data.split('\n')[2])
        # get frames
        frames = []
        for c in clean_data.split('\n')[3].split(','):
            frames.append(int(c))
        
        self.sheet = pygame.image.load(path)
        self.rate = rate
        self.frames = frames
        self.divisions = divisions
        self.current_frame = 0
        self.anim_end = False
        self.image = self.sheet.subsurface(pygame.Rect(
            self.divisions[0] * int(self.frames[int(self.current_frame)]%int(self.sheet.get_width()/self.divisions[0])), 
            self.divisions[1] * int(self.frames[int(self.current_frame)]/int(self.sheet.get_width()/self.divisions[0])), 
            self.divisions[0], self.divisions[1]))

    def update(self, game_rate):
        self.anim_end = False
        self.current_frame += self.rate/game_rate
        if self.current_frame >= len(self.frames): 
            self.current_frame = 0
            self.anim_end = True

        self.image = self.sheet.subsurface(pygame.Rect(
            self.divisions[0] * int(self.frames[int(self.current_frame)]%int(self.sheet.get_width()/self.divisions[0])), 
            self.divisions[1] * int(self.frames[int(self.current_frame)]/int(self.sheet.get_width()/self.divisions[0])), 
            self.divisions[0], self.divisions[1]))
    def reset(self):
        self.anim_end = False
        self.current_frame = 0

class Object(pygame.sprite.Sprite):
    def __init__(self, position, anims, scale=[1,1], flip_x=False, flip_y=False):
       pygame.sprite.Sprite.__init__(self)
       self.animations = []
       for anim in anims:
        if anim.split('.')[1] == 'ani':
            self.animations.append(Animation(anim))
       self.anim_state = 0
       self.flip_x, self.flip_y = flip_x, flip_y
       self.scale = scale
       self.surface = self.animations[self.anim_state].image if len(self.animations) > 0 else pygame.image.load(anims[0])
       self.image = pygame.transform.flip(pygame.transform.scale(self.surface, (self.surface.get_width() * abs(self.scale[0]), self.surface.get_height() * abs(self.scale[1]))), flip_x, flip_y)
       self.x = position[0]
       self.y = position[1]

       self.rect = self.image.get_rect()
       
    def update(self, screen):
        if len(self.animations) > 0:
            self.animations[self.anim_state].update(game.FRAMERATE)
            self.surface = self.animations[self.anim_state].image
        self.image = pygame.transform.flip(pygame.transform.scale(self.surface, (int(self.surface.get_width() * self.scale[0] * (screen.get_width()/game.SCREEN_WIDTH)), int(self.surface.get_height() * self.scale[1]) * (screen.get_height()/game.SCREEN_HEIGHT))), self.flip_x, self.flip_y)
        self.rect = self.image.get_rect()
        self.rect.x = int(game.MEASUREMENT_UNIT[0] / (game.SCREEN_WIDTH / screen.get_width())) * self.x
        self.rect.y = screen.get_height() - self.rect.height if self.y == None else int(game.MEASUREMENT_UNIT[1] / (game.SCREEN_HEIGHT/screen.get_height())) * self.y
class Entity(Object):
    def __init__(self, position, health, hit, speed, rest, range, anims, scale=[1,1], flip_x=False, flip_y=False):
        Object.__init__(self, [position, None], anims, scale=scale, flip_x=flip_x, flip_y=flip_y)
        self.health = health
        self.hit = hit
        self.rest = rest
        self.speed = speed
        self.range = range
class Worker(Entity):
    def __init__(self, player):
        Entity.__init__(self, (game.FIELD_SIZE-2)*player, 1, 0, game.WORKER_SPEED-(player*game.WORKER_SPEED*2), 1, 0, ['assets/worker-idle.ani','assets/worker-run.ani'], scale=[2,2], flip_x=player)
class Swordsman(Entity):
    def __init__(self, player):
        Entity.__init__(self, (game.FIELD_SIZE-2)*player, game.SWORD_HEALTH, game.SWORD_HIT, game.SWORD_SPEED-(player*game.SWORD_SPEED*2), game.SWORD_REST, game.SWORD_RANGE, ['assets/sword-idle.ani','assets/sword-run.ani', 'assets/sword-attack.ani'], scale=[2,2], flip_x=player)
class Archer(Entity):
    def __init__(self, player):
        Entity.__init__(self, (game.FIELD_SIZE-2)*player, game.ARCHER_HEALTH, game.ARCHER_HIT, game.ARCHER_SPEED-(player*game.ARCHER_SPEED*2), game.ARCHER_REST, game.ARCHER_RANGE, ['assets/archer-idle.ani','assets/archer-run.ani','assets/archer-attack.ani'], scale=[2,2], flip_x=player)
class Tower(Entity):
    def __init__(self, player):
        Entity.__init__(self, game.TOWER_POS+(game.FIELD_SIZE-2-game.TOWER_POS*2)*player, game.WALL_HEALTH, game.TOWER_HIT, 0, game.TOWER_REST, game.TOWER_RANGE, ['assets/tower-idle.ani','assets/tower-shoot.ani'], scale=[2,2], flip_x=player)
