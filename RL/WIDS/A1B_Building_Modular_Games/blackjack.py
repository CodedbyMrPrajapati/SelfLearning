import cards
class BlackJack:
    def __init__(self):
        self.deck = cards.Deck()
        self.player = cards.Hand()
        self.dealer = cards.Hand()
        self.game_over = False
        self.result = None
    def start_round(self):
        self.deck.reset()
        self.deck.shuffle()
        self.player.flush()
        self.dealer.flush()
        self.game_over = False
        self.result = None
        for _ in range(2):
            self.player.add_card(self.deck.draw())
            self.dealer.add_card(self.deck.draw())
    def hit(self):
        if self.game_over:
            return
        self.player.add_card(self.deck.draw())
        if self.player.value() > 21:
            self.game_over = True
            self.result = "dealer"
    def stand(self):
        if self.game_over:return
        while self.dealer.value() < 17:
            self.dealer.add_card(self.deck.draw())

        if self.dealer.value() > 21:
            self.result = "player"
        else:
            pv = self.player.value()
            dv = self.dealer.value()

            if pv > dv:
                self.result = "player"
            elif dv > pv:
                self.result = "dealer"
            else:
                self.result = "push"

        self.game_over = True
    def run_match(self, policy):
        """
        policy(hand_value) -> 'hit' or 'stand'
        """
        self.start_round()

        while not self.game_over:
            action = policy(self.player.value())
            if action == "hit":
                self.hit()
            else:
                self.stand()

        return self.result
    
def simple_policy(hand_value):
    return "hit" if hand_value < 17 else "stand"

