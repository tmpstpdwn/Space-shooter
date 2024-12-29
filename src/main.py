#!/bin/python3

# Module imports

import pygame
import random
import time

### INIT ###

pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

### CLASSES ###

#Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = pygame.image.load('../images/player.png').convert_alpha()
        self.rect = self.image.get_frect(center = (WIDTH/2, HEIGHT/2))
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 500
        self.mask = pygame.mask.from_surface(self.image)
        self.cooldown = 400
        self.can_shoot = True

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_time > self.cooldown:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT]) 
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP]) 
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_sprites, laser_surf, self.rect.midtop)
            laser_sound.play()
            self.last_time = pygame.time.get_ticks()
            self.can_shoot = False
        self.laser_timer()

# Star class
class Star(pygame.sprite.Sprite):
    def __init__(self, group, surf):
        super().__init__(group)
        self.image = surf
        self.rect = self.image.get_frect(center = (random.randint(0, WIDTH), random.randint(0, HEIGHT)))

# Meteor class
class Meteor(pygame.sprite.Sprite):
    def __init__(self, group, surf, pos):
        super().__init__(group)
        self.og = surf
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = random.randint(300, 400)
        self.direction = pygame.math.Vector2(random.uniform(-0.9, 0.9),1)
        self.rotation_speed = random.randint(-50, 50)
        self.rotation = 0

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if self.rect.top > HEIGHT:
            self.kill()
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.og, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

# Laser class
class Laser(pygame.sprite.Sprite):
    def __init__(self, group, surf, pos: tuple):
        super().__init__(group)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
        self.speed = 500
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.rect.y -= self.speed * dt
        if self.rect.bottom < 0:
            self.kill()

# Explotion animation class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, group):
        super().__init__(group)
        self.frames = frames
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_frect(center = pos)
        self.animation_speed = 75

    def update(self, dt):
        self.current_frame += self.animation_speed * dt
        if not int(self.current_frame) >= len(self.frames):
            self.image = self.frames[int(self.current_frame)]
            self.rect = self.image.get_frect(center = self.rect.center)
        else:
            self.kill()

### MAIN ###

# Asset imports.

# Surface imports.
star_surf = pygame.image.load('../images/star.png').convert_alpha()
meteor_surf = pygame.image.load('../images/meteor.png').convert_alpha()
laser_surf = pygame.image.load('../images/laser.png').convert_alpha()
font = pygame.font.Font('../images/Oxanium-Bold.ttf', 30)
explosion_frames = [pygame.image.load(f'../images/explosion/{i}.png').convert_alpha() for i in range(21)]

# Audio imports.
laser_sound = pygame.mixer.Sound('../audio/laser.wav')
laser_sound.set_volume(0.1)
explosion_sound = pygame.mixer.Sound('../audio/explosion.wav')
explosion_sound.set_volume(0.1)
damage_sound = pygame.mixer.Sound('../audio/damage.ogg')
damage_sound.set_volume(0.1)
music_sound = pygame.mixer.Sound('../audio/game_music.wav')
music_sound.set_volume(0.1)
music_sound.play()

# Grp, Sprite creations

all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
for i in range(20):
    Star(all_sprites, star_surf)
player = Player(all_sprites)
grp_list = [all_sprites, meteor_sprites, laser_sprites]

# Timer

meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 800)

# Main Functions

def score():
    current_time = pygame.time.get_ticks() // 100
    text_surf = font.render(str(current_time), True, "#ffffff")
    text_rect = text_surf.get_frect(midbottom=(WIDTH / 2, HEIGHT - 50))
    screen.blit(text_surf, text_rect)
    pygame.draw.rect(screen, 'white', text_rect.inflate(20, 20).move(0, -5), 3, 5)

def draw():
    screen.fill('#3a2e3f')
    score()
    for grp in grp_list:
        grp.draw(screen)
    pygame.display.update()

def update(dt):
    for grp in grp_list:
        grp.update(dt)

def collisions():
    for laser in laser_sprites:
        if pygame.sprite.spritecollide(laser, meteor_sprites, True):
            Explosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()
            laser.kill()
    if pygame.sprite.spritecollide(player, meteor_sprites, False, pygame.sprite.collide_mask):
        damage_sound.play()
        return False
    return True

def main():
    clock = pygame.time.Clock()
    running = True
    while running:

        # Delta time
        dt = clock.tick() / 1000

        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == meteor_event:
                x = random.randint(0, WIDTH)
                y = random.randint(-200, -10)
                Meteor(meteor_sprites, meteor_surf, (x, y))
        else:
            if not running:
                break

        # Update
        update(dt)

        #Draw
        draw()

        #collisions
        running = collisions()

    print("GAME OVER!!")
    time.sleep(1)
    pygame.quit()

# Exec.

if __name__ == "__main__":
    main()

### END ###
