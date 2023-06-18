import pygame as py
import random

class Player:
    def __init__(self):
        self.x = 100
        self.y = 300
        self.flying = False
        self.y_speed = 0
        self.gravity = 0.05 
        self.heli = py.transform.scale(py.image.load('helicopter.png'), (60, 60))
        self.rect = self.heli.get_rect(topleft=(self.x, self.y))

    def draw(self, screen):
        self.rect.topleft = (self.x, self.y)
        screen.blit(self.heli, self.rect)
        return self.rect

    def move(self):
        if self.flying:
            self.y_speed += self.gravity
        else:
            self.y_speed -= self.gravity
        self.y -= self.y_speed
        return self.y, self.y_speed


class Coin:
    size = 10
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False
        self.brightness = 255  # Maximum brightness
        self.dimming = True  # Whether the coin is currently getting dimmer

    def draw(self, screen):
        if not self.collected:
            color = (self.brightness, self.brightness, 0)  # RGB color for the coin
            py.draw.circle(screen, color, (self.x, self.y), self.size)
            if self.dimming:
                self.brightness -= 5  # Decrease brightness to create dimming effect
                if self.brightness <= 100:  # If brightness is low enough, start brightening
                    self.dimming = False
            else:
                self.brightness += 5  # Increase brightness to create brightening effect
                if self.brightness >= 255:  # If brightness is high enough, start dimming
                    self.dimming = True

    def get_rect(self):
        return py.Rect(self.x, self.y, self.size, self.size)
    
    def collect(self, player):
        if player.rect.colliderect(self.get_rect()):
            self.collected = True
            return True
        return False


class Map:
    def __init__(self, width, height):
        self.new_map = True
        self.rects = []
        self.coins = []
        self.rect_width = 10
        self.total_rects = (width//self.rect_width) +2
        self.spacer = 10
        self.map_speed = 10
        self.width = width
        self.height = height

    def generate_new(self, player_y):
        rects = []
        coins = []
        top_height = random.randint(0,300)
        player_y = top_height + 150
        for i in range(self.total_rects):
            top_height = random.randint(top_height - self.spacer, top_height + self.spacer)
            if top_height < 0:
                top_height = 0
            elif top_height > 300:
                top_height = 300
            rects.append(py.Rect(i * self.rect_width, 0, self.rect_width, top_height))
            rects.append(py.Rect(i * self.rect_width, top_height + 300, self.rect_width, self.height))
            if i % 100 == 0:  # Every 100 rects, add a coin
                coin_y = random.randint(top_height + Coin.size, top_height + 300 - Coin.size)
                coins.append(Coin(i * self.rect_width, coin_y))
        self.coins = coins
        return rects, player_y


    def draw(self, screen):
        for rect in self.rects:
            py.draw.rect(screen, 'green', rect)
        py.draw.rect(screen, 'dark gray', [0,0,  self.width, self.height], 12)

    def move(self, score):
        for i in range(len(self.rects)):
            self.rects[i].move_ip(-self.map_speed, 0)
            if self.rects[i].right < 0:
                self.rects.pop(1)
                self.rects.pop(0)
                top_height = random.randint(self.rects[-2].height - self.spacer, self.rects[-2].height + self.spacer)
                if top_height < 0:
                    top_height = 0
                elif top_height > 300:
                    top_height = 300
                self.rects.append(py.Rect(self.rects[-2].right, 0, self.rect_width, top_height))
                self.rects.append(py.Rect(self.rects[-2].right, top_height + 300, self.rect_width, self.height))
                score += 1
                # Generate a new coin every screen width
                if score % (self.width // self.rect_width) == 0:
                    coin_y = random.randint(self.rects[-2].bottom + Coin.size, self.rects[-1].top - Coin.size)
                    self.coins.append(Coin(self.rects[-1].right + self.width, coin_y))
        # Move coins and remove coins that have moved off the screen
        self.coins = [coin for coin in self.coins if coin.x + coin.size > 0]
        for coin in self.coins:
            coin.x -= self.map_speed
        return self.rects, score




class Game:
    def __init__(self):
        py.init()
        py.font.init()

        self.WIDTH = 1000
        self.HEIGHT = 600
        self.screen = py.display.set_mode((self.WIDTH, self.HEIGHT))

        py.display.set_caption('KnotZHeliRace')

        self.font = py.font.SysFont('freesansbold', 20)
        self.fps= 60
        self.timer = py.time.Clock()

        self.score = 0
        self.high_score = 0
        self.active = True

        self.player = Player()
        self.map = Map(self.WIDTH, self.HEIGHT)

    def check_collision(self, player_circle):
        for rect in self.map.rects:
            if player_circle.colliderect(rect):
                self.active = False
        return self.active

    def run(self):
        run = True
        while run:

            self.screen.fill('black')
            self.timer.tick(self.fps)
            if self.map.new_map:
                self.map.rects, self.player.y = self.map.generate_new(self.player.y)
                self.map.new_map = False
            self.map.draw(self.screen)
            player_circle = self.player.draw(self.screen)
            if self.active:
                #move player
                self.player.y, self.player.y_speed = self.player.move()
                #move map
                self.map.rects, self.score = self.map.move(self.score)
            self.active = self.check_collision(player_circle)
            
            for coin in self.map.coins:
                coin.draw(self.screen)
                if coin.collect(self.player):
                    self.score += 1  # Or however many points you want to award
                    self.map.map_speed -= 0.1  # Slow down the map


            for event in py.event.get():
                if event.type == py.QUIT:
                    run = False
                if event.type == py.KEYDOWN:
                    if event.key == py.K_SPACE:
                        self.player.flying = True
                    if event.key == py.K_RETURN:
                        if not self.active:
                            self.map.new_map = True
                            self.active = True
                            self.player.y_speed = 0
                            self.map.map_speed = 10
                            if self.score > self.high_score:
                                self.high_score = self.score 
                            self.score = 0  
                if event.type == py.KEYUP:
                    if event.key == py.K_SPACE:
                        self.player.flying = False


            #score increases difficulty
            self.map.map_speed = 1 + self.score//50
            self.map.spacer = 1 + self.score//100  

            self.screen.blit(self.font.render(f'Score: {self.score}', True, 'black'), (20, 15))
            self.screen.blit(self.font.render(f'High Score: {self.high_score}', True, 'black'), (20, 565))
            if not self.active:
                self.screen.blit(self.font.render('Press Enter to Restart', True, 'black'), (self.WIDTH * 0.5 - 100, self.HEIGHT * .15))
                self.screen.blit(self.font.render('Press Enter to Restart', True, 'black'), (self.WIDTH * 0.5 - 100, self.HEIGHT * .85))

            py.display.flip()

game = Game()
game.run()
