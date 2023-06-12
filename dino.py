import sys
import random
from itertools import accumulate
from pathlib import Path

import pygame

class Settings:
    '''A class to store settings of dino game.'''
    def __init__(self):
        '''Initialize settings'''
        self.screen_width = 800
        self.screen_height = 450
        self.bg_color = (10, 10, 10)

        self.speedup_scale = 1.2
        self.milestones = (200, 500, 1000, 2000, 5000, 10000, 20000, 50000, float('inf'))
        self.reset_state()

    def reset_state(self):
        '''Set or reset settings to the original state.'''
        self.points = 0.35
        self.trex_jump_speed = 20
        self.cactus_speed = 18
        self.flying_lizard_speed = 20
        self.milestone_point = 0

    def increase_speed(self):
        '''Increase game speed and points gained when reaching a milestone point.'''
        self.cactus_speed = int(self.cactus_speed * self.speedup_scale)
        self.flying_lizard_speed = int(self.flying_lizard_speed * self.speedup_scale)
        self.points *= 2
        self.milestone_point += 1

    def get_font(self, fpath=None, size=12):
        '''Get pygame Font object with Press Start 2P as the default font.'''
        if not fpath:
            fpath = Path('font/Press_Start_2P/PressStart2P-Regular.ttf')
        return pygame.font.Font(fpath, size)

