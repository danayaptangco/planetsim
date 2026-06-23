import numpy as np
import batman
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML

class Constants:  
    '''
    Class for astronomical constants used in this simualtion
        
    Attributes:
        G (float): gravitational constant (m^3 kg^-1 s^-2)
        msun (float): solar mass (kg)
        rsun (float): solar radius (m)
    '''

    def __init__(self):
        self.G = 6.67430e-11  # m^3 kg^-1 s^-2
        self.msun = 1.989e30  # kg
        self.rsun = 6.957e8  # m


class Transit:
    '''
    Class for transit objects
        
    Attributes:
        planet (class): object created from planet class
        star (class): object created from star class
    '''

    def __init__(self, planet, star):
        self.planet_radius = planet.radius
        self.star_radius = star.radius
        self.planet_orbital_period = planet.orbital_period
        self.planet_x = planet.x  # current planet x position
        self.front = True  # is planet in front of star?

        self.star_mass = star.mass

        c = Constants()

        # --- Newton Kepler 3rd law ---
        P = self.planet_orbital_period * 86400   # days -> seconds
        M = self.star_mass * c.msun              # solar masses -> kg

        self.semimajor_axis = (
            c.G * M * P**2 / (4 * np.pi**2)
        ) ** (1/3)                              #units of meters


        self.star_radius_m = self.star_radius * c.rsun              # solar radii -> meters

        # convert to stellar radii for plotting + batman
        self.semimajor_axis = self.semimajor_axis / self.star_radius_m


    def make_lightcurve(self):
        '''
        Generate the transit lightcurve with batman
        
        Inputs:
            None

        Returns:
            None
        '''
        params = batman.TransitParams()
        params.t0 = 50.                       #time of inferior conjunction
        params.per = self.planet_orbital_period                      #orbital period
        params.rp = self.planet_radius / self.star_radius     #planet radius (in units of stellar radii)
        params.a = self.semimajor_axis          #semi-major axis (in units of stellar radii)
        params.inc = 90.                     #orbital inclination (in degrees)
        params.ecc = 0.                      #eccentricity
        params.w = 90.                       #longitude of periastron (in degrees)
        params.u = [0.1, 0.3]                #limb darkening coefficients [u1, u2]
        params.limb_dark = "quadratic"       #limb darkening model
        t = np.linspace(0,100, 1000)            #times at which to calculate light curve)
        m = batman.TransitModel(params, t)    #initializes model
        flux = m.light_curve(params)          #calculates light curve

        plt.plot(t, flux)
        plt.xlabel("Time from central transit")
        plt.ylabel("Relative flux")
        plt.show()


    def make_snapshot(self, x):
        '''
        Create snapshot of system given planet position using matplotlib
        
        Inputs:
            x (int): horizontal position of planet relative to star
        
        Returns:
            None
        '''
        star_circle=plt.Circle((0,0),self.star_radius, color='yellow', alpha=1)
        planet_circle = plt.Circle((x,0),
                self.planet_radius,
                color='blue',
                alpha=1
            )

        fig, ax = plt.subplots()
        ax.add_patch(star_circle)
        ax.add_patch(planet_circle)
        plt.xlim(-2, 2)
        plt.ylim(-2, 2)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.hlines(0, -2, 2, color='black', linestyle='--', lw=0.5)
        plt.show()

    def make_animation(self):
        '''
        Create animation of system as planet follows its orbit
        
        Inputs:
            None

        Returns:
            None
        '''
        times = np.linspace(
            0,
            self.planet_orbital_period,
            100
        )

        fig, ax = plt.subplots()


        # star
        star_circle = plt.Circle(
            (0, 0),
            self.star_radius,
            color='yellow'
        )

        # planet
        planet_circle = plt.Circle(
            (0, 0),
            self.planet_radius,
            color='blue'
        )
        
        ax.add_patch(star_circle)
        ax.add_patch(planet_circle)

        ax.set_xlim(-1.2*self.semimajor_axis, 1.2*self.semimajor_axis)
        ax.set_ylim(-1.2*self.semimajor_axis, 1.2*self.semimajor_axis)
        ax.set_aspect('equal')


        def update(frame):
            '''
            Update animation frame as planet orbits

            Inputs:
                frame (): current state of system

            Returns:
                planet_circle (matplotlib patch): planet patch with updated position and zorder
            '''
            if self.front == True:
                zorder = 1
            elif self.front == False:
                zorder = 0

            t = times[frame]
            phase = 2*np.pi*t/self.planet_orbital_period

            x = self.semimajor_axis * np.sin(phase)

            planet_circle.center = (x, 0) 
            planet_circle.set_zorder(zorder)  # update whether planet is in front of or behind star
            
            if x > self.planet_x:
                self.front = True
            elif x < self.planet_x:
                self.front = False
                
            self.planet_x = x
            
            return (planet_circle,)

        anim = FuncAnimation(
            fig,
            update,
            frames=len(times),
            interval=50,
            blit=True
        )

        plt.close(fig)  # prevents duplicate static plot

        return HTML(anim.to_jshtml())


    

class Planet:
    '''
    Class for planet objects
        
    Attributes:
        radius (float): planet radius (meters)
        orbital_period (float): planet orbital period (seconds)
    '''
    def __init__(self, radius, orbital_period):
        self.radius = radius
        self.orbital_period = orbital_period
        self.x = 0

class Star:
    '''
    Class for star objects
        
    Attributes:
        radius (float): star radius (meters)
        mass (float): star mass (kg)
    '''

    def __init__(self, radius, mass):
        self.radius = radius
        self.mass = mass
