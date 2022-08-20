class GameMode:
    def __init__(self):
        self.max_player = 4        
        self.players = []
    def add(self):
        if len(self.players) < self.max_player:
            player = PlayerController()
            self.players.append(player)
            return player.id