class DinoGame:
    '''Main class to represent dino game.'''
    def __init__(self):
        '''Initialize trex game.'''
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        self.screen_rect = self.screen.get_rect()
        pygame.display.set_caption('Dino Game')

        self.play_button = Button(self)

        self.trex = Trex(self)
        self.obstacles = self._create_obstacles()
        self.obstacle = self.obstacles[0]

        self.scoreboard = Scoreboard(self)

        self.background = Background(self)

        self.game_active = False

        # The below attribute is only used for testing.
        #self.pcollide = (0, 0)

    def run_game(self):
        '''Start running the game.'''
        while True:
            self._check_events()
            if self.game_active:
                self._update_background()
                self._update_obstacle()
                self._update_trex_jump()
                self.trex.duck_action()
                self._check_trex_obstacle_collide()
            self._update_screen()
            self.clock.tick(30)

    def _check_events(self):
        '''Check player's interaction.'''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_keydown_events(self, event):
        '''Responses to key down/pressed events.'''
        if event.key == pygame.K_ESCAPE:
            sys.exit()
            #self.game_active = False if self.game_active else True
        elif event.key == pygame.K_SPACE or event.key == pygame.K_UP:
            if not self.game_active:
                self._check_play_button()
            else:
                self.trex.jump = True
        elif event.key == pygame.K_DOWN:
            self.trex.duck = True

    def _check_keyup_events(self, event):
        '''Responses to key up/released events.'''
        if event.key == pygame.K_DOWN:
            self.trex.duck = False

    def _check_play_button(self):
        '''Set or reset the game to the original state when play or replay, and run the game.'''
        self.settings.reset_state()
        self.trex.reset_state()
        self.obstacles = self._create_obstacles()
        self.obstacle = self.obstacles[0]
        
        self.scoreboard.score = 0
        self.scoreboard.prepare_score()

        self.game_active = True

    def _create_obstacles(self):
        '''Create obstacles for the game.'''
        obstacle_types = []

        # Cactus version 1
        cactus_type = pygame.sprite.Group()
        cactus = Cactus(self)
        cactus_type.add(cactus)

        obstacle_types.append(cactus_type)

        # Cactus version 2
        cactus_type = pygame.sprite.Group()
        cactus = Cactus(self)
        cactus.rescale_flip_cactus(0.8)
        cactus_type.add(cactus)

        obstacle_types.append(cactus_type)

        # Cactus version 3
        cactus_type = pygame.sprite.Group()
        distance = 35
        for i in range(2):
            cactus = Cactus(self)
            cactus.rect.x += distance * i
            cactus_type.add(cactus)

        obstacle_types.append(cactus_type)

        # Cactus version 4
        cactus_type = pygame.sprite.Group()
        distance = 28
        flips = (False, True)
        for i, flip in enumerate(flips):
            cactus = Cactus(self)
            cactus.rescale_flip_cactus(0.8, flip)
            cactus.rect.x += distance * i
            cactus_type.add(cactus)

        obstacle_types.append(cactus_type)

        # Cactus version 5
        cactus_type = pygame.sprite.Group()
        distance = 28
        flips = (False, True, False)
        for i, flip in enumerate(flips):
            cactus = Cactus(self)
            cactus.rescale_flip_cactus(0.8, flip)
            cactus.rect.x += distance * i
            cactus_type.add(cactus)

        obstacle_types.append(cactus_type)

        # Cactus version 6
        cactus_type = pygame.sprite.Group()
        distances = (0, 37, 70, 75)
        scales = (1, 0.9, 0.6, 1)
        flips = (False, True, True, False)
        for scale, flip, distance in zip(scales, flips, distances):
            cactus = Cactus(self)
            cactus.rescale_flip_cactus(scale, flip)
            cactus.rect.x += distance
            cactus_type.add(cactus)

        obstacle_types.append(cactus_type)

        # Flying lizard version 1, 2 & 3
        heights = (0, 40, 80)
        for height in heights:
            flying_lizard_type = pygame.sprite.Group()
            flying_lizard = FlyingLizard(self)
            flying_lizard.rect.bottom += height
            flying_lizard_type.add(flying_lizard)

            obstacle_types.append(flying_lizard_type)

        return random.sample(obstacle_types, counts=(3, 3, 3, 3, 2, 1, 1, 1, 1), k=18)

    def _update_obstacle(self):
        '''Update obstacle and scoring.'''
        self.obstacle.update()
        sprites = self.obstacle.sprites()
        # If the obstacle goes pass the left of the screen,
        # reset its position to the right of the screen and choose the next obstacle.
        if sprites[-1].rect.right < self.screen_rect.left:
            move_distance = self.screen_rect.right - sprites[0].rect.left
            for sprite in sprites:
                sprite.rect.left += move_distance
            self.obstacle = random.choice(self.obstacles)

        # Update score, as well as check for new high score and milestone.
        self.scoreboard.score += self.settings.points
        self.scoreboard.prepare_score()
        self.scoreboard.check_high_score()
        self._check_milestone()

    def _check_milestone(self):
        '''Check if the score has reached a milestone, if so, increase the speed.'''
        if self.scoreboard.score >= self.settings.milestones[self.settings.milestone_point]:
            self.settings.increase_speed()
            #print('speed: ', self.settings.cactus_speed, self.settings.flying_lizard_speed)

    def _update_trex_jump(self):
        '''Process trex jump.'''
        if self.trex.jump:
            # When trex starts jumping, the direction of movement is up.
            direction = -1 if self.trex.reached else 1
            self.trex.jump_action(direction)

            # When trex reaches the max jump height, the direction of movement is reversed down.
            if self.trex.rect.y <= self.trex.max_jump_height:
                self.trex.reached = True

            # Reset jump and reached flags when back to the ground.
            if self.trex.rect.y >= self.trex.original_y_pos:
                self.trex.jump = False
                self.trex.reached = False
            #print(self.trex.reached, self.trex.rect.y, self.trex.original_y_pos)
    
    def _check_trex_obstacle_collide(self):
        '''Check for collision between trex and obstacle.'''
        collide_dict = {'Cactus': [], 'FlyingLizard': []}
        for sprite in self.obstacle.sprites():
            # The below variable is only used for cactus to help get the appropriate
            # coordinate of each cactus because of the different sizes of cactuses.
            scale = sprite.rect.width / 80

            # Specify collide points for cactus and flying lizard.
            if sprite.__class__.__name__ == 'Cactus':
                collide_point_1 = (sprite.rect.centerx, sprite.rect.centery - int(35 * scale))
                collide_point_2 = (sprite.rect.centerx - int(13 * scale), sprite.rect.centery - int(22 * scale))
                collide_point_3 = (sprite.rect.centerx, sprite.rect.centery + int(10 * scale))
                collide_dict['Cactus'].append(collide_point_1)
                collide_dict['Cactus'].append(collide_point_2)
                collide_dict['Cactus'].append(collide_point_3)
            elif sprite.__class__.__name__ == 'FlyingLizard':
                collide_point_1 = (sprite.rect.centerx - 28, sprite.rect.centery - 16)
                collide_point_2 = (sprite.rect.centerx - 6, sprite.rect.centery + 15)
                collide_point_3 = (sprite.rect.centerx + 26, sprite.rect.centery - 2)
                collide_dict['FlyingLizard'].append(collide_point_1)
                collide_dict['FlyingLizard'].append(collide_point_2)
                collide_dict['FlyingLizard'].append(collide_point_3)

            for type in collide_dict:
                for i, collide_point in enumerate(collide_dict[type]):
                    if not self.trex.duck:
                        if self.trex.head_rect.collidepoint(collide_point):
                            self.game_active = False
                            #self.pcollide = collide_point
                            #print('head', collide_point, i, self.trex.head_rect, sprite.rect)
                        elif self.trex.feet_rect.collidepoint(collide_point):
                            self.game_active = False
                            #self.pcollide = collide_point
                            #print('feet', collide_point, i, self.trex.feet_rect, sprite.rect)
                    else:
                        if self.trex.head_duck_rect.collidepoint(collide_point):
                            self.game_active = False
                            #self.pcollide = collide_point
                            #print('head_duck', collide_point, i, self.trex.head_rect, sprite.rect)

                    # The game is over when a collision happens.
                    if not self.game_active:
                        self.play_button.prepare_msg(' '.join('GAME OVER'), 'Press space to replay')
                        break

    def _update_background(self):
        '''Update background of the game.'''
        self.background.update()
        if self.background.moon.rect.right < self.screen_rect.left:
            self.background.moon.rect.left = self.screen_rect.right
        for sprite in self.background.clouds.sprites():
            if sprite.rect.right < self.screen_rect.left:
                sprite.rect.left = self.screen_rect.right
        for sprite in self.background.stars.sprites():
            if sprite.rect.right < self.screen_rect.left:
                sprite.rect.left = self.screen_rect.right
        for stone in self.background.stones:
            if stone.rect.right < self.screen_rect.left:
                stone.rect.left = self.screen_rect.right

    def _update_screen(self):
        '''Draw all objects to the screen.'''
        self.screen.fill(self.settings.bg_color)
        self.background.draw()
        self.trex.draw()
        self.obstacle.draw(self.screen)
        self.scoreboard.draw()

        # The commented code is only used for testing.
        '''if self.trex.duck:
            pygame.draw.rect(self.screen, (0, 250, 0), self.trex.head_duck_rect)
        else:
            pygame.draw.rect(self.screen, (0, 250, 0), self.trex.head_rect)
            pygame.draw.rect(self.screen, (0, 250, 0), self.trex.feet_rect)
        pygame.draw.circle(self.screen, (250, 0, 0), self.pcollide, 2)'''

        if not self.game_active:
            self.play_button.draw()

        pygame.display.flip()

