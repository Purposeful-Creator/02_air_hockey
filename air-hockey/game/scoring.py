class Score:
    def __init__(self):
        self.player = 0
        self.computer = 0

    def add_point(self, scorer):          # "player" or "computer"
        if scorer == "player":
            self.player += 1
        else:
            self.computer += 1

    def result(self):                     # call at time-up
        if self.player > self.computer:
            return "player"
        if self.computer > self.player:
            return "computer"
        return "draw"