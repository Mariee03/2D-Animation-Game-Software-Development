#!/usr/bin/env python3
import pygame, sys, math
from pygame.locals import *

pygame.init()
pygame.font.init()

# global constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FRAMERATE = 60
MEASUREMENT_UNIT = [36, 36] # pixels
FONT = pygame.font.Font('assets/font.ttf', int((MEASUREMENT_UNIT[0]+MEASUREMENT_UNIT[1])/2))
FIELD_SIZE = 36
INIT_RESOURCES = 100

WALL_POS       = 6
WALL_HEALTH    = 100

MINE_POS       = 3

BARRACKS_POS   = 0

TOWER_POS      = 6
TOWER_RANGE    = 8
TOWER_HIT      = 3
TOWER_REST     = 0

# unit constants
WORKER_COST   = 100
WORKER_TRAIN  = 3
WORKER_PROD   = 5
WORKER_SPEED  = 3
WORKER_REPAIR = 1

SWORD_COST    = 75
SWORD_TRAIN   = 3
SWORD_SPEED   = 1
SWORD_RANGE   = 1
SWORD_HIT     = 3
SWORD_REST    = 0
SWORD_HEALTH  = 10

ARCHER_COST   = 100
ARCHER_TRAIN  = 3
ARCHER_SPEED  = 2
ARCHER_RANGE  = 8
ARCHER_HIT    = 3
ARCHER_REST   = 0
ARCHER_HEALTH = 5

