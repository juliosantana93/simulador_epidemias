import pygame
import sys
import numpy as np

# Inicializar pygame antes de usar fuentes
pygame.init()
pygame.font.init()

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
GREEN = (50, 150, 50)
PURPLE = (130, 0, 130)
GREY = (230, 230, 230)
YELLOW = (190, 175, 50)
DARK_GREY = (40, 40, 40)
RED = (180, 30, 30)
BUTTON_BLUE = (50, 120, 220)
BUTTON_HOVER = (30, 100, 200)

BACKGROUND = WHITE

# Fuentes
FONT = pygame.font.SysFont("Arial", 20)
BIGFONT = pygame.font.SysFont("Arial", 26, bold=True)


class Button:
    def __init__(self, text, x, y, w, h, base_color, hover_color, action=None):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.base_color = base_color
        self.hover_color = hover_color
        self.action = action

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        color = self.hover_color if is_hovered else self.base_color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)

        text_surf = FONT.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


class Dot(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=BLACK, radius=5, velocity=[0, 0], randomize=False):
        super().__init__()
        self.image = pygame.Surface([radius * 2, radius * 2], pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect()
        self.pos = np.array([x, y], dtype=np.float64)
        self.vel = np.asarray(velocity, dtype=np.float64)
        self.killswitch_on = False
        self.recovered = False
        self.randomize = randomize
        self.WIDTH = width
        self.HEIGHT = height

    def update(self):
        self.pos += self.vel
        x, y = self.pos

        # Bordes periódicos
        if x < 0: self.pos[0] = self.WIDTH
        if x > self.WIDTH: self.pos[0] = 0
        if y < 0: self.pos[1] = self.HEIGHT
        if y > self.HEIGHT: self.pos[1] = 0

        self.rect.x = int(self.pos[0])
        self.rect.y = int(self.pos[1])

        vel_norm = np.linalg.norm(self.vel)
        if vel_norm > 3:
            self.vel /= vel_norm

        if self.randomize:
            self.vel += np.random.rand(2) * 2 - 1

        if self.killswitch_on:
            self.cycles_to_fate -= 1
            if self.cycles_to_fate <= 0:
                self.killswitch_on = False
                if np.random.rand() < self.mortality_rate:
                    self.kill()
                else:
                    self.recovered = True

    def respawn(self, color, radius=5):
        return Dot(self.rect.x, self.rect.y, self.WIDTH, self.HEIGHT, color=color, velocity=self.vel)

    def killswitch(self, cycles_to_fate=20, mortality_rate=0.2):
        self.killswitch_on = True
        self.cycles_to_fate = cycles_to_fate
        self.mortality_rate = mortality_rate


class Simulation:
    def __init__(self, width=800, height=600):
        self.WIDTH = width
        self.HEIGHT = height
        self.sim_area = height - 120  # Área útil para dots

        self.susceptible_container = pygame.sprite.Group()
        self.infected_container = pygame.sprite.Group()
        self.recovered_container = pygame.sprite.Group()
        self.all_container = pygame.sprite.Group()

        self.n_susceptible = 100
        self.n_infected = 5
        self.n_quarantined = 0
        self.T = 1000
        self.cycles_to_fate = 200
        self.mortality_rate = 0.2
        self.paused = False

    def start(self, randomize=False):
        self.N = self.n_susceptible + self.n_infected + self.n_quarantined
        screen = pygame.display.set_mode([self.WIDTH, self.HEIGHT])
        clock = pygame.time.Clock()

        # Crear dots
        for _ in range(self.n_susceptible):
            guy = Dot(np.random.randint(self.WIDTH), np.random.randint(self.sim_area), self.WIDTH, self.sim_area,
                      color=BLUE, velocity=np.random.rand(2) * 2 - 1, randomize=randomize)
            self.susceptible_container.add(guy)
            self.all_container.add(guy)

        for _ in range(self.n_quarantined):
            guy = Dot(np.random.randint(self.WIDTH), np.random.randint(self.sim_area), self.WIDTH, self.sim_area,
                      color=BLUE, velocity=[0, 0])
            self.susceptible_container.add(guy)
            self.all_container.add(guy)

        for _ in range(self.n_infected):
            guy = Dot(np.random.randint(self.WIDTH), np.random.randint(self.sim_area), self.WIDTH, self.sim_area,
                      color=GREEN, velocity=np.random.rand(2) * 2 - 1, randomize=randomize)
            self.infected_container.add(guy)
            self.all_container.add(guy)

        # Estadísticas
        stats = pygame.Surface((self.WIDTH, 100))
        stats.set_alpha(230)
        stats.fill(GREY)

        # Botones
        pause_btn = Button("⏸ Pausar", 20, 10, 120, 40, BUTTON_BLUE, BUTTON_HOVER)
        menu_btn = Button("← Menú", 660, 10, 120, 40, RED, (150, 0, 0))

        for i in range(self.T):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if pause_btn.is_clicked(event):
                    self.paused = not self.paused
                    pause_btn.text = "▶ Reanudar" if self.paused else "⏸ Pausar"
                if menu_btn.is_clicked(event):
                    from main_menu import main_menu
                    main_menu()

            if not self.paused:
                self.all_container.update()

            screen.fill(WHITE)

            # Dibujar simulación
            self.all_container.draw(screen)

            # Dibujar gráfico de estadísticas
            stats.fill(DARK_GREY)
            t = int((i / self.T) * self.WIDTH)
            n_inf = len(self.infected_container)
            n_pop = len(self.all_container)
            n_rec = len(self.recovered_container)
            y_inf = int((1 - n_inf / self.N) * 100)
            y_dead = int(((self.N - n_pop) / self.N) * 100)
            y_rec = int((1 - n_rec / self.N) * 100)

            graph = pygame.PixelArray(stats)
            if t < self.WIDTH:
                graph[t, y_inf:] = pygame.Color(*GREEN)
                graph[t, :y_dead] = pygame.Color(*YELLOW)
                graph[t, y_dead:y_dead + (100 - y_rec)] = pygame.Color(*PURPLE)
            del graph
            stats.unlock()

            # Encabezado HUD
            pygame.draw.rect(screen, (30, 30, 30), (0, 0, self.WIDTH, 60))
            pause_btn.draw(screen)
            menu_btn.draw(screen)

            # Agregar info
            info_text = BIGFONT.render(f"Infectados: {n_inf}   |   Recuperados: {n_rec}   |   Muertos: {self.N - n_pop}", True, WHITE)
            screen.blit(info_text, (self.WIDTH // 2 - info_text.get_width() // 2, 15))

            # Dibujar gráfico al final
            screen.blit(stats, (0, self.HEIGHT - 100))
            pygame.display.flip()
            clock.tick(30)

        pygame.quit()
