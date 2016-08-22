import pyglet
import math
import random

WIDTH = 1100
HEIGHT = 700
MAX_SPEED = 250
keys = set()
window = pyglet.window.Window(width = WIDTH, height = HEIGHT)

background_source = pyglet.image.load("data/graphics/Backgrounds/purple.png")
background = pyglet.sprite.Sprite(background_source)
lives_img_source = pyglet.image.load("data/graphics/PNG/UI/playerLife2_green.png")
lives_img = pyglet.sprite.Sprite(lives_img_source)
ship_img = pyglet.image.load("data/graphics/PNG/playerShip1_green.png")
laser_img = pyglet.image.load("data/graphics/PNG/LASERS/laserGreen13.png")
ast_img_list = ["data/graphics/PNG/Meteors/meteorGrey_big1.png",
                "data/graphics/PNG/Meteors/meteorGrey_big2.png",
                "data/graphics/PNG/Meteors/meteorGrey_big3.png",
                "data/graphics/PNG/Meteors/meteorGrey_big4.png"]
main_batch = pyglet.graphics.Batch()

pyglet.font.add_file("data/PressStart2P-Regular.ttf")
game_over_label = pyglet.text.Label("Game OVER", x=WIDTH/2, y=HEIGHT/2,
                                    anchor_x="center",
                                    font_name = "Press Start 2P",
                                    font_size = 50,
                                    color = (0,0,0,255))

class Game:
    def __init__(self):
        self.lives = 3
        self.level = 1
        self.score = 0
        self.level_label = None

    def minus_life (self):
        self.lives -= 1
        if self.lives < 1:
            spaceship.remove()

    def plus_level (self):
        count = 0
        for obj in objects:
            if isinstance (obj, Asteroid):
                count += 1

        if count == 0:
            self.level += 1
            spaceship.start()
            for obj in objects:
                if isinstance (obj, Laser):
                    obj.remove()
            first_asteroids(self.level + 1)

    def tick(self, dt):
        self.level_label = pyglet.text.Label("LEVEL no."+str(game.level), x=10, y=680, bold=True)


game = Game()


class SpaceObject:
    def __init__ (self, window, image):
        self.x = WIDTH/2
        self.y = HEIGHT/2
        self.rotation = 0
        self.x_speed = 0
        self.y_speed = 0
        self.speed = 0
        self.sprite = pyglet.sprite.Sprite(image, batch = main_batch)
        self.sprite.image.anchor_x = self.sprite.image.width / 2 #rotace kolem stredu
        self.sprite.image.anchor_y = self.sprite.image.height / 2
        self.window = window
        self.radius = max(self.sprite.image.height, self.sprite.image.width) / 2     #určení rozměru pro výpočet poloměru (co je delší - výška nebo šířka)

    def tick(self, dt):
        #aktualizace hry
        self.x += self.x_speed * dt
        self.y += self.y_speed * dt

        if self.x > window.width:      #vylétnutí z okna
            self.x = 0
        if self.y > window.height:
            self.y = 0
        if self.x < 0:
             self.x = window.width
        if self.y < 0:
            self.y = window.height

        #aktualizace obrázku
        self.sprite.rotation = self.rotation  #rotation v self.sprite.rotation je atribut třídy sprite, podle tohoto program ví, že hodnota "self.rotation" se má použít na rotaci a ne na něco jiného (pohyb, barva,..)
        self.sprite.x = self.x
        self.sprite.y = self.y

        self.x_speed = math.sin(self.rotation * (math.pi / 180)) * self.speed
        self.y_speed = math.cos(self.rotation * (math.pi / 180)) * self.speed

    def remove (self):
        if self in objects:
            objects.remove(self)
            self.sprite.delete()

    def distance(self, a, b, wrap_size):    #distance, overlaps, intersects počítají, zda se objekty potkají
        result = abs(a - b)
        if result > wrap_size / 2:
            result = wrap_size - result
        return result

    def overlaps(self, a, b):
        distance_squared = (self.distance(a.x, b.x, window.width) ** 2 +
                            self.distance(a.y, b.y, window.height) ** 2)
        max_distance_squared = (a.radius + b.radius) ** 2
        return distance_squared < max_distance_squared

    def intersects (self, obj):
        if self.overlaps (self, obj):
            return True

    def hit_spaceship(self, spaceship):
        pass

    def hit_by_laser(self, laser):
        pass

class Spaceship(SpaceObject):
    def __init__(self, window, image):
        super().__init__(window, image)
        self.shoot = 0
        self.immortality = 0
        self.visibility = 0

    def tick(self, dt):
        super().tick(dt)
        self.shoot -= dt            #střelba jednou za 0.3 sec
        if self.shoot < 0:
            self.shoot = 0

        self.immortality -= dt        #nesmrtelnost na 2 sec
        if self.immortality < 0:
            self.immortality = 0

        self.visibility -= dt
        if self.visibility < 0:
            self.visibility = 0
        if self.visibility > 0:
            if self.sprite.visible:
                self.sprite.visible = False
            else:
                self.sprite.visible = True
        if self.visibility == 0:
            self.sprite.visible = True


        #rotace
        if "left" in keys:
            self.rotation -= 3
        if "right" in keys:
            self.rotation += 3

        #akcelerace
        if "forward" in keys and self.speed < MAX_SPEED:
            self.speed += 5
        #zpomalení
        if "backward" in keys:
            self.speed -= 5
            if self.speed < 0:
                self.speed = 0
        #zastavení
        if "forward" not in keys:
            self.speed -= 1
            if self.speed < 0:
                self.speed = 0

        for obj in objects:             #zda se nějaký objekt potkal s lodí, pokud to bude asteroid, tak raketa umírá
            obj.hit_spaceship(spaceship)

    def start (self):
        keys.clear()
        self.x = window.width/2
        self.y = window.height/2
        self.speed = 0
        self.immortality = 2