class Trex:
    '''A class to represent T-rex.'''
    def __init__(self, game):
        '''Initialize trex.'''
        self.screen = game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = game.settings

        # Load trex's default image and set its rect.
        self.default_image = pygame.image.load(Path('images/default_trex.png'))
        self.default_image = pygame.transform.scale_by(self.default_image, 0.5)
        self.default_image_rect = self.default_image.get_rect()
        self.default_image_rect.x = self.screen_rect.x + 20
        self.default_image_rect.bottom = self.screen_rect.bottom - 150

        # Load trex's duck image and set its rect.
        self.duck_image = pygame.image.load(Path('images/duck_trex.png'))
        self.duck_image = pygame.transform.scale_by(self.duck_image, 0.6)
        self.duck_image_rect = self.duck_image.get_rect()
        self.duck_image_rect.x = self.screen_rect.x + 20
        self.duck_image_rect.bottom = self.screen_rect.bottom - 150

        # Hit boxes of trex
        # Hit boxes of default trex
        self.head_rect = pygame.Rect(self.default_image_rect.centerx, self.default_image_rect.centery - 35, 27, 24)
        self.feet_rect = pygame.Rect(self.default_image_rect.centerx - 20, self.default_image_rect.centery + 2, 26, 33)

        # Hit box of duck trex
        self.head_duck_rect = pygame.Rect(self.duck_image_rect.centerx - 26, self.duck_image_rect.centery + 6, 64, 22)

        # The below attribute is only used to modify the position of images
        # because of the different sizes between the default and duck images.
        self.mod = False

        # Attribute image and rect hold the current image and its rect.
        self.image = self.default_image
        self.rect = self.default_image_rect
        self.reset_state()
        self.original_y_pos = self.rect.y
        self.max_jump_height = self.original_y_pos - self.rect.height * 2

    def jump_action(self, direction):
        '''Update jump action, as well as the relevant hit boxes.'''
        self.rect.y -= self.settings.trex_jump_speed * direction
        self.head_rect.y -= self.settings.trex_jump_speed * direction
        self.feet_rect.y -= self.settings.trex_jump_speed * direction
        self.head_duck_rect.y -= self.settings.trex_jump_speed * direction

    def duck_action(self):
        '''Perform duck action.'''
        if self.duck:
            self.image = self.duck_image

            # The below code is only used to modifying the position of image
            if not self.jump:
                self.rect = self.duck_image_rect
                self.rect.x = self.screen_rect.x + 20
                self.rect.bottom = self.screen_rect.bottom - 150
                if self.mod:
                    self.head_duck_rect.y -= 16
                    self.mod = False
            else:
                if not self.mod:
                    self.head_duck_rect.y += 16
                    self.mod = True
        else:
            self.image = self.default_image

            # The below code is only used to modifying the position of image
            if not self.jump:
                self.rect = self.default_image_rect
                self.rect.x = self.screen_rect.x + 20
                self.rect.bottom = self.screen_rect.bottom - 150

    def reset_state(self):
        '''Set or reset settings to original state.'''
        self.rect = self.default_image_rect
        self.rect.x = self.screen_rect.x + 20
        self.rect.bottom = self.screen_rect.bottom - 150

        self.head_rect = pygame.Rect(self.default_image_rect.centerx, self.default_image_rect.centery - 35, 27, 24)
        self.feet_rect = pygame.Rect(self.default_image_rect.centerx - 20, self.default_image_rect.centery + 2, 26, 33)

        self.head_duck_rect = pygame.Rect(self.duck_image_rect.centerx - 26, self.duck_image_rect.centery + 6, 64, 22)

        self.jump = False
        self.reached = False
        self.duck = False

        self.mod = False

    def draw(self):
        '''Draw trex.'''
        self.screen.blit(self.image, self.rect)

