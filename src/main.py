import random
from threading import Thread
from tkinter import Canvas, Label, Radiobutton, TclError, font, Tk, Button, Frame, ttk
import tkinter as tk
from particle import Particle
import time


class ParticleThread(Thread):
    def __init__(self, id: int, particle: Particle, master=None, length=None,
                 fps=None, speed=None, other: list = []):
        super().__init__()

        self.id = id
        self.particle = particle
        self.duration = 0.0
        self.length = length
        if length is None:
            self.length = 3.0
        self.fps = fps
        if fps is None:
            self.fps = 1
        self.master = master
        self.speed = speed*800
        if speed is None:
            self.speed = 1.0 * 800
        self.other = other

    def run(self):
        delay = 1 / self.fps
        while self.duration < self.length:
            # Wait 1 frame
            time.sleep(delay)
            self.duration += delay
            # Set speed
            self.particle.updatePosition(self.other, (delay * self.speed))
            # Render
            self.master.updateSimulation(self)


class App(Tk):
    def __init__(self):
        super().__init__()

        # Set GUI attributes
        self.title("Gravity Simulator - Jaydon Walters")
        self.resizable(False, False)
        self.createCanvas()
        self.createConsole()
        self.simulations = []
        self.particles = []

    def createCanvas(self):
        self.canvas = Canvas(self, bg="black", width=580, height=580)
        self.canvas.grid(column=0, row=0, padx=10, pady=10)
        self.meter = self.canvas.winfo_reqwidth() / 50

    def createConsole(self):
        underlined = font.Font(font=Label().cget("font"))
        underlined.configure(underline=True)
        # Add Frame
        self.console = Frame(self, relief=tk.RAISED,
                             width=200, height=580)
        self.console.grid(column=1, row=0, padx=10, pady=10)
        current_row = 0
        Label(self.console, text="Simulation settings:",
              font=underlined).grid(column=0, row=current_row, columnspan=2)
        current_row += 1
        # Number of particles
        self.num_particles = tk.StringVar()
        self.num_particles.trace_add("write", self.updateConsole)
        Label(self.console, text="Number of particles:").grid(
            column=0, row=current_row, padx=5, pady=5)
        self.num_input = ttk.Spinbox(self.console, from_=2, to=100,
                                     textvariable=self.num_particles)
        self.num_input.grid(column=1, row=current_row, padx=5, pady=5)
        self.num_input.set(2)   # Default value
        self.max_particles = Button(
            self.console, text="Max", command=self.setMaxParticles)
        self.max_particles.grid(column=2, row=current_row)
        current_row += 1
        # Speed input
        Label(self.console, text="Simulation speed multiplier:").grid(
            column=0, row=current_row, padx=5, pady=5)
        self.spd_input = ttk.Spinbox(self.console, from_=1, to=10)
        self.spd_input.grid(column=1, row=current_row, padx=5, pady=5)
        self.spd_input.set(1)   # Default value
        current_row += 1
        # Lenth input
        Label(self.console, text="Length of simulation:").grid(
            column=0, row=current_row, padx=5, pady=5)
        self.length_input = ttk.Spinbox(self.console, from_=1, to=5*60)
        self.length_input.grid(column=1, row=current_row, padx=5, pady=5)
        self.length_input.set(60)    # Default value
        Label(self.console, text="seconds").grid(column=2, row=current_row)
        current_row += 1
        # Placement controls
        Label(self.console, text="Particle placement", font=underlined).grid(
            column=0, row=current_row, columnspan=2)
        current_row += 1
        self.placement = tk.StringVar()
        self.placement.trace_add("write", self.updateConsole)
        self.centre_button = Radiobutton(self.console, text="Centre",
                                         variable=self.placement, value='c')
        self.centre_button.grid(column=0, row=current_row)
        self.everywhere_button = Radiobutton(self.console, text="Everywhere",
                                             variable=self.placement, value='e')
        self.everywhere_button.grid(column=1, row=current_row)
        self.placement.set("e")
        current_row += 1
        # Initial velocity controls
        Label(self.console, text="Initial velocity",
              font=underlined).grid(column=0, row=current_row, columnspan=2)
        current_row += 1
        self.direction = tk.StringVar()
        self.direction.trace_add("write", self.displayMinMax)
        self.no_vel = Radiobutton(self.console, text="None",
                                  variable=self.direction, value="n")
        self.no_vel.grid(column=0, row=current_row)
        self.ran_vel = Radiobutton(self.console, text="Random",
                                   variable=self.direction, value="r")
        self.ran_vel.grid(column=1, row=current_row)
        self.direction.set("n")
        current_row += 1
        # Min / max initial velocity
        self.min_label = Label(self.console, text="Min:")
        self.min_label.grid(column=0, row=current_row)
        self.min_v = tk.StringVar()
        self.min_v.trace_add("write", self.compareMinMax)
        self.max_v = tk.StringVar()
        self.max_v.trace_add("write", self.compareMinMax)
        self.min_vel_input = ttk.Spinbox(self.console, from_=-1., to=1.,
                                         textvariable=self.min_v, increment=0.1)
        self.min_vel_input.grid(column=1, row=current_row)
        current_row += 1
        self.max_label = Label(self.console, text="Max:")
        self.max_label.grid(column=0, row=current_row)
        self.max_vel_input = ttk.Spinbox(self.console, from_=-1., to=1.,
                                         textvariable=self.max_v, increment=0.1)
        self.max_vel_input.grid(column=1, row=current_row)
        self.min_vel_input.set(-1.)
        self.max_vel_input.set(1.)
        self.min_label.grid_remove()
        self.max_label.grid_remove()
        self.min_vel_input.grid_remove()
        self.max_vel_input.grid_remove()
        current_row += 1
        # Create warning message
        self.warning = Label(self.console, fg="red",
                             text="Please enter all fields")
        self.warning.grid(column=0, columnspan=3, row=current_row)
        self.warning.grid_remove()
        current_row += 1
        # Place button
        self.place_button = Button(self.console, text="Place particles")
        self.place_button.grid(column=0, row=current_row, padx=5, pady=5)
        self.place_button['command'] = self.placeParticles
        # Start button
        self.start_button = Button(self.console, text="Start simulation",
                                   state=tk.DISABLED)
        self.start_button.grid(column=1, row=current_row, padx=5, pady=5)
        self.start_button['command'] = self.startAll
        current_row += 1
        # Stop button
        self.stop_button = Button(self.console, text="Stop simulation",
                                  state=tk.DISABLED)
        self.stop_button.grid(column=1, row=current_row, padx=5, pady=5)
        self.stop_button['command'] = self.stopAll

    def updateConsole(self, *args):
        try:
            self.place_button['text'] = "Place particles"
            self.start_button['state'] = tk.DISABLED
            # Check max value
            if self.num_particles.get() != "100":
                self.max_particles["state"] = tk.NORMAL
            else:
                self.max_particles['state'] = tk.DISABLED
        except AttributeError:
            pass

    def setMaxParticles(self, *args):
        if self.num_particles.get() != "100":
            self.max_particles["state"] = tk.DISABLED
            self.num_particles.set("100")
        else:
            pass

    def displayMinMax(self, *args):
        try:
            if self.direction.get() != "n":
                self.min_label.grid()
                self.max_label.grid()
                self.min_vel_input.grid()
                self.max_vel_input.grid()
            else:
                self.min_label.grid_remove()
                self.max_label.grid_remove()
                self.min_vel_input.grid_remove()
                self.max_vel_input.grid_remove()
        except AttributeError:
            pass

    def compareMinMax(self, *args):
        try:
            self.max_vel_input.configure(from_=self.min_v.get())
            self.min_vel_input.configure(to=self.max_v.get())
        except tk.TclError:
            pass

    def placeParticles(self):
        try:
            self.place_button['text'] = "Reseed particles"
            self.start_button['state'] = tk.NORMAL
            self.stop_button['state'] = tk.DISABLED
            self.warning.grid_remove()
            # Get user input
            n = int(self.num_input.get())
            l = int(self.length_input.get())
            s = int(self.spd_input.get())
            # Clear stored data
            self.particles.clear()
            self.simulations.clear()
            # Rerender canvas
            self.createCanvas()
            # Create particles
            for x in range(n):
                self.particles.append(Particle(x, mass=20.))
                p = self.particles[x]
                # Placement options
                if self.placement.get() == 'c':
                    padding = int(app.canvas.winfo_reqwidth() / 4)
                else:
                    padding = 10
                p.x = random.randrange(
                    padding, app.canvas.winfo_reqwidth() - padding)
                p.y = random.randrange(
                    padding, app.canvas.winfo_reqheight() - padding)
                # Initial velocity options
                min = float(self.min_vel_input.get())
                max = float(self.max_vel_input.get())
                if self.direction.get() == 'r':
                    p.vel_x = random.uniform(min, max)
                    p.vel_y = random.uniform(min, max)
                else:
                    p.vel_x = 0
                    p.vel_y = 0
                # Create simulation threads
                sim = ParticleThread(x, p, fps=60, master=app,
                                     length=l, speed=s)
                self.addSimulation(sim)
                del p
            for x in self.simulations:
                x.other = self.particles
        except:
            # Place warning message
            self.warning.grid()
            self.place_button['text'] = "Place particles"
            self.place_button['state'] = tk.NORMAL
            self.start_button['state'] = tk.DISABLED
            self.stop_button['state'] = tk.DISABLED

    def startAll(self):
        # Start simulation
        try:
            self.start_button['state'] = tk.DISABLED
            self.stop_button['state'] = tk.NORMAL
            self.place_button['state'] = tk.DISABLED
            self.num_input['state'] = tk.DISABLED
            self.spd_input['state'] = tk.DISABLED
            self.length_input['state'] = tk.DISABLED
            self.max_particles['state'] = tk.DISABLED
            for x in self.simulations:
                x.length = int(self.length_input.get())
                x.speed = int(self.spd_input.get())
                # Initial velocity options
                min = float(self.min_vel_input.get())
                max = float(self.max_vel_input.get())
                if self.direction.get() == 'r':
                    x.particle.vel_x = random.uniform(min, max)
                    x.particle.vel_y = random.uniform(min, max)
                else:
                    x.particle.vel_x = 0
                    x.particle.vel_y = 0
                x.start()
                self.checkRunning(x)
        except:
            self.start_button['state'] = tk.NORMAL
            self.stop_button['state'] = tk.DISABLED
            self.place_button['state'] = tk.NORMAL
            self.num_input['state'] = tk.NORMAL
            self.spd_input['state'] = tk.NORMAL
            self.length_input['state'] = tk.NORMAL
            if self.num_particles.get() != '100':
                self.max_particles['state'] = tk.NORMAL
            else:
                self.max_particles['state'] = tk.DISABLED

    def stopAll(self):
        self.stop_button['state'] = tk.DISABLED
        self.place_button['state'] = tk.NORMAL
        self.num_input['state'] = tk.NORMAL
        self.spd_input['state'] = tk.NORMAL
        self.length_input['state'] = tk.NORMAL
        if self.num_particles.get() != '100':
            self.max_particles['state'] = tk.NORMAL
        else:
            self.max_particles['state'] = tk.DISABLED
        # Stop all threads
        for x in self.simulations:
            x.length = x.duration
        # Clear stored data
        self.simulations.clear()
        self.particles.clear()

    def checkRunning(self, thread: Thread):
        if thread.is_alive():
            self.after(100, lambda: self.checkRunning(thread))
        else:
            self.stopAll()

    def addSimulation(self, sim: ParticleThread):
        radius = self.meter * sim.particle.radius  # Set local radius
        # Draw particle
        sim.particle.id = self.canvas.create_oval(
            sim.particle.x,  sim.particle.y,
            sim.particle.x + radius,  sim.particle.y + radius,
            fill="skyblue", width=0
        )
        self.simulations.append(sim)

    def updateSimulation(self, sim: ParticleThread):
        # Move particle
        self.canvas.move(sim.particle.id,
                         sim.particle.vel_x * (1/sim.fps) * self.meter,
                         sim.particle.vel_y * (1/sim.fps) * self.meter)
        self.update()


if __name__ == "__main__":
    # Create app
    app = App()
    app.mainloop()
