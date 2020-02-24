import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from util.orientation import Orientation
from util.vec import Vec3

from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator, GameInfoState

class MyBot(BaseAgent):

	def initialize_agent(self):
		# This runs once before the bot starts up
		self.controller_state = SimpleControllerState()

		self.FPS = 120
		
		self.lastTime = 0
		self.realLastTime = 0
		self.currentTick = 0
		self.skippedTicks = 0
		self.doneTicks = 0
		self.ticksNowPassed = 0

		self.stage = 0
		self.dodgeTick = 0
		self.lastGround = 0

	def get_output(self, packet: GameTickPacket) -> SimpleControllerState:

		self.packet = packet
		self.handleTime()

		if self.currentTick % 300 == 0:
			self.stage = -10
		
		if self.stage <= 0:
			car_state = CarState(physics=Physics(location=Vector3(0, 1000, 17), rotation=Rotator(0, 0, 0), angular_velocity=Vector3(0, 0, 10)))
			self.stage += 1
			self.lastGround = self.currentTick
		else:
			car_state = CarState(physics=Physics(location=Vector3(0, 1000, 1000), rotation=Rotator(pitch=0, roll=0), angular_velocity=Vector3(0, 0, 10)))
			
			if self.stage == 1:
				if self.lastGround + 10 > self.currentTick:
					self.stage = 2
				print("----------------")
				print("RESET")
				print("----------------")
			elif self.stage == 2:
				self.controller_state.roll = 1
				self.controller_state.pitch = 0
				self.controller_state.jump = True
				self.dodgeTick = self.currentTick
				self.stage = 3
			else:
				self.controller_state.jump = False
				print(f"{self.currentTick - self.dodgeTick}\t{packet.game_cars[self.index].physics.angular_velocity.x}\t{packet.game_cars[self.index].physics.angular_velocity.y}")

				if self.stage == 3:
					if self.dodgeTick + 5 < self.currentTick:
						self.stage = 4
				# elif self.stage == 4:
				# 	self.controller_state.pitch = -1
				# 	self.controller_state.roll = 0
				# 	self.stage = 5
				else:
					self.controller_state.pitch = 0
					self.controller_state.roll = 0
				

		self.set_game_state(GameState(cars={self.index: car_state}))

		return self.controller_state





	def handleTime(self):
		# this is the most conservative possible approach, but it could lead to having a "backlog" of ticks if seconds_elapsed
		# isnt perfectly accurate.
		if not self.lastTime:
			self.lastTime = self.packet.game_info.seconds_elapsed
		else:
			if self.realLastTime == self.packet.game_info.seconds_elapsed:
				return

			if int(self.lastTime) != int(self.packet.game_info.seconds_elapsed):
				if self.skippedTicks > 0:
					print(f"did {self.doneTicks}, skipped {self.skippedTicks}")
				self.skippedTicks = self.doneTicks = 0

			self.ticksNowPassed = round(max(1, (self.packet.game_info.seconds_elapsed - self.lastTime) * self.FPS))
			self.lastTime = min(self.packet.game_info.seconds_elapsed, self.lastTime + self.ticksNowPassed)
			self.realLastTime = self.packet.game_info.seconds_elapsed
			self.currentTick += self.ticksNowPassed
			if self.ticksNowPassed > 1:
				#print(f"Skipped {ticksPassed - 1} ticks!")
				self.skippedTicks += self.ticksNowPassed - 1
			self.doneTicks += 1