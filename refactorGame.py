import pygame as py
import random

class Player:
    def __init__(self):
        self.x = 100
        self.y = 300
        self.flying = False
        self.y_speed = 0
        self.gravity = 0.3
        self.heli = py.transform.scale(py.image.load('heli2.png'), (50, 50))

    def draw(self, screen):
        player = screen.blit(self.heli, (self.x - 40, self.y - 30))
        return player

    def move(self):
        if self.flying:
            self.y_speed += self.gravity
        else:
            self.y_speed -= self.gravity
        self.y -= self.y_speed
        return self.y, self.y_speed

class Map:
    def __init__(self, width, height):
        self.new_map = True
        self.rects = []
        self.rect_width = 10
        self.total_rects = (width//self.rect_width) +2
        self.spacer = 10
        self.map_speed = 2
        self.width = width
        self.height = height

    def generate_new(self, player_y):
        rects = []
        top_height = random.randint(0,300)
        player_y = top_height + 150
        for i in range(self.total_rects):
            top_height = random.randint(top_height - self.spacer, top_height + self.spacer)
            if top_height < 0:
                top_height = 0
            elif top_height > 300:
                top_height = 300
            top_rect = py.Rect(i * self.rect_width, 0, self.rect_width, top_height)
            bot_rect = py.Rect(i * self.rect_width, top_height + 300, self.rect_width, self.height)
            rects.append(top_rect)
            rects.append(bot_rect)
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
                            self.map.map_speed = 2
                            if self.score > self.high_score:
                                self.high_score = self.score 
                            self.score = 0  
                if event.type == py.KEYUP:
                    if event.key == py.K_SPACE:
                        self.player.flying = False
            #score increases difficulty
            self.map.map_speed = 2 + self.score//50
            self.map.spacer = 10 + self.score//100  

            self.screen.blit(self.font.render(f'Score: {self.score}', True, 'black'), (20, 15))
            self.screen.blit(self.font.render(f'High Score: {self.high_score}', True, 'black'), (20, 565))
            if not self.active:
                self.screen.blit(self.font.render('Press Enter to Restart', True, 'black'), (self.WIDTH * 0.5 - 100, self.HEIGHT * .15))
                self.screen.blit(self.font.render('Press Enter to Restart', True, 'black'), (self.WIDTH * 0.5 - 100, self.HEIGHT * .85))

            py.display.flip()

game = Game()
game.run()