class FlyingLizard(pygame.sprite.Sprite):
    '''A class to represent flying lizard.'''
    def __init__(self, game):
        '''Initialize flying lizard.'''
        super().__init__()
        self.screen = game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = game.settings

        # Load image and set its rect
        self.image = pygame.image.load(Path('images/flying_lizard.png'))
        self.image = pygame.transform.scale_by(self.image, 0.5)
        self.rect = self.image.get_rect()
        self.reset_state()

    def update(self):
        '''Update horizontal position.'''
        self.rect.x -= self.settings.flying_lizard_speed

    def reset_state(self):
        '''Set or reset settings to original state.'''
        self.rect.left = self.screen_rect.right
        self.rect.bottom = self.screen_rect.bottom - 230

    def draw(self):
        '''Draw flying lizard.'''
        self.screen.blit(self.image, self.rect)

class Cactus(pygame.sprite.Sprite):
    '''A class to represent cactus.'''
    def __init__(self, game):
        '''Initialize cactus.'''
        super().__init__()
        self.screen = game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = game.settings

        # Load image and set its rect.
        self.image = pygame.image.load(Path('images/cactus.png'))
        self.rescale_flip_cactus(0.5)
        
    def rescale_flip_cactus(self, factor, flip=False):
        '''Rescale and/or flip horizontally image and reset its rect.'''
        self.image = pygame.transform.scale_by(self.image, factor)
        if flip:
            self.image = pygame.transform.flip(self.image, flip_x=True, flip_y=False)
        self.rect = self.image.get_rect()
        self.reset_state()

    def update(self):
        '''Update horizontal position'''
        self.rect.x -= self.settings.cactus_speed

    def reset_state(self):
        '''Set or reset settings to original state.'''
        self.rect.left = self.screen_rect.right
        self.rect.bottom = self.screen_rect.bottom - 150

    def draw(self):
        '''Draw cactus.'''
        self.screen.blit(self.image, self.rect)