# game vars
game_time = 0 # turns
turn = 0 # current player turn
BACKDROP = pygame.image.load('assets/backdrop.png')


                   
def main():
    import object
    global FONT, turn, game_time

    # runtime vars
    pygame.display.set_caption("Castles War")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    adjusted_unit = [int(MEASUREMENT_UNIT[0] / (SCREEN_WIDTH / screen.get_width())), # unit of measurement adjusted to window size
    int(MEASUREMENT_UNIT[1] / (SCREEN_HEIGHT / screen.get_height()))] 
    gameover = False
    running = True

    sprites = pygame.sprite.Group()
    wall_1 = object.Tower(0)
    mine_1 = object.Object([MINE_POS, None], ['assets/mine.gif',],scale=[2,2])
    barracks_1 = object.Object([BARRACKS_POS, None], ['assets/barracks.gif',], scale=[2,2])
    wall_2 = object.Tower(1)
    mine_2 = object.Object([FIELD_SIZE-2.5-MINE_POS, None], ['assets/mine.gif',],scale=[2,2], flip_x=True)
    barracks_2 = object.Object([FIELD_SIZE-2.5-BARRACKS_POS, None], ['assets/barracks.gif',], scale=[2,2], flip_x=True)

    worker_portrait_1 = object.Object([2, 0.7], ['assets/worker-portrait.gif'])
    sword_portrait_1 = object.Object([4, 0.7], ['assets/sword-portrait.gif'])
    archer_portrait_1 = object.Object([6, 0.7], ['assets/archer-portrait.gif'])
    worker_portrait_2 = object.Object([32.5, 0.7], ['assets/worker-portrait.gif'])
    sword_portrait_2 = object.Object([30.5, 0.7], ['assets/sword-portrait.gif'])
    archer_portrait_2 = object.Object([28.5, 0.7], ['assets/archer-portrait.gif'])


    sprites.add(wall_1, mine_1, barracks_1, wall_2, mine_2, barracks_2, worker_portrait_1, sword_portrait_1, archer_portrait_1, worker_portrait_2, sword_portrait_2, archer_portrait_2)

    player_data = {
    # player 1 data
        0: {
            "resource":0,
            "queue":[],
            "barracks":[[False,object.Worker(0)]],
            "mine":0, # number of workers in mine
            "wall":0, # number of workers at wall
        },
        # player 2 data
        1: {
            "resource":0,
            "queue":[],
            "barracks":[[False,object.Worker(1)]],
            "mine":0, # number of workers in mine
            "wall":0, # number of workers at wall
        }
    }
    def animation_phase():
        _entities = {}
        for sprite in sprites.sprites():
            if type(sprite) in (object.Archer, object.Swordsman, object.Tower):
                sprite.rest += 1
                _entities[round(sprite.x)] = sprite

        # attack
        for unit in _entities.values():
            if unit.flip_x == False:
                _spotted = False
                for i in range(unit.range):
                    try:
                        if _entities[round(unit.x+i+1)].flip_x:
                            _spotted = True
                    except:
                        pass
                    if _spotted:     
                        if type(unit) == object.Archer:
                            unit.anim_state = 2
                            _arrow = object.Object([unit.x+1, int(screen.get_height()/adjusted_unit[1]-1)], ['assets/arrow.gif',], scale=[2,2])
                            sprites.add(_arrow)
                            while _arrow.x < unit.x+i+1:
                                _arrow.x += 15/FRAMERATE
                                update_screen()
                                clock.tick(FRAMERATE)
                            sprites.remove(_arrow)
                            unit.animations[2].reset()
                        if type(unit) == object.Swordsman:
                            unit.anim_state = 2
                            while unit.animations[unit.anim_state].anim_end == False:
                                update_screen()
                                clock.tick(FRAMERATE)
                            unit.animations[2].reset()
                        if type(unit) == object.Tower:
                            unit.anim_state = 1
                            _arrow = object.Object([unit.x, int(screen.get_height()/adjusted_unit[1]-5)], ['assets/arrow.gif',], scale=[2,2])
                            sprites.add(_arrow)
                            while _arrow.x < unit.x+i+1 or _arrow.y < int(screen.get_height()/adjusted_unit[1]-1):
                                _arrow.x += 15/FRAMERATE
                                _arrow.y += 4/((i+1)/(15/FRAMERATE))
                                update_screen()
                                clock.tick(FRAMERATE)
                            sprites.remove(_arrow)
                            unit.animations[1].reset()
                        unit.anim_state=0
                        _entities[round(unit.x+i+1)].health -= sprite.hit
                        if _entities[round(unit.x+i+1)].health <= 0: sprites.remove(_entities[round(unit.x+i+1)])
                        unit.rest = -1
                        break
                         
        # player 1
        previous = {}
        unit_move = {}
        for sprite in sprites.sprites():
            if type(sprite) in (object.Archer, object.Swordsman) and sprite.flip_x==False:
                    previous[sprite] = sprite.x
                    unit_move[sprite] = 0
                    if sprite.rest >= {object.Archer: ARCHER_REST, object.Swordsman: SWORD_REST}[type(sprite)]:
                        for i in range(sprite.speed):
                            if len([j for j in unit_move.keys() if round(j.x + unit_move[j]) == round(sprite.x)+i+1])==0:
                                unit_move[sprite] += 1
                            else: 
                                break
        while len(previous) > 0:
            finished = []
            for sprite in previous.keys():
                sprite.anim_state = 1
                if sprite.x >= previous[sprite] + unit_move[sprite]:
                    finished.append(sprite)
                    break
                sprite.x += unit_move[sprite]/FRAMERATE
            for sprite in reversed(finished):
                sprite.anim_state = 0
                previous.pop(sprite)
                finished.remove(sprite)
            clock.tick(FRAMERATE)
            update_screen()

        _entities = {}
        for sprite in sprites.sprites():
            if type(sprite) in (object.Archer, object.Swordsman, object.Tower):
                _entities[round(sprite.x)] = sprite
        
        # attack
        for unit in _entities.values():
            if unit.flip_x:
                _spotted = False
                for i in range(unit.range):
                    try:
                        if _entities[round(unit.x-i-1)].flip_x == False:
                            _spotted = True
                    except:
                        pass
                    if _spotted:
                        if type(unit) == object.Archer:
                            unit.anim_state = 2
                            _arrow = object.Object([unit.x-1, int(screen.get_height()/adjusted_unit[1]-1)], ['assets/arrow.gif',], scale=[2,2], flip_x=True)
                            sprites.add(_arrow)
                            while _arrow.x > unit.x-i and unit.animations[unit.anim_state].anim_end == False:
                                _arrow.x -= 15/FRAMERATE
                                update_screen()
                                clock.tick(FRAMERATE)
                            sprites.remove(_arrow)
                            unit.animations[2].reset()
                        if type(unit) == object.Swordsman:
                            unit.anim_state = 2
                            while unit.animations[unit.anim_state].anim_end == False:
                                update_screen()
                                clock.tick(FRAMERATE)
                            unit.animations[2].reset()
                        if type(unit) == object.Tower:
                            unit.anim_state = 1
                            _arrow = object.Object([unit.x, int(screen.get_height()/adjusted_unit[1]-5)], ['assets/arrow.gif',], scale=[2,2], flip_x=True)
                            sprites.add(_arrow)
                            while _arrow.x > unit.x-i or _arrow.y < int(screen.get_height()/adjusted_unit[1]-1):
                                _arrow.x -= 15/FRAMERATE
                                _arrow.y += 4/((i+int(not(i)))/(15/FRAMERATE))
                                update_screen()
                                clock.tick(FRAMERATE)
                            sprites.remove(_arrow)
                            unit.animations[1].reset()
                        unit.anim_state = 0
                        _entities[round(unit.x-i-1)].health -= sprite.hit
                        if _entities[round(unit.x-i-1)].health <= 0: sprites.remove(_entities[round(unit.x-i-1)])
                        unit.rest = -1
                        break

        # player 2
        previous = {}
        unit_move = {}
        for sprite in sprites.sprites():
            if type(sprite) in (object.Archer, object.Swordsman) and sprite.flip_x:
                previous[sprite] = sprite.x
                unit_move[sprite] = 0
                if sprite.rest >= {object.Archer: ARCHER_REST, object.Swordsman: SWORD_REST}[type(sprite)]:
                    for i in range(abs(sprite.speed)):
                        if len([j for j in unit_move.keys() if round(j.x - unit_move[j]) == round(sprite.x)-i-1])==0:
                            unit_move[sprite] += 1
                        else: 
                            break
        while len(previous) > 0:
            finished = []
            for sprite in previous.keys():
                sprite.anim_state = 1
                if sprite.x <= previous[sprite] - unit_move[sprite]:
                    finished.append(sprite)
                    break
                sprite.x -= unit_move[sprite]/FRAMERATE
            for sprite in finished:
                sprite.anim_state = 0
                previous.pop(sprite)
                finished.remove(sprite)
            clock.tick(FRAMERATE)
            update_screen()
    def update_screen():
        screen.blit(pygame.transform.scale(BACKDROP, (screen.get_width(), screen.get_height())), (0, 0)) # reset screen

        # ui
        _turn_text = FONT.render(f"Player {turn+1}'s Turn", False, (0, 0, 0))
        _resource_text_1 = FONT.render(f"{player_data[0]['resource']}", False, (0, 255, 0))
        _resource_text_2 = FONT.render(f"{player_data[1]['resource']}", False, (0, 255, 0))
        _health_text_1 = FONT.render(f"{wall_1.health}", False, (255, 0, 0))
        _health_text_2 = FONT.render(f"{wall_2.health}", False, (255, 0, 0))
        _workers_1 = FONT.render(str(len([unit for unit in player_data[0]['barracks'] if type(unit[1]) == object.Worker])), False, (0,0,0))
        _workers_2 = FONT.render(str(len([unit for unit in player_data[1]['barracks'] if type(unit[1]) == object.Worker])), False, (0,0,0))
        _swords_1 = FONT.render(str(len([unit for unit in player_data[0]['barracks'] if type(unit[1]) == object.Swordsman])), False, (0,0,0))
        _swords_2 = FONT.render(str(len([unit for unit in player_data[1]['barracks'] if type(unit[1]) == object.Swordsman])), False, (0,0,0))
        _archers_1 = FONT.render(str(len([unit for unit in player_data[0]['barracks'] if type(unit[1]) == object.Archer])), False, (0,0,0))
        _archers_2 = FONT.render(str(len([unit for unit in player_data[1]['barracks'] if type(unit[1]) == object.Archer])), False, (0,0,0))
        _worker_cost_text = FONT.render(str(WORKER_COST), False, (0, 255, 0))
        _sword_cost_text = FONT.render(str(SWORD_COST), False, (0, 255, 0))
        _archer_cost_text = FONT.render(str(ARCHER_COST), False, (0, 255, 0))
        _mine_1_text = FONT.render(f"+{player_data[0]['mine']*WORKER_PROD}", False, (0, 255, 0))
        _mine_2_text = FONT.render(f"+{player_data[1]['mine']*WORKER_PROD}", False, (0, 255, 0))
        _wall_1_text = FONT.render(f"+{player_data[0]['wall']*WORKER_REPAIR}", False, (255, 0, 0))
        _wall_2_text = FONT.render(f"+{player_data[1]['wall']*WORKER_REPAIR}", False, (255, 0, 0))

        screen.blit(_turn_text, (screen.get_width()/2 - _turn_text.get_width()/2, adjusted_unit[1]/2))  
        screen.blit(_resource_text_1, (adjusted_unit[0]/2, adjusted_unit[1]/2))
        screen.blit(_resource_text_2, (screen.get_width() - adjusted_unit[0]*1.5, adjusted_unit[1]/2))
        screen.blit(_health_text_1, (WALL_POS * adjusted_unit[0], screen.get_height() - 7 * adjusted_unit[1]))
        screen.blit(_health_text_2, (screen.get_width() - (WALL_POS+1.5) * adjusted_unit[0], screen.get_height() - 7 * adjusted_unit[1]))
        screen.blit(_workers_1, (adjusted_unit[0]*2, adjusted_unit[1] * 1.5))
        screen.blit(_workers_2, (screen.get_width() - adjusted_unit[0]*2 - _workers_2.get_width(), adjusted_unit[1] * 1.5))
        screen.blit(_swords_1, (adjusted_unit[0]*4, adjusted_unit[1] * 1.5))
        screen.blit(_swords_2, (screen.get_width() - adjusted_unit[0]*4 - _swords_2.get_width(), adjusted_unit[1] * 1.5))
        screen.blit(_archers_1, (adjusted_unit[0]*6, adjusted_unit[1] * 1.5))
        screen.blit(_archers_2, (screen.get_width() - adjusted_unit[0]*6 - _archers_2.get_width(), adjusted_unit[1] * 1.5))

        screen.blit(_worker_cost_text, (adjusted_unit[0]*2, -10))
        screen.blit(_sword_cost_text, (adjusted_unit[0]*4, -10))
        screen.blit(_archer_cost_text, (adjusted_unit[0]*6, -10))
        screen.blit(_worker_cost_text, (screen.get_width() - adjusted_unit[0]*2 - _worker_cost_text.get_width(), -10))
        screen.blit(_sword_cost_text, (screen.get_width() - adjusted_unit[0]*4 - _sword_cost_text.get_width(), -10))
        screen.blit(_archer_cost_text, (screen.get_width() - adjusted_unit[0]*6 - _archer_cost_text.get_width(), -10))

        screen.blit(_mine_1_text, (MINE_POS * adjusted_unit[0], screen.get_height() - adjusted_unit[1] * 3))
        screen.blit(_mine_2_text, (screen.get_width() - ((MINE_POS+2) * adjusted_unit[0]), screen.get_height() - adjusted_unit[1] * 3))

        screen.blit(_wall_1_text, (WALL_POS * adjusted_unit[0], screen.get_height() - adjusted_unit[1] * 6))
        screen.blit(_wall_2_text, (screen.get_width() - ((WALL_POS+1.5) * adjusted_unit[0]), screen.get_height() - adjusted_unit[1] * 6))

        sprites.update(screen)
        sprites.draw(screen)

        if gameover:
            _winner = FONT.render(f"Player {1 if wall_2.health<=0 else 2} Wins", False, (255, 255, 0))
            _winner = pygame.transform.scale(_winner, (_winner.get_width()*2, _winner.get_height()*2))
            screen.blit(_winner, (screen.get_width()/2 - _winner.get_width()/2, screen.get_height()/2 - _winner.get_height()/2))

        pygame.display.update()  

    update_screen()
    # game loop
    while running:
        # get events
        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()
            # window size change
            if event.type == pygame.VIDEORESIZE:
                adjusted_unit[0] = int(MEASUREMENT_UNIT[0] / (SCREEN_WIDTH / screen.get_width()))
                adjusted_unit[1] = int(MEASUREMENT_UNIT[1] / (SCREEN_HEIGHT / screen.get_height()))
                FONT = pygame.font.Font('assets/font.ttf', int((adjusted_unit[0]+adjusted_unit[1])/2))
                update_screen()
                pygame.display.update()
        if gameover: continue
        keys = pygame.key.get_pressed()
        if True in keys:
            # commands
            if keys[(K_q, K_p)[turn]]: # train worker
                if player_data[turn]['resource'] >= WORKER_COST:
                    player_data[turn]['resource'] -= WORKER_COST
                    player_data[turn]['queue'].append([WORKER_TRAIN+1,object.Worker(turn)])
                else:
                    continue
            elif keys[(K_w, K_o)[turn]]: # train swordsman
                if player_data[turn]['resource'] >= SWORD_COST:
                    player_data[turn]['resource'] -= SWORD_COST
                    player_data[turn]['queue'].append([SWORD_TRAIN+1,object.Swordsman(turn)])
                else:
                    continue
            elif keys[(K_e, K_i)[turn]]: # train archer
                if player_data[turn]['resource'] >= ARCHER_COST:
                    player_data[turn]['resource'] -= ARCHER_COST
                    player_data[turn]['queue'].append([ARCHER_TRAIN+1,object.Archer(turn)])
                else:
                    continue
            elif keys[(K_a, K_l)[turn]]: # deploy worker to mine
                _found = False
                for unit in player_data[turn]['barracks']:
                    if type(unit[1]) == type(object.Worker(turn)):
                        player_data[turn]['barracks'].remove(unit)
                        _found = True
                        break
                if _found == False: continue
                _worker = object.Worker(turn)
                sprites.add(_worker)
                # animation
                while (_worker.x-(_worker.x*2)*turn <= MINE_POS-(FIELD_SIZE-2)*turn):
                    _worker.anim_state = 1
                    _worker.x += (_worker.speed/FRAMERATE)
                    update_screen()
                    clock.tick(FRAMERATE)
                sprites.remove(_worker)
                player_data[turn]['mine']+=1
            elif keys[(K_s, K_k)[turn]]: # deploy worker to wall
                _found = False
                for unit in player_data[turn]['barracks']:
                    if type(unit[1]) == object.Worker:
                        player_data[turn]['barracks'].remove(unit)
                        _found = True
                        break
                if _found == False: continue
                _worker = object.Worker(turn)
                sprites.add(_worker)
                # animation
                while (_worker.x-(_worker.x*2)*turn <= WALL_POS-(FIELD_SIZE-2)*turn):
                    _worker.anim_state = 1
                    _worker.x += (_worker.speed/FRAMERATE)
                    update_screen()
                    clock.tick(FRAMERATE)
                sprites.remove(_worker)
                player_data[turn]['wall']+=1
            elif keys[(K_z, K_m)[turn]]: # deploy units to field
                if len(player_data[turn]['barracks'])<1:continue
                for unit in player_data[turn]['barracks']:
                    if type(unit[1]) != type(object.Worker(turn)):
                        unit[0] = True
            elif keys[(K_LSHIFT, K_RSHIFT)[turn]]: # skip 
                pass
            else:
                continue
            for i in (0,1):
                for unit in player_data[i]['queue']:
                    unit[0]-=1
                    if unit[0] <= 0:
                        player_data[i]['barracks'].append([False, unit[1]])
                        player_data[i]['queue'].remove(unit)
                for unit in player_data[i]['barracks']:
                    _occupied = False
                    for sprite in sprites.sprites():
                        if round(sprite.x) == (FIELD_SIZE-2)*i and type(sprite) != object.Object:          
                            _occupied = True
                            break
                    if unit[0] and _occupied == False:
                        sprites.add(unit[1])
                        player_data[i]['barracks'].remove(unit)
                        break
            animation_phase()
            if wall_1.health <= 0 or wall_2.health <= 0:
                gameover = True
            turn = int(not turn) # change turn
            game_time+=1   
            update_screen()
            player_data[0]['resource'] += (player_data[0]['mine'] * WORKER_PROD)
            player_data[1]['resource'] += (player_data[1]['mine'] * WORKER_PROD)
            wall_1.health = min(WALL_HEALTH, wall_1.health + (player_data[0]['wall'] * WORKER_REPAIR))
            wall_2.health = min(WALL_HEALTH, wall_2.health + (player_data[1]['wall'] * WORKER_REPAIR))





if __name__ == '__main__':
    main()