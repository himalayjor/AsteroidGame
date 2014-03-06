# program template for Spaceship
import pygame
import math
import random, sys, pygame.mixer
from pygame.locals import *


# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0.5
started = False
rockgroup = set([])
missilegroup =  set([])
explosiongroup = set([])

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated



# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)


# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.forward = [0,0]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.tic = [self.image_center[0] + 90, self.image_center[1]]
        self.rect = (0, 0, self.image_size[0], self.image_size[1])
        self.rect1 = (90, 0, self.image_size[0], self.image_size[1])

    def get_position(self):
        return self.pos

    def set_initial(self):
        self.pos = [WIDTH / 2, HEIGHT / 2]
        self.vel = [0, 0]

    def get_radius(self):
        return self.radius

    def rot_center(self, image, angle):

       orig_rect = image.get_rect()
       rot_image = pygame.transform.rotate(image, - (180 * angle / math.pi))
       rot_rect = orig_rect.copy()
       rot_rect.center = rot_image.get_rect().center
       #rot_image = rot_image.subsurface(rot_rect).copy()

       return (rot_image, rot_rect)

    def draw(self, screen):
        posrect = (self.pos[0] - self.image_size[0]//2, self.pos[1] -self.image_size[1]//2, self.image_size[0], self.image_size[1])

        if not self.thrust:
            (rotateimg, rotateRect) = self.rot_center(self.image.subsurface(self.rect).copy() ,  self.angle)
            screen.blit(rotateimg , posrect, rotateRect)
        else:
            (rotateimg, rotateRect) = self.rot_center(self.image.subsurface(self.rect1).copy() , self.angle)
            screen.blit(rotateimg , posrect, rotateRect)


    def update(self):

        x = score / 6000 + 1
        self.pos[0] = (self.pos[0] + x * self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] +  x * self.vel[1]) % HEIGHT


        self.forward = angle_to_vector(self.angle)

        if self.thrust:

            self.vel[0] += 0.1 * self.forward[0]
            self.vel[1] += 0.1 * self.forward[1]

        self.vel = [self.vel[0] * 0.991, self.vel[1] * 0.991]

        self.angle += self.angle_vel

    def increase_av(self, val):
        self.angle_vel += val

    def decrease_av(self, val):
        self.angle_vel -= val

    def set_thrust(self):
        self.thrust = not self.thrust

    def shoot(self):
        global missilegroup

        x = self.pos[0] + self.forward[0] * self.radius
        y = self.pos[1] + self.forward[1] * self.radius
        vx = self.vel[0] + self.forward[0] * 6
        vy = self.vel[1] + self.forward[1] * 6
        a_missile = Sprite([x, y], [vx, vy], self.angle, 0, missile_image, missile_info, missile_sound)
        missilegroup.add(a_missile)

# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.stop()
            sound.play()

    def get_position(self):
        return self.pos

    def get_radius(self):
        return self.radius

    def draw(self, canvas):
        imagepos = [self.pos[0] -self.image_size[0]//2, self.pos[1] -self.image_size[1]//2, self.image_size[0], self.image_size[1]]
        if not self.animated:
            imagepart = [0, 0, self.image_size[0], self.image_size[1]]
            canvas.blit(self.image, imagepos, imagepart)
        else:
            imagepart = [self.age * self.image_size[0], 0, self.image_size[0], self.image_size[1]]
            canvas.blit(self.image, imagepos , imagepart)

    def update(self):
        self.age += 1
        if self.age > self.lifespan:
            return True

        self.angle += self.angle_vel
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        return False

    def collide(self, ob):
        global explosiongroup
        pos1 = self.pos
        pos2 = ob.get_position()
        dis = dist(pos1, pos2)
        r1 = self.radius
        r2 = ob.get_radius()

        if (r1 + r2 >= dis):
            explosion = Sprite(self.pos, [0, 0], self.angle, 0, explosion_image, explosion_info, explosion_sound)
            explosiongroup.add(explosion)
            return True
        else:
            return False

def draw(screen):
    global time, score, lives, my_ship


    # animiate background
    screen.blit(nebula_image, (0,0))


    font=pygame.font.Font(None, 24)
    scoretext=font.render('Lives', 1,(255,255,255))
    screen.blit(scoretext, (50, 50))
    scoretext=font.render(str(lives), 1,(255,255,255))
    screen.blit(scoretext, (75, 75))
    scoretext=font.render('Score', 1,(255,255,255))
    screen.blit(scoretext, (700, 50))
    scoretext=font.render(str(score), 1,(255,255,255))
    screen.blit(scoretext, (720, 75))

    my_ship.draw(screen)

    my_ship.update()


    if not started:
        sz = splash_info.get_size()
        splashpos = [WIDTH//2 - sz[0]//2 ,  HEIGHT//2 - sz[1]//2 , sz[0], sz[1]]
        screen.blit(splash_image, splashpos)
    else:
      process_sprite_group(rockgroup, screen)
      count = group_collide(rockgroup, my_ship)
      lives -= count
      if lives <= 0:
            resetgame()

      process_sprite_group(missilegroup, screen)
      process_sprite_group(explosiongroup, screen)
      x = group_group_collide(rockgroup, missilegroup)
      score += x * 10

def group_collide(se, ob):
    count = 0
    for item in list(se):
        if item.collide(ob):
            count += 1
            se.remove(item)
    return count

def resetgame():
    global rockgroup, missilegroup, lives, score, started, timer

    rockgroup = set([])
    missilegroup = set([])
    explosiongroup = set([])
    started = False

    soundtrack.stop()


def newgame():
    global started, lives, score
    started = True
    lives = 3
    score = 0
    my_ship.set_initial()

    soundtrack.stop()
    soundtrack.play()

# timer handler that spawns a rock
def rock_spawner():
    global rockgroup

    if len(rockgroup) > 12:
        return

    rock_pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]

    while dist(rock_pos, my_ship.get_position()) < 45:
        rock_pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]

    rock_vel = [random.random() * .6 - .3, random.random() * .6 - .3]
    rock_avel = random.random() * .2 - .1
    a_rock = Sprite(rock_pos, rock_vel, 0, rock_avel, asteroid_image, asteroid_info)

    rockgroup.add(a_rock)

