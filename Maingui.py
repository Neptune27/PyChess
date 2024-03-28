import pygame
import pygame_gui
from pygame_gui import UIManager

pygame.init()

pygame.display.set_caption('Pygame Chat')
window_surface = pygame.display.set_mode((800, 660))
manager = UIManager((800, 700), '../data/themes/chat.json')

background = pygame.Surface((800, 700))
background.fill(manager.ui_theme.get_colour('dark_bg'))

clock = pygame.time.Clock()
is_running = True


while is_running:
    time_delta = clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
            exit()

        manager.process_events(event)


    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    pygame.display.update()