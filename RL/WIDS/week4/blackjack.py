import cards
class BlackJack:
    def __init__(self):
        self.deck = cards.Deck()
        self.player = cards.Hand()
        self.dealer = cards.Hand()
        self.game_over = False
    def reset(self):
        return self.start_round()
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
        return self._get_state()
    def usable_ace(self,hand):
        total = 0
        aces = 0
        for c in hand.cards:
            if c.rank == 1:
                aces += 1
                total += 11
            else:
                total += min(c.rank, 10)
        if total > 21 and aces > 0:
            total -= 10
        return aces > 0 and total <= 21
    def _get_state(self):
        return (
            self.player.value(),
            self.dealer.cards[0].rank,
            self.usable_ace(self.player)
        )
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
    def step(self,action):
        if self.game_over:
            raise RuntimeError("Episode already finished")

        if action == 0:
            self.hit()
            if self.game_over:
                return self._get_state(), -1, True
            return self._get_state(), 0, False
        else:
            self.stand()
            if self.result == "player":
                return self._get_state(), +1, True
            elif self.result == "dealer":
                return self._get_state(), -1, True
            else:
                return self._get_state(), 0, True

print("Here")