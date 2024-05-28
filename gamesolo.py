import pygame
import random

# Define the background color
BACKGROUND = (40, 44, 52)

class Card(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y):
        super().__init__()
        self.image = pygame.image.load(image_path).convert()

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.dragging = False
        self.draggingMouseDistanceX = 0
        self.draggingMouseDistanceY = 0

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

def print_amount_cards(deck1, deck2):
    print("top deck:")
    print(len(deck1))
    print("bottom deck")
    print(len(deck2))

def main():
    pygame.init()

    # Set the width and height of the screen [width, height]
    screen_width = 1920
    screen_height = 1080
    screen = pygame.display.set_mode((screen_width, screen_height))

    pygame.display.set_caption("Card Game")

    all_sprites_list = pygame.sprite.Group()

    card_list = pygame.sprite.Group()
    deck_list_1 = pygame.sprite.Group()
    deck_list_2 = pygame.sprite.Group()
    for i in range(30):
        prefix = ''
        if i < 10:
            prefix = '0'
        deck_list_1.add(Card('deck1/'+ prefix + str(i) +'.png', 30*i, 0))
        deck_list_2.add(Card('deck2/'+ prefix + str(i) +'.png', 30*i, 800))

    # Shuffle the card group
    deck_list_1_temp = list(deck_list_1.sprites())
    deck_list_2_temp = list(deck_list_2.sprites())
    random.shuffle(deck_list_1_temp)
    random.shuffle(deck_list_2_temp)

    # Clear the card group
    deck_list_1.empty()
    deck_list_2.empty()

    # Re-add the card in shuffled order
    for card in deck_list_1_temp:
        deck_list_1.add(card)
    for card in deck_list_2_temp:
        deck_list_2.add(card)

    sprite_change = False

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                # Right mouse button up
                if event.button == 3:
                    if pygame.mouse.get_pos()[1] < 540:
                        card = deck_list_1.sprites()[0]
                        deck_list_1.remove(card)
                    else:
                        card = deck_list_2.sprites()[0]
                        deck_list_2.remove(card)

                    card_list.add(card)
                    sprite_change = True

                    # print amount of cards in the deck
                    print_amount_cards(deck_list_1, deck_list_2)
            for sprite in all_sprites_list:
                if isinstance(sprite, Card):  # Only handle events for cards
                    sprite.handle_event(event)

        if sprite_change:
            all_sprites_list.empty()
            for card in card_list:
                all_sprites_list.add(card)

        all_sprites_list.update()

        screen.fill(BACKGROUND)

        all_sprites_list.draw(screen)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
