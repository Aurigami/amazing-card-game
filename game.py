import pygame
import sys
import random
import socket
import threading
import queue

from Card import Card
from constants import *
from general_functions import *

def print_amount_cards(own_deck, other_deck):
    print("own deck :")
    print(len(own_deck))
    print("other deck :")
    print(len(other_deck))

def main():
    # Console menu
    print("Game Menu:")
    print("1. Host")
    print("2. Connect")
    print("3. Quit")
    gamemode = "none"
    choice = input("Enter your choice: ")
    if choice == "1":
        gamemode = "host"
    elif choice == "2":
        gamemode = "client"
    else:
        return

    # defining the ip and port of the host
    if gamemode == "host":
        ip = input("Entrez votre adresse IP: ")
    elif gamemode == "client":
        ip = input("Enter the IP adress of the host: ")
    port = 5555
    host_address = (ip, port)
    # making sockets to send stuff
    own_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=0, fileno=None)
    own_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # and sending the first message to give the host the client's address
    if gamemode == "host":
        own_socket.bind(("0.0.0.0", port))
        # wait for first messages to get the client's ip
        msg, client_address = own_socket.recvfrom(1024)
        # the address to speak with
        other_address = client_address
    elif gamemode == "client":
        # Send a message to establish the connection
        msg = "Connection requested"
        own_socket.sendto(msg.encode(), host_address)
        # the address to speak with
        other_address = host_address


    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    pygame.display.set_caption("Card Game: " + gamemode)

    all_sprites_list = pygame.sprite.Group()

    card_list = pygame.sprite.Group()
    deck_list_own = pygame.sprite.Group()
    deck_list_other = pygame.sprite.Group()

    sprite_change = False

    # the host shuffles the cards
    # and send the order to the client
    if gamemode == "host":
        for i in range(30):
            deck_list_own.add(Card('deck1/'+ cardstr(i) +'.png', 30*i, 800, cardstr(i)))
            deck_list_other.add(Card('deck2/'+ cardstr(i) +'.png', 30*i, 0, str(i+50)))

        # Shuffle the card group
        deck_list_host_temp = list(deck_list_own.sprites())
        deck_list_client_temp = list(deck_list_other.sprites())
        random.shuffle(deck_list_host_temp)
        random.shuffle(deck_list_client_temp)

        # Clear the card group
        deck_list_own.empty()
        deck_list_other.empty()

        # Re-add the card in shuffled order
        for card in deck_list_host_temp:
            deck_list_own.add(card)
        for card in deck_list_client_temp:
            deck_list_other.add(card)

        # list of the order of the cards, to send to the client
        host_number_order = []
        client_number_order = []
        for card in deck_list_own:
            host_number_order.append(card.number)
        for card in deck_list_other:
            client_number_order.append(card.number)
        # sending the order of the cards to the client
        # order of the host's deck
        own_socket.sendto(b''.join(s.encode() for s in host_number_order), other_address)
        # order of the client's deck
        own_socket.sendto(b''.join(s.encode() for s in client_number_order), other_address)

    elif gamemode == "client":
        # order of the host's deck
        host_number_order_raw, sa = own_socket.recvfrom(1024)
        # order of the client's deck
        client_number_order_raw, sa = own_socket.recvfrom(1024)

        # decoding the bytes
        host_number_order_raw = host_number_order_raw.decode()
        client_number_order_raw = client_number_order_raw.decode()

        # split the string into pairs of 2 characters
        host_number_order = [host_number_order_raw[i:i+2] for i in range(0, len(host_number_order_raw), 2)]
        client_number_order = [client_number_order_raw[i:i+2] for i in range(0, len(client_number_order_raw), 2)]
        for i in host_number_order:
            deck_list_other.add(Card('deck1/' + i +'.png', 30*int(i), 0, i))
        for i in client_number_order:
            j = int(i) - 50
            deck_list_own.add(Card('deck2/' + cardstr(j) +'.png', 30*j, 800, i))


    # A queue to process the actions of the other player
    action_queue = queue.Queue()

    # listening the actions of the other player
    def listen_actions(action_queue, socket_passed, address_passed):
        while True:
            # receive a message and store it
            msg, address_passed = socket_passed.recvfrom(1024)
            action_queue.put(msg.decode())
    # the thread to receive the actions of the other player
    receiving_thread = threading.Thread(target=listen_actions, args=(action_queue, own_socket, other_address), daemon=True)
    receiving_thread.start()



    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                # Right mouse button up & condition to prevent drawing the last card
                if event.button == 3 and len(deck_list_own) > 0:
                    msg_card_draw = "draw".encode()
                    # draw a card
                    card = deck_list_own.sprites()[0]
                    deck_list_own.remove(card)
                    # send the update to the other player
                    own_socket.sendto(msg_card_draw, other_address)

                    # display amount of cards in deck of each player
                    print_amount_cards(deck_list_own, deck_list_other)

                    card_list.add(card)
                    sprite_change = True
            for sprite in all_sprites_list:
                if isinstance(sprite, Card):  # Only handle events for cards
                    sprite.handle_event(event)
                    # if the sprite is being moved, we send the update to the other player
                    if sprite.dragging:
                        card_info = sprite.number + " " + str(sprite.rect.x) + " " + str(sprite.rect.y)
                        own_socket.sendto(card_info.encode(), other_address)

        queue_not_empty = True
        last_action_position = []
        # a list of actions to do
        while queue_not_empty:
            try:
                action = action_queue.get(block=False)
            except queue.Empty:
                queue_not_empty = False
            else:
                # draw a card for the other player
                if action == "draw":
                    card = deck_list_other.sprites()[0]
                    deck_list_other.remove(card)
                    card_list.add(card)
                    sprite_change = True

                    # display amount of cards in deck of each player
                    print_amount_cards(deck_list_own, deck_list_other)
                else:
                    last_action_position = action.split()

        # changing the card position according to the last position known
        if last_action_position != []:
            for card in card_list:
                if card.number == last_action_position[0]:
                    card.rect.x = int(last_action_position[1])
                    card.rect.y = SCREEN_HEIGHT -CARD_HEIGHT -int(last_action_position[2])

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
