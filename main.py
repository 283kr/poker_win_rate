import random
from collections import Counter
import streamlit as st

class PokerOddsCalculator:
    def __init__(self, simulations=10000):
        self.simulations = simulations
        self.deck = ['2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', 'Th', 'Jh', 'Qh', 'Kh', 'Ah',
                    '2d', '3d', '4d', '5d', '6d', '7d', '8d', '9d', 'Td', 'Jd', 'Qd', 'Kd', 'Ad',
                    '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', 'Ts', 'Js', 'Qs', 'Ks', 'As',
                    '2c', '3c', '4c', '5c', '6c', '7c', '8c', '9c', 'Tc', 'Jc', 'Qc', 'Kc', 'Ac']
        self.value_order = "23456789TJQKA"
        self.value_ranks = {v: i for i, v in enumerate(self.value_order)}

    def calculate_odds(self, board_cards, n_cards):
        deck = list(self.deck)
        for card in board_cards:
            deck.remove(card)

        counts = {
            "no_hand": 0,
            "pair": 0,
            "two_pair": 0,
            "trips": 0,
            "straight": 0,
            "flush": 0,
            "full_house": 0,
            "four_of_a_kind": 0,
            "straight_flush": 0,
            "royal_flush": 0
        }

        for _ in range(self.simulations):
            sampled_deck = random.sample(deck, n_cards)
            current_hand = board_cards + sampled_deck
            hand_rank = self.evaluate_hand(current_hand)

            if hand_rank is None:
                counts["no_hand"] += 1
            else:
                counts[hand_rank] += 1

        odds = {k: (v / self.simulations) * 100 for k, v in counts.items()}
        return odds

    def evaluate_hand(self, hand):
        def is_straight(values):
            sorted_indices = sorted(set([self.value_ranks[v] for v in values]))
            if len(sorted_indices) < 5:
                return False
            for i in range(len(sorted_indices) - 4):
                if sorted_indices[i:i+5] == list(range(sorted_indices[i], sorted_indices[i]+5)):
                    return True
            return False

        def is_flush(suits):
            suit_counts = Counter(suits)
            for suit, count in suit_counts.items():
                if count >= 5:
                    return True
            return False

        def get_flush_suit(suits):
            suit_counts = Counter(suits)
            for suit, count in suit_counts.items():
                if count >= 5:
                    return suit
            return None

        def get_straight_flush(values, suits):
            flush_suit = get_flush_suit(suits)
            if flush_suit:
                flush_cards = [card[0] for card in hand if card[1] == flush_suit]
                if is_straight(flush_cards):
                    return True
            return False

        values = [card[0] for card in hand]
        suits = [card[1] for card in hand]
        multiples = Counter(values)

        straight = is_straight(values)
        flush = is_flush(suits)
        straight_flush = get_straight_flush(values, suits)

        if straight_flush:
            if set(values) >= set(self.value_order[-5:]):
                return "royal_flush"
            return "straight_flush"
        if 4 in multiples.values():
            return "four_of_a_kind"
        if 3 in multiples.values() and 2 in multiples.values():
            return "full_house"
        if flush:
            return "flush"
        if straight:
            return "straight"
        if 3 in multiples.values():
            return "trips"
        if list(multiples.values()).count(2) == 2:
            return "two_pair"
        if 2 in multiples.values():
            return "pair"

        return None

def card_emoji(card):
    value = card[0]
    suit = card[1]
    suits = {'h': '🧡', 'd': '♦️', 's': '♠️', 'c': '♣️'}
    return f"{value}{suits[suit]}"

# Streamlit App

st.title("Poker Odds Calculator")

poker_calculator = PokerOddsCalculator()

if 'selected_cards' not in st.session_state:
    st.session_state.selected_cards = []

if st.session_state.selected_cards:
    probabilities = poker_calculator.calculate_odds(st.session_state.selected_cards, 7 - len(st.session_state.selected_cards))
    st.subheader('Poker Odds:')
    col1, col2 = st.columns(2)
    with col1:
        for hand in list(probabilities.keys())[:5]:
            st.write(f"{hand.capitalize()}: {probabilities[hand]:.2f}%")
    with col2:
        for hand in list(probabilities.keys())[5:]:
            st.write(f"{hand.capitalize()}: {probabilities[hand]:.2f}%")
else:
    st.write("Please select cards to calculate odds.")

st.subheader('Select your cards (up to 7)')
cols = st.columns(13)
for i, card in enumerate(poker_calculator.deck):
    col = cols[i % 13]
    card_label = card_emoji(card)
    if card in st.session_state.selected_cards:
        if col.button(f"✅ {card_label}", key=f"remove_{card}", use_container_width=True):
            st.session_state.selected_cards.remove(card)
            st.experimental_rerun()
    else:
        if col.button(card_label, key=f"add_{card}", use_container_width=True):
            if len(st.session_state.selected_cards) < 7:
                st.session_state.selected_cards.append(card)
                st.experimental_rerun()
            else:
                st.warning("You can only select up to 7 cards.")

if st.button('Reset'):
    st.session_state.selected_cards = []
    st.experimental_rerun()