class Scoreboard:
    '''A class to represent scoreboard.'''
    def __init__(self, game):
        '''Initialize scoreboard.'''
        self.screen = game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = game.settings

        self.text_color = (100, 100, 100)
        self.font = self.settings.get_font(size=32)

        self.score = 0
        self.high_score = 0

        self.prepare_score()
        self.prepare_high_score()

    def prepare_score(self):
        '''Prepare score to draw.'''
        self.score_img = self.font.render(f'{round(self.score):05}', True, self.text_color)
        self.score_img_rect = self.score_img.get_rect()
        self.score_img_rect.right = self.screen_rect.right - 20
        self.score_img_rect.top = self.screen_rect.top + 20

    def prepare_high_score(self):
        '''Prepare high score to draw.'''
        self.high_score_img = self.font.render(f'HI {round(self.high_score):05}', True, self.text_color)
        self.high_score_img_rect = self.high_score_img.get_rect()
        self.high_score_img_rect.right = self.score_img_rect.left - 20
        self.high_score_img_rect.top = self.screen_rect.top + 20

    def check_high_score(self):
        '''Check for new high score.'''
        if self.score > self.high_score:
            self.high_score = self.score
            self.prepare_high_score()

    def draw(self):
        '''Draw score and high score'''
        self.screen.blit(self.score_img, self.score_img_rect)
        self.screen.blit(self.high_score_img, self.high_score_img_rect)

class Cloud(pygame.sprite.Sprite):
    '''A class to represent cloud.'''
    def __init__(self, game):
        '''Initialize cloud.'''
        super().__init__()
        self.screen = game.screen
        self.screen_rect = self.screen.get_rect()

        # Load image and set its rect.
        self.image = pygame.image.load(Path('images/cloud.png'))
        self.image = pygame.transform.scale_by(self.image, 0.5)
        self.image.set_alpha(50)
        self.rect = self.image.get_rect()
        self.rect.x = self.screen_rect.x + 50
        self.rect.y = self.screen_rect.y

    def update(self):
        '''Update horizontal position.'''
        self.rect.x -= 2

    def draw(self):
        '''Draw cloud.'''
        self.screen.blit(self.image, self.rect)

class Moon:
    '''A class to represent moon.'''
    def __init__(self, game):
        '''Initialize moon.'''
        self.screen = game.screen
        self.screen_rect = self.screen.get_rect()

        # Load image and set its rect.
        self.image = pygame.image.load(Path('images/moon.png'))
        self.image = pygame.transform.scale_by(self.image, 0.5)
        self.image.set_alpha(100)
        self.rect = self.image.get_rect()
        self.rect.x = self.screen_rect.x + 700
        self.rect.y = self.screen_rect.y + 75

    def update(self):
        '''Update horizontal position.'''
        self.rect.x -= 1

    def draw(self):
        '''Draw moon.'''
        self.screen.blit(self.image, self.rect)

class Star(pygame.sprite.Sprite):
    '''A class to represent star.'''
    def __init__(self, game):
        '''Initialize star.'''
        super().__init__()
        self.screen = game.screen
        self.screen_rect = self.screen.get_rect()

        # Load image and set its rect.
        self.image = pygame.image.load(Path('images/star.png'))
        self.image = pygame.transform.scale_by(self.image, 0.1)
        self.image.set_alpha(100)
        self.rect = self.image.get_rect()
        self.rect.x = self.screen_rect.x + 200
        self.rect.y = self.screen_rect.y + 50

    def update(self):
        '''Update horizontal position.'''
        self.rect.x -= 1

    def draw(self):
        '''Draw star.'''
        self.screen.blit(self.image, self.rect)

