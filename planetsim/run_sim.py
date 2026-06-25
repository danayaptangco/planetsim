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
        self.m_sun = 1.989e30  # kg
        self.r_sun = 6.957e8  # m
        self.r_jupiter = 7.149e7 # m 
        self.days2sec = 86400 #s 

class Planet:
    '''
    Class for planet objects
        
    Attributes:
        radius (float): it's passed in jupiter radii units but it's converted and stored in SI units. 
        orbital_period (float): it's passed in days but it's converted and stored in SI units. 
    '''
    def __init__(self, radius, orbital_period):
        c = Constants()
        self.radius = radius * c.r_jupiter #  rJupiter --> meters 
        self.orbital_period = orbital_period * c.days2sec # days --> seconds 
        self.x = 0

class Star:
    '''
    Class for star objects
        
    Attributes:
        radius (float): star radius. It's passed in solar radii units but it's converted and stored in SI units. 
        mass (float): star mass. It's passed in jupiter radii units but it's converted and stored in SI units. 
    '''

    def __init__(self, radius, mass):
        c = Constants()
        self.radius = radius * c.r_sun
        self.mass = mass * c.m_sun

class Transit:
    '''
    Class for transit objects
        
    Attributes:
        planet (class): object created from planet class
        star (class): object created from star class
    '''

    def __init__(self, planet, star):
        self.planet_radius = planet.radius # m
        self.star_radius = star.radius # m
        self.planet_orbital_period = planet.orbital_period #s
        self.planet_x = planet.x  # current planet x position
        self.front = True  # is planet in front of star?

        self.star_mass = star.mass #kg 

        c = Constants()

        # --- Newton Kepler 3rd law ---
        #P = self.planet_orbital_period * 86400   # days -> seconds
        #M = self.star_mass * c.msun              # solar masses -> kg

        self.semimajor_axis = (c.G * self.star_mass * self.planet_orbital_period**2 
                               / (4 * np.pi**2)) ** (1/3)    # m                        


        #self.star_radius_m = self.star_radius * c.rsun              # solar radii -> meters

        # convert to stellar radii for plotting + batman
        #self.semimajor_axis = self.semimajor_axis / self.star_radius


    def make_lightcurve(self):
        
        c = Constants()

        '''
        Generate the transit lightcurve with batman
        
        Inputs:
            None

        Returns:
            None
        '''
        params = batman.TransitParams()
        params.t0 = self.planet_orbital_period/c.days2sec / 2                       #time of inferior conjunction
        params.per = self.planet_orbital_period/c.days2sec   #orbital period IN DAYS
        params.rp = self.planet_radius / self.star_radius     #planet radius (in units of stellar radii)
        params.a = self.semimajor_axis/self.star_radius      # planet's semi-major axis (in units of stellar radii)
        params.inc = 90.                     #orbital inclination (in degrees)
        params.ecc = 0.                      #eccentricity
        params.w = 90.                       #longitude of periastron (in degrees)
        params.u = [0.1, 0.3]                #limb darkening coefficients [u1, u2]
        params.limb_dark = "quadratic"       #limb darkening model
        t = np.linspace(0,self.planet_orbital_period/c.days2sec, 1000)            #times at which to calculate light curve)
        m = batman.TransitModel(params, t)    #initializes model
        flux = m.light_curve(params)          #calculates light curve

        # plt.plot(t, flux)
        # plt.xlabel("Time from central transit")
        # plt.ylabel("Relative flux")
        # plt.show()

        return flux, t


    def make_snapshot(self, x):
        c = Constants()
        '''
        Create snapshot of system given planet position using matplotlib
        
        Inputs:
            x (int): horizontal position of planet relative to star
        
        Returns:
            None
        '''
        # planet and star radii need to be on the same scale so that they will plot right. 
        star_circle=plt.Circle((0,0),self.star_radius/c.r_sun, color='yellow', alpha=1)
        planet_circle = plt.Circle((x,0),
                self.planet_radius/c.r_sun,
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
        c = Constants()
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

        #Calculating the ratio of white space to star size to line up with lightcurve
        R_star = self.star_radius / c.r_sun

        xmax = 1.2 * self.semimajor_axis / c.r_sun
        L = 2 * xmax  # total plot width
        D_star = 2 * R_star
        star_fraction = D_star / L

        print("Star fraction of plot:", star_fraction)

        #Calculating 





        fig, (ax1, ax2) = plt.subplots(2, 1, figsize = (5,10))

        flux, t = self.make_lightcurve()

        ax1.plot(t, flux)
        ax1.set_box_aspect(1)
        ax1.set_xlim(0, self.planet_orbital_period/c.days2sec)

        # star
        star_circle = plt.Circle(
            (0, 0),
            self.star_radius/ c.r_sun,
            color='yellow'
        )

        # planet
        planet_circle = plt.Circle(
            (0, 0),
            self.planet_radius/ c.r_sun,
            color='blue'
        )
        
        ax2.add_patch(star_circle)
        ax2.add_patch(planet_circle)

        ax2.set_xlim(-1.2*self.semimajor_axis/c.r_sun, 1.2*self.semimajor_axis/c.r_sun)
        ax2.set_ylim(-1.2*self.semimajor_axis/c.r_sun, 1.2*self.semimajor_axis/c.r_sun)
        ax2.set_aspect('equal')




        def update(frame):
            c = Constants()
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

            x = self.semimajor_axis/c.r_sun * np.sin(phase)
            #print(f'your phase number is {phase} and your x is {x}')

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

        gif_path = "planet_transit.gif"

        anim.save(
            gif_path,
            writer="pillow",
            fps=20
        )

        return gif_path