class Laser(SpaceObject):
    def __init__(self, window, image, spaceship):
        super().__init__(window, image)
        self.sprite = pyglet.sprite.Sprite(laser_img, batch = main_batch)
        self.x = spaceship.x
        self.y = spaceship.y
        self.rotation = spaceship.rotation
        self.x_speed = spaceship.x_speed
        self.y_speed = spaceship.y_speed
        self.speed = 500
        self.time_to_live = window.width/600

    def tick(self,dt):
        super().tick(dt)
        self.time_to_live -= dt
        if self.time_to_live < 0:
            self.remove()

        for obj in objects:         #zda se laser potkal s nějakým objektem, pokud ano, objekt asteroid se dělí, raketa umírá
            obj.hit_by_laser(self)


class Asteroid(SpaceObject):
    def __init__(self, window, image):
        super().__init__(window, image)
        self.x = random.randrange(window.width)
        self.y = 0
        self.speed = 50

    def hit_spaceship(self, spaceship):
        if self.intersects(spaceship) and spaceship.immortality == 0:
            game.minus_life()
            spaceship.visibility = 2
            spaceship.start()

    def hit_by_laser(self, laser):
        if self.intersects(laser):
            laser.remove()
            self.split()

    def split(self):
        if self.sprite.scale > 0.25:
            for smaller in range (2):
                smaller = new_asteroid()
                smaller.sprite.scale = self.sprite.scale - 0.25
                smaller.x = self.x
                smaller.y = self.y
                smaller.radius = self.radius * smaller.sprite.scale
                smaller.speed = self.speed * 1.3
                objects.append(smaller)
        self.remove()
        game.plus_level()


objects = []

def new_asteroid():
    asteroid_img = pyglet.image.load(random.choice(ast_img_list))
    new_asteroid = Asteroid(window, asteroid_img)
    new_asteroid.sprite = pyglet.sprite.Sprite(asteroid_img, batch = main_batch)
    new_asteroid.rotation = random.uniform (0,360)
    return new_asteroid
def first_asteroids (amount):               #funkce pro vytvoření více jak jednoho asteroidu s různými vlastnostmi
        for one in range(amount):
            one = new_asteroid()
            one.sprite.scale = random.choice([0.25,0.5,0.75,1])
            one.radius *= one.sprite.scale  #radius zmenšených asteroidů dle náhodně vybraného scale
            objects.append(one)

first_asteroids(1)

spaceship = Spaceship(window,ship_img)
objects.append(spaceship)

def draw():
        window.clear()
        #vykresli pozadí
        for x_axis in range (0, window.width, background.image.width):
            for y_axis in range (0, window.height, background.image.height):
                background.x = x_axis
                background.y = y_axis
                background.draw()
        #vykresli objekty
        #vykresluje plynule na hranách - obrázek neskočí celý pryč, ale jen jeho poměrná část (z rakety může být půlka vidět na jedné hraně a druhá půlka na opačné)
        for x_offset in (-window.width, 0, window.width):
            for y_offset in (-window.height, 0, window.height):
                pyglet.gl.glPushMatrix()
                pyglet.gl.glTranslatef(x_offset, y_offset, 0)
                main_batch.draw()           #main_batch obsahuje všechny objekty v hře
                pyglet.gl.glPopMatrix()

        game.level_label.draw()

        #vykresli počet životů
        for lives in range (game.lives-1):
                lives_img.x = lives*40 + 10
                lives_img.y = 5
                lives_img.draw()
        #vykresli game over
        if game.lives < 1:
            game_over_label.draw()

def pressed_keys(symbol,mod):
    #klávesy pro ovládání lodi
    if symbol == pyglet.window.key.LEFT:  #rotace vlevo
        keys.add("left")
    elif symbol == pyglet.window.key.RIGHT:   #rotace vpravo
        keys.add("right")
    elif symbol == pyglet.window.key.UP:      #zrychlení
        keys.add("forward")
    elif symbol == pyglet.window.key.DOWN:      #zpomalení
        keys.add("backward")
    elif symbol == pyglet.window.key.SPACE:               #zobrazení střely při mezerníku
        if spaceship in objects:
            if spaceship.shoot == 0:
                laser = Laser(window,laser_img, spaceship)
                objects.append(laser)
                spaceship.shoot = 0.3       #jestliže je čas do střely (shoot) na nule, vytvoří se střela a čas se posune na 0.3 sec ze kterého tick u spaceshipu odečítá

def released_keys(symbol,mod):
    #klávesy pro ovládání lodi
    if symbol == pyglet.window.key.LEFT:  #rotace vlevo
        keys.discard("left")
    elif symbol == pyglet.window.key.RIGHT:   #rotace vpravo
        keys.discard("right")
    elif symbol == pyglet.window.key.UP:
        keys.discard("forward")
    elif symbol == pyglet.window.key.DOWN:      #zpomalení
        keys.discard("backward")

window.push_handlers(
    on_draw = draw,
    on_key_press = pressed_keys,
    on_key_release = released_keys)

def tick(dt):                   #místo for cyklu pro item in objects v schedule, pže to zobrazuje jen jednou, ale ne pro nové objekty
    for obj in objects:
        obj.tick(dt)
    game.tick(dt)
pyglet.clock.schedule(tick)         #dívá se na fci tick (ne ve třídě, ale obecná fce tick), ale nevolá ji, takže bez ()

pyglet.app.run()
