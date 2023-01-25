import math


class Particle:
    G = 1.
    MAX_ACC = 10
    MAX_VEL = 20

    def __init__(self, id: int, mass=None, x=None, y=None, vel_x=None, vel_y=None):
        self.id = id
        # Mass measured in kg
        self.mass = mass
        if mass is None:
            self.mass = 1.0
        # Set position
        self.x = x
        self.y = y
        if x is None:
            self.x = 0.0
        if y is None:
            self.y = 0.0
        # Speed measured in m/s -- ↑=+y ↓=-y ←=-x →=+x
        self.vel_x = vel_x
        self.vel_y = vel_y
        if vel_x is None:
            self.vel_x = 0.0
        if vel_y is None:
            self.vel_y = 0.0

        # Radius of particle measured in meters
        self.radius = 0.5
        # Acceleration measured in m/s^2
        self.accx = 0.0
        self.accy = 0.0
        # Total force measured in Newtons
        self.force_x = 0.0
        self.force_y = 0.0

    def attraction(self, p2):
        # Calculate distance between particles (Pythagorus Theorum)
        self.d = math.sqrt((p2.x - self.x) ** 2 + (p2.y - self.y) ** 2)
        self.dx = p2.x - self.x
        self.dy = p2.y - self.y
        # Calculate force
        self.force = 0
        if self.d != 0:
            # Newton's Law of Universal Gravitation
            self.force = self.G * self.mass * p2.mass / (self.d ** 2)
        # Get angle
        angle = math.atan2(self.dy, self.dx)
        # Get force components
        self.force_x = math.cos(angle) * self.force
        self.force_y = math.sin(angle) * self.force

        # Update acceleration
        self.accx += self.force_x / self.mass
        if self.accx > self.MAX_ACC:
            self.accx = self.MAX_ACC
        elif self.accx < -self.MAX_ACC:
            self.accx = -self.MAX_ACC
        self.accy += self.force_y / self.mass
        if self.accy > self.MAX_ACC:
            self.accy = self.MAX_ACC
        elif self.accy < -self.MAX_ACC:
            self.accy = -self.MAX_ACC

    def updatePosition(self, particles: list, updateDelay: float):
        # Reset force
        self.force_x = 0.
        self.force_y = 0.
        # Reset acceleration
        self.accx = 0.
        self.accy = 0.
        for p in particles:
            if p != self:
                self.attraction(p)

        # Update speed
        self.vel_x += self.accx * updateDelay
        self.vel_y += self.accy * updateDelay
        # Update position
        self.x = self.x + (self.vel_x * updateDelay)
        self.y = self.y + (self.vel_y * updateDelay)
