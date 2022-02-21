from dis import dis
from glob import escape
import math
from black import color_diff
from cv2 import rotate
import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 81)

TICKRATE = 60
WIDTH, HEIGHT = 800, 800

SUN_SPRITE = "sun_sprite.png"
EARTH_SPRITE = "earth_sprite.png"
MERCURY_SPRITE = "mercury_sprite.png"
MARS_SPRITE = "mars_sprite.png"
VENUS_SPRITE = "venus_sprite.png"

class CelestialBody:
    # distance from earth to sun in meters
    AU = 149.6e6 * 1000
    # gravitational constant
    G = 6.67428e-11
    # 1 AU = 100 pixels
    SCALE = 250 / AU
    
    
    def __init__(self, x, y, radius, color, mass, x_vel=0, y_vel=0, tickrate=60, sprite=None, cycle=None, starting_rotation=0):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.sprite = sprite
        self.cycle = cycle
        self.rotation = starting_rotation
        self.tickrate = tickrate
        
        self.orbit = []
        self.is_star = False
        self.distance_to_star = 0
        # realtime seconds per step. planetary motion update speed: 1 day / tickrate (for fps independent update speed)
        self.timestep = 3600 * 24 / self.tickrate * 10 # 10 days per second

    def draw(self, win, show_distance=True, show_elipse=True, use_sprites=True):
        x = self.x * self.SCALE + WIDTH / 2
        y = self.y * self.SCALE + HEIGHT / 2
        
        if show_elipse and len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                x, y = point
                x = x * self.SCALE + WIDTH / 2
                y = y * self.SCALE + HEIGHT / 2
                updated_points.append((x, y))
            pygame.draw.aalines(win, self.color, False, updated_points)
            
        if (self.sprite == None or not use_sprites):
            pygame.draw.circle(win, self.color, (x, y), self.radius)
        else:
            rotated_sprite = pygame.transform.rotate(self.sprite, self.rotation)
            rect = rotated_sprite.get_rect(center = self.sprite.get_rect(center = (x, y)).center)
            win.blit(rotated_sprite, rect)
        
        if show_distance and not self.is_star:
            distance_text = FONT.render(f"{round(self.distance_to_star/1000, 1)}km", 1, WHITE)
            win.blit(distance_text, (x - distance_text.get_width() / 2, y - distance_text.get_height() / 2))

    def attraction(self, other_body):
        other_body_x, other_body_y = other_body.x, other_body.y
        distance_x = other_body_x - self.x
        distance_y = other_body_y - self.y
        distance = math.sqrt(distance_y**2 + distance_x**2)
        
        if (other_body.is_star):
            self.distance_to_star = distance
        
        force = self.G * self.mass * other_body.mass / distance**2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force    
        force_y = math.sin(theta) * force
        return force_x, force_y
    
    def update_positions(self, bodies):    
        total_fx = total_fy = 0
        for body in bodies:
            if self == body:
                continue
            
            fx, fy = self.attraction(body)
            total_fx += fx
            total_fy += fy
            
        self.x_vel += total_fx / self.mass * self.timestep
        self.y_vel += total_fy / self.mass * self.timestep
        
        self.x += self.x_vel * self.timestep
        self.y += self.y_vel * self.timestep
        self.orbit.append((self.x, self.y))
        
        if self.cycle is not None:
            self.rotation += 360 * (self.timestep / (3600 * 24 * self.cycle))
            self.rotation = self.rotation % 360
            # print(self.cycle, self.timestep, self.rotation)


def create_solar_system():
    sun_sprite = pygame.image.load(SUN_SPRITE)
    sun_sprite = pygame.transform.smoothscale(sun_sprite, (70, 70))
    sun = CelestialBody(0, 0, 30, YELLOW, 1.98892 * 10**30, tickrate=TICKRATE, sprite=sun_sprite)
    sun.is_star = True
    
    earth_sprite = pygame.image.load(EARTH_SPRITE)
    earth_sprite = pygame.transform.smoothscale(earth_sprite, (30, 30))
    earth = CelestialBody(-1 * CelestialBody.AU, 0, 16, BLUE, 5.9742 * 10**24, y_vel = 29.783 * 1000, tickrate=TICKRATE, sprite=earth_sprite)
    
    mars_sprite = pygame.image.load(MARS_SPRITE)
    mars_sprite = pygame.transform.smoothscale(mars_sprite, (26, 26))
    mars = CelestialBody(-1.524 * CelestialBody.AU, 0, 8, RED, 6.39 * 10**23, y_vel = 24.077 * 1000, tickrate=TICKRATE, sprite=mars_sprite)
    
    mercury_sprite = pygame.image.load(MERCURY_SPRITE)
    mercury_sprite = pygame.transform.smoothscale(mercury_sprite, (13, 13))
    mercury = CelestialBody(0.387 * CelestialBody.AU, 0, 5, DARK_GREY, 3.3 * 10**23, y_vel = -47.4 * 1000, tickrate=TICKRATE, sprite=mercury_sprite, cycle=88, starting_rotation=180)
    
    venus_sprite = pygame.image.load(VENUS_SPRITE)
    venus_sprite = pygame.transform.smoothscale(venus_sprite, (23, 23))
    venus = CelestialBody(0.723 * CelestialBody.AU, 0, 12, WHITE, 4.8685 * 10**24, y_vel = -35.02 * 1000, tickrate=TICKRATE, sprite=venus_sprite)
    
    return [sun, mercury, venus, earth, mars]

def main():
    run = True
    clock = pygame.time.Clock()
    bodies = create_solar_system()
    show_distance = show_elipse = use_sprites = True
    paused = False
    
    while run:
        clock.tick(TICKRATE)
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                elif event.key == pygame.K_t:
                    show_distance = 1 - show_distance
                elif event.key == pygame.K_e:
                    show_elipse = 1 - show_elipse
                elif event.key == pygame.K_r:
                    use_sprites = 1 - use_sprites
                elif event.key == pygame.K_SPACE:
                    paused = 1 - paused
            if event.type == pygame.QUIT:
                run = False

        WIN.fill(BLACK)
        for body in bodies:
            if not paused:
                body.update_positions(bodies)
            body.draw(WIN, show_distance=show_distance, show_elipse=show_elipse, use_sprites=use_sprites)

        pygame.display.update()
                
    pygame.quit()
    
if __name__ == '__main__':

    pygame.init()
    FONT = pygame.font.SysFont("comicsans", 11)
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Planet Simulation")

    main()