def process_sprite_group(se, canvas):
    for item in list(se):
        item.draw(canvas)
        val = item.update()
        if val:
            se.remove(item)

def group_group_collide(se1, se2):
    count = 0

    for item in list(se1):
        x = group_collide(se2,  item)
        if x > 0:
            se1.remove(item)
        count += x

    return count

def move_ship():
    my_ship.set_thrust()
    ship_thrust_sound.stop()
    ship_thrust_sound.play()

def stop_ship():
    my_ship.set_thrust()
    ship_thrust_sound.stop()

def turn_left():
    my_ship.decrease_av(0.1)

def turn_right():
    my_ship.increase_av(0.1)

def stop_turn_left():
    my_ship.increase_av(0.1)

def stop_turn_right():
    my_ship.decrease_av(0.1)

def fire():
    my_ship.shoot()

inputs = {K_UP : move_ship, K_LEFT : turn_left, K_RIGHT : turn_right }
inputs_down = {K_UP : stop_ship, K_LEFT : stop_turn_left, K_RIGHT : stop_turn_right, K_SPACE: fire }

def keyup(key):
    for i in inputs_down.keys():
        if key == i:
            inputs_down[i]()

def keydown(key):
    for i in inputs.keys():
        if key == i:
            inputs[i]()

def click(pos):
    global started, timer
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        newgame()



# initialize ship and two sprites

def main():
    global debris_info, debris_image, nebula_info, nebula_image, asteroid_info, asteroid_image, splash_info, splash_image, ship_info, ship_image
    global explosion_info, explosion_image, missile_info, missile_image
    global my_ship, a_rock, a_missile
    global missile_sound, ship_thrust_sound, explosion_sound, soundtrack, timer, started


    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
    pygame.display.set_caption('Asteriod')
    clock = pygame.time.Clock()
    milli = clock.tick()


    debris_info = ImageInfo([320, 240], [640, 480])
    debris_image = pygame.image.load('debris2_blue.png').convert()



    nebula_info = ImageInfo([400, 300], [800, 600])
    nebula_image = pygame.image.load("nebula_blue.png").convert()

    splash_info = ImageInfo([200, 150], [400, 300])
    splash_image = pygame.image.load("splash.png").convert()


    ship_info = ImageInfo([45, 45], [90, 90], 35)
    ship_image = pygame.image.load("double_ship.png").convert_alpha()


    missile_info = ImageInfo([5,5], [10, 10], 3, 50)
    missile_image = pygame.image.load("shot2.png").convert_alpha()


    asteroid_info = ImageInfo([45, 45], [90, 90], 40)
    asteroid_image = pygame.image.load("asteroid_blue.png").convert_alpha()


    explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
    explosion_image = pygame.image.load("explosion_alpha.png").convert_alpha()


    soundtrack = pygame.mixer.Sound("soundtrack.wav")
    missile_sound = pygame.mixer.Sound("missile.wav")
    ship_thrust_sound = pygame.mixer.Sound("thrust.wav")
    explosion_sound = pygame.mixer.Sound("explosion.wav")

    my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
    a_rock = Sprite([WIDTH / 3, HEIGHT / 2], [1, 1], 0, 0.1, asteroid_image, asteroid_info)
    a_missile = Sprite([2 * WIDTH / 3, 2 * HEIGHT / 3], [-1,1], 0, 0, missile_image, missile_info, missile_sound)
    started = False

    EVENTROCK = pygame.USEREVENT + 1
    timer = pygame.time.set_timer(EVENTROCK, 1000);

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and started:
                keydown(event.key)
            elif event.type == pygame.KEYUP and started:
                keyup(event.key)
            elif event.type == EVENTROCK and started:
                rock_spawner()
            elif event.type == pygame.MOUSEBUTTONDOWN and not started:
                click(event.pos)


        milli = clock.tick(60)
        draw(screen)


        pygame.display.update()


# get things rolling
#timer.start()

if __name__ == '__main__':
    main()
