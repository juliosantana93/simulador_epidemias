import pygame
import sys

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("cancion_pandemia.mp3")  # Asegúrate del nombre correcto
pygame.mixer.music.play(-1)  # -1 = bucle infinito

# Pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulación de Pandemia")

# Colores y fuentes
WHITE = (255, 255, 255)
DARK_BLUE = (10, 10, 50)
LIGHT_BLUE = (50, 150, 255)
HOVER_BLUE = (30, 130, 230)
FONT_TITLE = pygame.font.SysFont("Arial", 48, bold=True)
FONT_MENU = pygame.font.SysFont("Arial", 30)

# Fondo con imagen
background_img = pygame.image.load("fondo_pandemia.png")
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

# Clase de botón
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

        text_surf = FONT_MENU.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# Función del menú principal
def main_menu():
    start_button = Button("Iniciar Simulación", WIDTH // 2 - 150, HEIGHT // 2 - 30, 300, 50, LIGHT_BLUE, HOVER_BLUE)
    exit_button = Button("Salir", WIDTH // 2 - 150, HEIGHT // 2 + 40, 300, 50, (200, 70, 70), (170, 40, 40))

    while True:
        screen.blit(background_img, (0, 0))  # Fondo con imagen

        # Sombra suave para el título
        title_surf = FONT_TITLE.render("Simulación de Pandemia", True, WHITE)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        pygame.draw.rect(screen, (0, 0, 0, 90), title_rect.inflate(30, 10), border_radius=12)
        screen.blit(title_surf, title_rect)

        # Botones
        start_button.draw(screen)
        exit_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if start_button.is_clicked(event):
                input_parameters()

            if exit_button.is_clicked(event):
                pygame.quit()
                sys.exit()

        pygame.display.flip()

# Función temporal para el input
from input_screen import input_parameters

# Ejecutar menú
main_menu()
