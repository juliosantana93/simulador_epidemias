import pygame
import sys

pygame.init()

# Configuración pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ingresar Parámetros")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BLUE = (50, 150, 255)
HOVER_BLUE = (30, 130, 230)
DARK_GRAY = (50, 50, 50)
RED = (200, 70, 70)
HOVER_RED = (170, 40, 40)

# Fuentes
FONT = pygame.font.SysFont("Comic Sans MS", 30, bold=True)
FONT_TITLE = pygame.font.SysFont("Comic Sans MS", 40, bold=True)

# Fondo
background_img = pygame.image.load("mapa_pandemia.png")
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

# InputBox
class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = DARK_GRAY
        self.text = text
        self.txt_surface = FONT.render(text, True, WHITE)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < 6:
                    self.text += event.unicode
            self.txt_surface = FONT.render(self.text, True, WHITE)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
        screen.blit(self.txt_surface, (self.rect.x + 10, self.rect.y + 5))

    def get_value(self, cast_type=int):
        try:
            return cast_type(self.text)
        except:
            return None

# Botón
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
        pygame.draw.rect(surface, color, self.rect, border_radius=12)

        text_surf = FONT.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# Pantalla de entrada de variables
def input_parameters():
    input_boxes = {
        "Susceptibles": InputBox(400, 120, 120, 40),
        "Infectados": InputBox(400, 180, 120, 40),
        "Cuarentena": InputBox(400, 240, 120, 40),
        "Ciclos destino": InputBox(400, 300, 120, 40),
        "Mortalidad (%)": InputBox(400, 360, 120, 40),
    }

    start_button = Button("Iniciar Simulación", WIDTH // 2 - 150, HEIGHT - 80, 300, 50, LIGHT_BLUE, HOVER_BLUE)
    clock = pygame.time.Clock()

    while True:
        screen.blit(background_img, (0, 0))

        # Título con sombra
        title_shadow = FONT_TITLE.render("Configuración de Simulación", True, BLACK)
        screen.blit(title_shadow, (WIDTH // 2 - 250 + 2, 30 + 2))
        title = FONT_TITLE.render("Configuración de Simulación", True, WHITE)
        screen.blit(title, (WIDTH // 2 - 250, 30))

        # Campos con sombra en el label
        y_offset = 120
        for label, box in input_boxes.items():
            shadow = FONT.render(label + ":", True, BLACK)
            screen.blit(shadow, (150 + 2, y_offset + 2))

            text = FONT.render(label + ":", True, WHITE)
            screen.blit(text, (150, y_offset))
            box.draw(screen)
            y_offset += 60

        # Botón
        start_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            for box in input_boxes.values():
                box.handle_event(event)

            if start_button.is_clicked(event):
                try:
                    values = {
                        "n_susceptible": input_boxes["Susceptibles"].get_value(int),
                        "n_infected": input_boxes["Infectados"].get_value(int),
                        "n_quarantined": input_boxes["Cuarentena"].get_value(int),
                        "cycles_to_fate": input_boxes["Ciclos destino"].get_value(int),
                        "mortality_rate": input_boxes["Mortalidad (%)"].get_value(float) / 100,
                    }

                    # Validación básica
                    if None in values.values():
                        raise ValueError("Valores inválidos")

                    print("Variables configuradas:", values)

                    from simulador import Simulation
                    sim = Simulation(800, 600)
                    sim.n_susceptible = values["n_susceptible"]
                    sim.n_infected = values["n_infected"]
                    sim.n_quarantined = values["n_quarantined"]
                    sim.cycles_to_fate = values["cycles_to_fate"]
                    sim.mortality_rate = values["mortality_rate"]
                    sim.start(randomize=True)
                    return

                except Exception as e:
                    print("Error:", e)

        pygame.display.flip()
        clock.tick(30)
