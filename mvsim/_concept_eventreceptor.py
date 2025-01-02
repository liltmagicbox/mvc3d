





#======================================
# healer, rock situation : cast magic.
#===========

#=== quite formed heal. a function to a target.
def heal(target):
	target.hp = target.max_hp
	target.illness = []
#what about caster's mp??
#maybe all funcs shall be self,target..
def heal(self,target):
	self.mp -= 5
	target.hp = target.max_hp
	target.illness = []
#what if not mp?
def heal(self,target):
	try:
		self.mp -= 5
	except:
		return
	target.hp = target.max_hp
	target.illness = []
#what if hasatrr(target,'hp') == False ???

def heal(self,target):
	self.mp -= 5
	target.hp = target.max_hp
	target.illness = []

class Rock:
	1

class Healer:
	def __init__(self):
		self.mp = 20

		#this may be changed via spells, or..  type:friendly or aggressive ..? ..ultimate?
		self.harrasments = [
		'{self}, the sacred one,',
		'to the evil enermy {target},',
		'give the power of {magic}!',
		'...justice delivered.'
		]
	def __repr__(self):
		return "I'm a healer."
	def cast(self, magic, target):
		tmp_harr = []
		for i in self.harrasments:			
			i = i.replace('{self}', str(self) )
			i = i.replace('{magic}', str(magic) )
			i = i.replace('{target}', str(target) )
			tmp_harr.append(i)
		for i in tmp_harr:
			print(i)			

		try:
			magic(self,target)
		except Exception as err:
			print( f"{self}: magic failed,", str(err) )

def healer_casts_heal_to_rock():
	mana = Healer()
	rock1 = Rock()
	mana.cast(heal, rock1)


def abadacadabara(self,target):
	if self.will_to_kill:
		target.hp=0

#===========
# healer, rock situation : cast magic.
#======================================






#======================================
# 2 types of magic
#===========
#1-you can kill directly
def kill_someone(self,target):
	"""super simple, whoever!"""
	target.kill()
	self.call911(self)

#2-you can kill by
def damage_enought_to_kill(self,target):
	"""whether killed or not is lied on the target"""
	damage = 500000
	damage = Damage.Pierce(500000,'knife')
	target.deliver(damage)

"""
maybe all events, shall be??
Damage.pierce #blunt..)
pierce not delivers physical Force. while blunt does.
Heal #Heal != -Damage
Fire?
Illness?
Boom?
Sound?
Visual?
"""

#most inputs from outside is via sensor.
#skin has collision sensor, with thermo,,
#eye can be assumed as visual collision detector.
#ear also has listen-bound-volume
#..so most of is collision volume.!

#===========
# 2 types of magic
#======================================


#======================================
# magic level concept
#===========

#finally ofcourse or maybe a spell is a class and has attr of required_level kinds..
#func can't sized. what about len(funcname)? or even remember, write? not that bad, ofcourse.
# spells that requires serialized spell..  i'm bone of the sword.. kinds.  even mic input.

#keep the concept of 'level'. not just exp and got.  a new user shall beat the old one!
#not the charactor, but a player.

#like:
#>>> ubw()#listening further spells..
#>>> 'im the bone of the sword'
#>>> 'WEF*@(#'
# SPELLERROR :spell ubw not matching.

#===========
# magic level concept
#======================================




#======================================
# attack/ defense relationship.
#===========


class Arrow:
	def __init__(self):
		self.pierce = 100
class PoisonArrow(Arrow):
	def __init__(self):
		super().__init__()
		self.poison = 50

class Shield:
	def __init__(self):
		1#self.hp
	def receive(self):
		1













#speed not slown
class Owl:
	def __init__(self):
		self.speed = 10	
	def receive(self, func):
		"""owl keeps speed"""
		tmp = self.speed
		func(self)
		self.speed = tmp



def damage(target):
	target.hp -= 20	
	#if hp<0.. this is more general thing,right?

def recv_immotal(self, func):
	tmp = self.hp
	func(self)
	self.hp = tmp

class Mummy:
	def __init__(self):
		self.hp = 5
		#self.receive = recv_immotal#not pythonic..
	def receive(self,func):
		func(self)

def mummy_is_immotal():
	a = Mummy()
	print(a.hp)

	#damage(a)#not thisway.
	#a.receive(a,damage)
	a.receive(damage)
	print(a.hp)#a still alive!










#pre-post is annoying but better forgetting func(self).

class Flying_Swordman:
	def __init__(self):
		self.damage = 500
		self.speed = 100
	def attack(self,target):
		target.hp -= self.damage
	def defense(self,func):
		tmp = self.damage
		func(self)
		self.damage = tmp
	
	def pre_defense(self):
		self.tmp = self.damage
	def post_defense(self):
		self.damage = self.tmp	
	def _defense(self,func):
		self.pre_defense()
		func(self)
		self.post_defense()

class Slower:
	def __init__(self):
		self.hp = 10
	def attack(self,target):
		target.damage -= 20
		target.speed -= 20
	def defense(self,func):
		func(self)

def engage(a,b):
	b.defense(a.attack)
	a.defense(b.attack)

def flying_swordsman_damage_preserved_slows_down():

	sman = Flying_Swordman()
	triwall = [Slower() for i in range(3)]

	for wall in triwall:
		#sman.attack(wall)
		#wall.attack(sman)
		engage(sman,wall)
		print(sman.damage,sman.speed)
		print(wall.hp)





class Event:
	1

class EF:#event factory..
	@classmethod
	def Speed(cls,*args):
		return Speed(*args)

class Speed(Event):
	def __init__(self,value):
		self.value = value
		self.by = None
		self.target = None
	def __repr__(self):
		return f"{self.value} {self.by} {self.target}"

#world.add(actor1)
class Actor:
	def __init__(self):
		self.world = None
	def deliver(self, event,target=None):
		event.by = self
		event.target = target
		print(event)
		if self.world:
			self.world.send(event)

class Slower(Actor):
	def __init__(self):
		super().__init__()
		self.hp = 10
	def attack(self,target):
		#target.damage -= 20
		#target.speed -= 20
		
		event = EF.Speed(-20)
		self.deliver(event,target)

	def defense(self,func):
		func(self)


def speed_down_by_event_EventFactory():
	a = Slower()
	a.attack( 'baka' )

#===========
# attack/ defense relationship.
#======================================











#======================================
# more concepts
#===========
#visual cone collision volume

#building snow , snow sim gets all building's collisiondata, not logic, actor itself.(static)
#just collision point, a snow can settle there.

#moving , each collision and pos. shall it be id, and stuck? _maybe that's the type of surface

#maybe all interactions shall be collision. atleast sound,visible is now confirmed.

#collision translated by F, or DamageType Events??

#boom hp-=20 , fire() ?? or Event.Boom(20,'fire') ??


#===========
# more concepts
#======================================