class Stone():
    '''A class to represent stone'''
    def __init__(self, game, width=2, height=2):
        '''Initialize stone.'''
        self.screen = game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = game.settings

        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.x = self.screen_rect.x
        self.rect.y = self.screen_rect.y

    def update(self):
        '''Update horizontal position'''
        self.rect.x -= self.settings.cactus_speed

    def draw(self):
        '''Draw stone.'''
        pygame.draw.rect(self.screen, (100, 100, 100), self.rect)

class Background:
    '''A class to control all the background components.'''
    def __init__(self, game):
        '''Initialize background'''
        self.screen = game.screen
        self.settings = game.settings

        self.moon = Moon(self)
        self.add_clouds()
        self.add_stars()

        self.road = pygame.Rect(0, 290, self.settings.screen_width, 2)
        self.add_stones()

    def add_clouds(self):
        '''Add clouds.'''
        self.clouds = pygame.sprite.Group()
        distance = 300
        heights = (100, 50, 75)
        for i, height in enumerate(heights):
            cloud = Cloud(self)
            cloud.rect.x += distance * i
            cloud.rect.y += height
            self.clouds.add(cloud)

    def add_stars(self):
        '''Add stars.'''
        self.stars = pygame.sprite.Group()
        distance = 400
        heights = (50, 75)
        for i, height in enumerate(heights):
            star = Star(self)
            star.rect.x += distance * i
            star.rect.y += height
            self.stars.add(star)

    def add_stones(self):
        '''Add stones.'''
        self.stones = []
        distances = accumulate(random.choices(range(20, 51), k=22))
        heights = range(5, 11)
        stone_widths = range(2, 10)
        stone_heights = (2, 3)
        for distance in distances:
            stone = Stone(self, random.choice(stone_widths), random.choice(stone_heights))
            stone.rect.x += distance
            stone.rect.y += 290 + random.choice(heights)
            self.stones.append(stone)

    def update(self):
        '''Update horizontal postion of all background's components.'''
        self.moon.update()
        self.clouds.update()
        self.stars.update()
        for stone in self.stones:
            stone.update()

    def draw(self):
        '''Draw background.'''
        self.stars.draw(self.screen)
        self.moon.draw()
        self.clouds.draw(self.screen)
        pygame.draw.rect(self.screen, (100, 100, 100), self.road)
        for stone in self.stones:
            stone.draw()

class Button:
    '''A class to represent button.'''
    def __init__(self, game):
        '''Initialize button.'''
        self.screen = game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = game.settings

        self.width = 96
        self.height = 54
        self.text_color = (100, 100, 100)
        self.font = self.settings.get_font(size=24)
        self.secondary_font = self.settings.get_font(size=16)

        self.prepare_msg('Press space to play')

    def prepare_msg(self, msg, submsg=None):
        '''Prepare message to draw.'''
        self.msg_img = self.font.render(msg, True, self.text_color)
        self.msg_img_rect = self.msg_img.get_rect()
        self.msg_img_rect.center = self.screen_rect.center

        # Prepare submessage to draw if given.
        if submsg:
            self.submsg_img = self.secondary_font.render(submsg, True, self.text_color)
            self.submsg_img_rect = self.submsg_img.get_rect()

            self.msg_img_rect.y -= 30
            self.submsg_img_rect.top = self.msg_img_rect.bottom + 30
            self.submsg_img_rect.centerx = self.msg_img_rect.centerx

    def draw(self):
        '''Draw message and submessage if given.'''
        self.screen.blit(self.msg_img, self.msg_img_rect)
        try:
            self.screen.blit(self.submsg_img, self.submsg_img_rect)
        except AttributeError:
            pass

if __name__ == '__main__':
    game = DinoGame()
    game.run_game()