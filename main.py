import pygame

from config import HEIGHT
from config import WIDTH
from game import Game


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Gorilla Shootout")
    clock = pygame.time.Clock()

    game = Game()

    game.render(screen)
    pygame.display.flip()

    while True:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYUP:
                game.on_key_up(event.key, event.mod)
            if event.type == pygame.MOUSEBUTTONDOWN:
                game.on_mouse_down(event.pos, event.button)
            if event.type == pygame.MOUSEBUTTONUP:
                game.on_mouse_up(event.pos, event.button)
            if event.type == pygame.MOUSEMOTION:
                game.on_mouse_move(event.pos, event.rel, event.buttons)

        game.update(dt)

        game.render(screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()
