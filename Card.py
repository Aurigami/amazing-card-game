import pygame
from constants import *

class Card(pygame.sprite.Sprite):
    def __init__(self, image_path, x=0, y=0, number="00", *, deck_place=-1):
        super().__init__()
        self.image_path = image_path
        self.image = pygame.image.load(image_path).convert()

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.dragging = False
        self.draggingMouseDistanceX = 0
        self.draggingMouseDistanceY = 0

        # adding a card number to help communication between client and server
        self.number = number

        self.deck_place = deck_place

        if deck_place >= 0:
            self.set_to_place(deck_place)

    def update(self):
        if self.dragging:
            pos = pygame.mouse.get_pos()
            self.rect.x = pos[0] - self.draggingMouseDistanceX
            self.rect.y = pos[1] - self.draggingMouseDistanceY

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.dragging = True
                self.draggingMouseDistanceX = pygame.mouse.get_pos()[0] - self.rect.x
                self.draggingMouseDistanceY = pygame.mouse.get_pos()[1] - self.rect.y
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

    def isClicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def set_to_place(self, place):
        self.rect.x = 10 + (CARD_WIDTH + SEPARATOR_HORIZONTAL)*place - 10*(CARD_WIDTH + SEPARATOR_HORIZONTAL)*(place//10)
        self.rect.y = 105 + (CARD_HEIGHT + SEPARATOR_VERTICAL)*(place//10)
