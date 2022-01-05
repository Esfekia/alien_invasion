class GameStats:
	"""Tracks statistics for Alien Invason."""

	def __init__(self, ai_game):
		"""Initialize statistics."""
		self.settings = ai_game.settings
		self.reset_stats()
		# Start Alien Invasion in an inactive state.
		self.game_active = False

	def reset_stats(self):
		"""Initialize statistics that can change during the game."""
		self.ships_left = self.settings.ship_limit
		self.score =0
		self.settings.ship_speed = 0.5
		self.settings.bullet_speed = 2.0
		self.settings.alien_speed = 0.5
		self.settings.alien_points = 50

		