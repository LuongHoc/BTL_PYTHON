import tkinter as tk
from tkinter import messagebox
import random
from PIL import Image, ImageTk
import os
import pygame
import asyncio
import platform
import numpy as np

class BJ_Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = self._get_value()

    def _get_value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11
        return int(self.rank)

    def __str__(self):
        return f"{self.rank} of {self.suit}"

    def get_image_path(self):
        suit_map = {
            'Hearts': 'Heart',
            'Diamonds': 'Diamond',
            'Clubs': 'Clover',
            'Spades': 'Spades'
        }
        folder = suit_map[self.suit]
        return os.path.join(r"D:\Blackjack\Resources\Cards", folder, f"{self.rank}.png")

class BJ_Deck:
    def __init__(self):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [BJ_Card(suit, rank) for suit in suits for rank in ranks]
        random.shuffle(self.cards)

    def deal(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        return None

class BJ_Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_value(self):
        value = 0
        aces = 0
        for card in self.cards:
            value += card.value
            if card.rank == 'A':
                aces += 1
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        return value

    def clear(self):
        self.cards = []

    def __str__(self):
        return ", ".join(str(card) for card in self.cards)

class BJ_Game:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="#2e8b57")
        self.deck = BJ_Deck()
        self.player_hand = BJ_Hand()
        self.dealer_hand = BJ_Hand()
        self.card_images = {}
        self.card_labels = {'player': [], 'dealer': []}
        self.back_image = None
        pygame.mixer.init()
        self.sounds = {
            'hit': pygame.mixer.Sound(os.path.join(r"D:\Blackjack\Resources\Sounds", "hit_sound.mp3")),
            'win': pygame.mixer.Sound(os.path.join(r"D:\Blackjack\Resources\Sounds", "win_sound.mp3")),
            'lose': pygame.mixer.Sound(os.path.join(r"D:\Blackjack\Resources\Sounds", "lose_sound.mp3")),
            'tie': pygame.mixer.Sound(os.path.join(r"D:\Blackjack\Resources\Sounds", "tie_sound.mp3"))
        }
        self.setup_gui()
        self.start_new_game()

    def load_card_image(self, card):
        if card not in self.card_images:
            try:
                image = Image.open(card.get_image_path())
                image = image.resize((70, 100), Image.LANCZOS)
                self.card_images[card] = ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Error loading image for {card}: {e}")
                return None
        return self.card_images[card]

    def load_back_image(self):
        if self.back_image is None:
            try:
                back_path = os.path.join(r"D:\Blackjack\Resources\Cards\Back", "red_design_back.png")
                if not os.path.exists(back_path):
                    print(f"Back card image not found: {back_path}")
                    return None
                image = Image.open(back_path)
                image = image.resize((70, 100), Image.LANCZOS)
                self.back_image = ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Error loading back image: {e}")
                return None
        return self.back_image

    def setup_gui(self):
        # Player frame
        self.player_frame = tk.Frame(self.root, bg="#2e8b57")
        self.player_frame.pack(pady=20)
        self.player_label = tk.Label(self.player_frame, text="Player's Hand", font=("Arial", 14, "bold"), bg="#2e8b57", fg="white")
        self.player_label.pack()
        self.player_cards_frame = tk.Frame(self.player_frame, bg="#2e8b57")
        self.player_cards_frame.pack()
        self.player_score_label = tk.Label(self.player_frame, text="Score: 0", font=("Arial", 12), bg="#2e8b57", fg="white")
        self.player_score_label.pack()

        # Dealer frame
        self.dealer_frame = tk.Frame(self.root, bg="#2e8b57")
        self.dealer_frame.pack(pady=20)
        self.dealer_label = tk.Label(self.dealer_frame, text="Dealer's Hand", font=("Arial", 14, "bold"), bg="#2e8b57", fg="white")
        self.dealer_label.pack()
        self.dealer_cards_frame = tk.Frame(self.dealer_frame, bg="#2e8b57")
        self.dealer_cards_frame.pack()
        self.dealer_score_label = tk.Label(self.dealer_frame, text="Score: 0", font=("Arial", 12), bg="#2e8b57", fg="white")
        self.dealer_score_label.pack()

        # Buttons
        self.button_frame = tk.Frame(self.root, bg="#2e8b57")
        self.button_frame.pack(pady=20)
        self.hit_button = tk.Button(self.button_frame, text="Hit", command=self.hit, font=("Arial", 12), bg="#4682b4", fg="white")
        self.hit_button.pack(side=tk.LEFT, padx=10)
        self.stand_button = tk.Button(self.button_frame, text="Stand", command=self.stand, font=("Arial", 12), bg="#4682b4", fg="white")
        self.stand_button.pack(side=tk.LEFT, padx=10)
        self.new_game_button = tk.Button(self.button_frame, text="New Game", command=self.start_new_game, font=("Arial", 12), bg="#4682b4", fg="white")
        self.new_game_button.pack(side=tk.LEFT, padx=10)

        # Result label
        self.result_label = tk.Label(self.root, text="", font=("Arial", 14, "bold"), bg="#2e8b57", fg="yellow")
        self.result_label.pack(pady=10)

    def start_new_game(self):
        self.deck = BJ_Deck()
        self.player_hand.clear()
        self.dealer_hand.clear()
        self.result_label.config(text="")
        self.hit_button.config(state=tk.NORMAL)
        self.stand_button.config(state=tk.NORMAL)

        # Clear card labels
        for label in self.card_labels['player']:
            label.destroy()
        for label in self.card_labels['dealer']:
            label.destroy()
        self.card_labels['player'] = []
        self.card_labels['dealer'] = []

        # Deal initial cards
        self.player_hand.add_card(self.deck.deal())
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())

        # Check for dealer blackjack
        dealer_upcard = self.dealer_hand.cards[0]
        if dealer_upcard.value == 10 or dealer_upcard.rank == 'A':
            if self.dealer_hand.get_value() == 21:
                self.show_result("Dealer Blackjack! You lose!")
                self.hit_button.config(state=tk.DISABLED)
                self.stand_button.config(state=tk.DISABLED)
                self.update_gui()
                return

        # Check for player blackjack
        if self.player_hand.get_value() == 21:
            self.show_result("Blackjack! You win!")
            self.hit_button.config(state=tk.DISABLED)
            self.stand_button.config(state=tk.DISABLED)

        self.update_gui()

    def hit(self):
        self.sounds['hit'].play()
        self.player_hand.add_card(self.deck.deal())
        self.update_gui()
        if self.player_hand.get_value() > 21:
            self.show_result("Bust! You lose!")
            self.hit_button.config(state=tk.DISABLED)
            self.stand_button.config(state=tk.DISABLED)

    def stand(self):
        self.hit_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)

        # Dealer's turn
        while self.dealer_hand.get_value() < 17:
            self.dealer_hand.add_card(self.deck.deal())
        self.update_gui()

        # Determine winner
        player_score = self.player_hand.get_value()
        dealer_score = self.dealer_hand.get_value()

        if dealer_score > 21:
            self.show_result("Dealer busts! You win!")
        elif player_score > dealer_score:
            self.show_result("You win!")
        elif dealer_score > player_score:
            self.show_result("Dealer wins!")
        else:
            self.show_result("It's a tie!")

    def update_gui(self):
        # Clear existing card labels
        for label in self.card_labels['player']:
            label.destroy()
        for label in self.card_labels['dealer']:
            label.destroy()
        self.card_labels['player'] = []
        self.card_labels['dealer'] = []

        # Update player cards
        for card in self.player_hand.cards:
            img = self.load_card_image(card)
            if img:
                label = tk.Label(self.player_cards_frame, image=img, bg="#2e8b57")
                label.image = img
                label.pack(side=tk.LEFT, padx=5)
                self.card_labels['player'].append(label)
        self.player_score_label.config(text=f"Score: {self.player_hand.get_value()}")

        # Update dealer cards
        if self.hit_button.cget("state") == tk.NORMAL:
            card = self.dealer_hand.cards[0]
            img = self.load_card_image(card)
            if img:
                label = tk.Label(self.dealer_cards_frame, image=img, bg="#2e8b57")
                label.image = img
                label.pack(side=tk.LEFT, padx=5)
                self.card_labels['dealer'].append(label)
            back_img = self.load_back_image()
            if back_img:
                label = tk.Label(self.dealer_cards_frame, image=back_img, bg="#2e8b57")
                label.image = back_img
                label.pack(side=tk.LEFT, padx=5)
                self.card_labels['dealer'].append(label)
            self.dealer_score_label.config(text=f"Score: {self.dealer_hand.cards[0].value}")
        else:
            for card in self.dealer_hand.cards:
                img = self.load_card_image(card)
                if img:
                    label = tk.Label(self.dealer_cards_frame, image=img, bg="#2e8b57")
                    label.image = img
                    label.pack(side=tk.LEFT, padx=5)
                    self.card_labels['dealer'].append(label)
            self.dealer_score_label.config(text=f"Score: {self.dealer_hand.get_value()}")

    def show_result(self, message):
        if "win" in message.lower() or "busts" in message.lower():
            self.sounds['win'].play()
        elif "lose" in message.lower() or "bust" in message.lower():
            self.sounds['lose'].play()
        elif "tie" in message.lower():
            self.sounds['tie'].play()
        self.result_label.config(text=message)
        messagebox.showinfo("Game Result", message)

async def main():
    setup()  # Initialize pygame game
    while True:
        update_loop()  # Update game/visualization state
        await asyncio.sleep(1.0 / 60)  # Control frame rate at 60 FPS

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        pygame.init()
        root = tk.Tk()
        root.title("Blackjack Game")
        root.geometry("800x600")
        game = BJ_Game(root)
        root.mainloop()