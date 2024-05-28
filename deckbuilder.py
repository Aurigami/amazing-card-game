import pygame
import os
import shutil

from constants import *
from general_functions import *
from Card import Card
from Zone import Zone

def main():
    # Create a new folder to store the deck
    current_directory = os.path.dirname(os.path.abspath(__file__))
    new_folder = "deck"
    full_path = os.path.join(current_directory, new_folder)
    os.makedirs(full_path, exist_ok=True)

    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    pygame.display.set_caption("Card Game: deckbuilder")

    # all_sprites_list = pygame.sprite.Group()

    # displayed cards
    card_list = pygame.sprite.Group()

    # card lists
    trunk_list = pygame.sprite.Group()
    deck_list = pygame.sprite.Group()
    # zones
    zone_list = pygame.sprite.Group()
    save_zone = Zone(GREY, 20, 20, 50, 50)
    save_zone.add(zone_list)

    # adding trunk zone and deck zone
    zone_main = Zone(TRUNK_COLOR, 0 , 94, SCREEN_WIDTH, SCREEN_HEIGHT-201)
    zone_list.add(zone_main)
    zone_trunk = Zone(TRUNK_COLOR, 0, SCREEN_HEIGHT-100, SCREEN_WIDTH/2-5, 100)
    zone_list.add(zone_trunk)
    zone_deck = Zone(DECK_COLOR_UNSELECTED, SCREEN_WIDTH/2+5, SCREEN_HEIGHT-100, SCREEN_WIDTH/2, 100)
    zone_list.add(zone_deck)

    # adding cards from the trunk at the right position
    for i in range(30):
        trunk_list.add(Card('fronts/'+ cardstr(i) +'.png', number = cardstr(i), deck_place = i))
    for card in trunk_list:
        card_list.add(card)

    clock = pygame.time.Clock()

    selected_zone = "trunk"
    running = True
    deck_cursor = 0
    click_cooldown = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Left mouse button down
                if event.button == 1:
                    # if we click on the trunk
                    if zone_trunk.rect.collidepoint(pygame.mouse.get_pos()):
                        selected_zone = "trunk"
                        # change colors of zones
                        zone_main.changeColor(TRUNK_COLOR)
                        zone_trunk.changeColor(TRUNK_COLOR)
                        zone_deck.changeColor(DECK_COLOR_UNSELECTED)
                        # add trunk cards to the displayed list of cards
                        card_list.empty()
                        for card in trunk_list:
                            card_list.add(card)
                    # if we click on the deck
                    elif zone_deck.rect.collidepoint(pygame.mouse.get_pos()):
                        selected_zone = "deck"
                        # change colors of zones
                        zone_main.changeColor(DECK_COLOR)
                        zone_trunk.changeColor(TRUNK_COLOR_UNSELECTED)
                        zone_deck.changeColor(DECK_COLOR)
                        # add deck cards to the displayed list of cards
                        card_list.empty()
                        for card in deck_list:
                            card_list.add(card)
                    # if we click on the save button
                    elif save_zone.rect.collidepoint(pygame.mouse.get_pos()):
                        i = 0
                        for card in deck_list:
                            shutil.copy(card.image_path, 'deck/' + cardstr(i) + '.png')
                            i += 1


                # Right mouse button up
                if event.button == 3:
                    pass

            for card in card_list:
                # if a card is clicked
                if card.isClicked(event):
                    # while being in the trunk
                    if selected_zone == "trunk":
                        # we add a copy of the card in the deck
                        deck_list.add(Card(card.image_path, deck_place = deck_cursor))
                        deck_cursor += 1
                    # while being in the deck
                    elif selected_zone == "deck" and click_cooldown == 0:
                        # we remove the card from the deck
                        deck_list.remove(card)
                        # replace the cards to fill the spot of the missing card
                        for other_card in deck_list:
                            if card.deck_place < other_card.deck_place:
                                other_card.deck_place -= 1
                                other_card.set_to_place(other_card.deck_place)
                        # preventing multiple events to trigger
                        click_cooldown = 4
                        # make it so the next card in the deck is added after the last current card
                        deck_cursor -= 1

                        # update the card in the screen
                        card_list.empty()
                        for card in deck_list:
                            card_list.add(card)

        screen.fill(BACKGROUND)

        zone_list.draw(screen)
        card_list.draw(screen)


        pygame.display.flip()

        # preventing multiple events to trigger
        if click_cooldown > 0:
            click_cooldown -= 1

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
