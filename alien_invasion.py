import sys
from time import sleep
import pygame

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button1 import Button1
from button2 import Button2
from game_stats import GameStats
from scoreboard import Scoreboard

class AlienInvasion:
	"""Overall class to manage game assets and behavior."""

	def __init__(self):
		"""Initialize the game and create game resources."""

		pygame.init()

		self.settings = Settings()

		self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
		self.settings.screen_width = self.screen.get_rect().width
		self.settings.screen_height = self.screen.get_rect().height
		pygame.display.set_caption("Alien Invasion")

		#Create an instance to store game statistics.
		#and create a scoreboard
		self.stats = GameStats(self)
		self.sb = Scoreboard(self)
		self.ship = Ship(self)
		self.bullets = pygame.sprite.Group()
		self.aliens = pygame.sprite.Group()

		self._create_fleet()

		#Make the EasyPlay button.
		self.play_button_easy = Button1(self, "(E)asy")
		self.play_button_hard = Button2(self, "(H)ard")
		
	def run_game(self):
		"""Start the main loop for the game."""
		while True:
			# Watch for keyboard and mouse events.
			self._check_events()

			# Check if game still active first!
			if self.stats.game_active:
				# Update ship's position.
				self.ship.update()

				# Update the bullets' position.
				self._update_bullets()

				# Update the Alien's movement:
				self._update_aliens()

			# Redraw the screen during each pass through the loop.
			self._update_screen()
			
	def _check_events(self):
		"""Respond to keypresses and mouse events"""
		for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
				elif event.type == pygame.KEYDOWN:
					self._check_keydown_events(event)
				elif event.type == pygame.KEYUP:
					self._check_keyup_events(event)
				elif event.type == pygame.MOUSEBUTTONDOWN:
					mouse_pos = pygame.mouse.get_pos()
					self._check_play_button_hard(mouse_pos)
					self._check_play_button_easy(mouse_pos)

	def _check_play_button_easy(self, mouse_pos):
		"""Start a new game when the player clicks Play"""
		button_clicked = self.play_button_easy.rect.collidepoint(mouse_pos)
		if button_clicked and not self.stats.game_active:	
			self.start_easy()

	def _check_play_button_hard(self, mouse_pos):
		"""Start a new game when the player clicks Play"""
		button_clicked = self.play_button_hard.rect.collidepoint(mouse_pos)
		if button_clicked and not self.stats.game_active:	
			self.start_hard()

	def start_easy(self):
	#Reset the game statistics and set active flag
		self.stats.reset_stats()
		self.stats.game_active = True
		self.sb.prep_score()

		#Get rid of remaining aliens and bullets
		self.aliens.empty()
		self.bullets.empty()

		#Create a new fleet and center the ship:
		self._create_fleet()
		self.ship.center_ship()

		#Hide the mouse cursor
		pygame.mouse.set_visible(False)

	def start_hard(self):
		#Reset the game statistics and set active flag
		self.stats.reset_stats()
		self.sb.prep_score()
		self.stats.game_active = True
		self.settings.ship_speed*=self.settings.initial_difficulty_multiplier
		self.settings.bullet_speed*=self.settings.initial_difficulty_multiplier
		self.settings.alien_speed*=self.settings.initial_difficulty_multiplier
		
		#Get rid of remaining aliens and bullets
		self.aliens.empty()
		self.bullets.empty()

		#Create a new fleet and center the ship:
		self._create_fleet()
		self.ship.center_ship()

		#Hide the mouse cursor
		pygame.mouse.set_visible(False)

	def _check_keydown_events(self,event):
		"""Respond to key presses."""
		if event.key == pygame.K_RIGHT:
			self.ship.moving_right = True
		elif event.key == pygame.K_LEFT:
			self.ship.moving_left = True
		elif event.key == pygame.K_SPACE:
			self._fire_bullet()
		elif event.key == pygame.K_q:
			sys.exit()
		elif event.key == pygame.K_e and not self.stats.game_active:	
			self.start_easy()
		elif event.key == pygame.K_h and not self.stats.game_active:
			self.start_hard()
		
	def _check_keyup_events(self,event):
		"""Respond to key releases."""
		if event.key== pygame.K_RIGHT:
			self.ship.moving_right = False
		elif event.key == pygame.K_LEFT:
			self.ship.moving_left = False

	def _fire_bullet(self):
		"""Create a new bullet and add it to the bullets group."""
		#First check max bullets allowed in settings.
		if len(self.bullets) < self.settings.bullets_allowed:
			new_bullet = Bullet(self)
			self.bullets.add(new_bullet)

	def _ship_hit(self):
		"""Respond to the ship being hit by an alien."""
		#Check how many lives left first!
		if self.stats.ships_left > 0:

			#Decrement ships_left.
			self.stats.ships_left -= 1

			#Get rid of any remaining aliens and bullets.
			self.aliens.empty()
			self.bullets.empty()
		
			#Create a new fleet and center the ship.
			self._create_fleet()
			self.ship.center_ship()

			#Pause
			sleep(1)

		else:
			self.stats.reset_stats()
			self.stats.game_active = False
			pygame.mouse.set_visible(True)

	def _check_aliens_bottom(self):
		"""Check if any aliens have reached the bottom of the screen."""
		screen_rect = self.screen.get_rect()
		for alien in self.aliens.sprites():
			if alien.rect.bottom >= screen_rect.bottom:
				#Treat this the same as if the ship got hit.
				self._ship_hit()
				break

	def _update_bullets(self):
		"""Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
		self.bullets.update()

		#Get rid of bullets that have disappeared.
		for bullet in self.bullets.copy():
			if bullet.rect.bottom <= 0:
				self.bullets.remove(bullet)

		self._check_bullet_alien_collisions()

	def _check_bullet_alien_collisions(self):
		"""Respond to bullet-alien collisions."""

		#Remove any bullets and aliens that have collided.
		collissions = pygame.sprite.groupcollide(
			self.bullets,self.aliens, True, True)

		if collissions:
			for aliens in collissions.values():
				self.stats.score+= self.settings.alien_points * len(aliens)
			self.sb.prep_score()

		#Check to see if all aliens are dead:
		if not self.aliens:
			#Destroy existing bullets and create new fleet.
			self.bullets.empty()
			self._create_fleet()
			self.settings.increase_speed()

	def _update_aliens(self):
		"""First check if the fleet is at an edge,
		Then update the positions of all aliens in the fleet."""
		self._check_fleet_edges()
		self.aliens.update()

		#Look for alien-ship collisions.
		if pygame.sprite.spritecollideany(self.ship, self.aliens):
			self._ship_hit()

		#Look for aliens reaching the bottom of screen.
		self._check_aliens_bottom()

	def _create_fleet(self):
		"""Create the fleet of aliens."""

		#Create an alien and find the number of aliens in a row.
		#Spacing between each alien is equal to one alien width.

		alien = Alien(self)
		alien_width, alien_height = alien.rect.size
		available_space_x = self.settings.screen_width - (2*alien_width)
		number_aliens_x = available_space_x // (2*alien_width)

		#Determine the number of rows of aliens that fit on the screen.

		ship_height = self.ship.rect.height
		available_space_y = (self.settings.screen_height -
				(3*alien_height)- ship_height)
		number_rows = available_space_y // (2*alien_height)

		#Create full fleet of aliens.
		for row_number in range(number_rows):
			for alien_number in range(number_aliens_x):
				self._create_alien(alien_number, row_number)

	def _create_alien(self, alien_number, row_number):
		"""Create an alien and place it in the row."""
		alien = Alien(self)
		alien_width, alien_height = alien.rect.size
		alien.x = alien_width + 2*alien_width*alien_number
		alien.rect.x = alien.x
		alien.rect.y = alien.rect.height + 2*alien.rect.height * row_number
		self.aliens.add(alien)

	def _check_fleet_edges(self):
		"""Respond if any aliens have reached an edge."""
		for alien in self.aliens.sprites():
			if alien.check_edges():
				self._change_fleet_direction()
				break

	def _change_fleet_direction(self):
		"""Drop the entire fleet and change the fleet's direction."""
		for alien in self.aliens.sprites():
			alien.rect.y += self.settings.fleet_drop_speed
		self.settings.fleet_direction*=-1

	def _update_screen(self):
		"""Update images on the screen and flip to the new screen."""
		self.screen.fill(self.settings.bg_color)
		self.ship.blitme()

		#Draw the bullets
		for bullet in self.bullets.sprites():
			bullet.draw_bullet()

		#Draw the aliens
		self.aliens.draw(self.screen)

		#Draw the score information.
		self.sb.show_score()

		# Draw the play buttons if the game is inactive.
		if not self.stats.game_active:
			self.play_button_easy.draw_button()
			self.play_button_hard.draw_button()
		#Make the most recently drawn screen visible.
		pygame.display.flip()

if __name__ == '__main__':
	#Make a game instance, and run the game.
	ai = AlienInvasion()
	ai.run_game()
