class Panel:
    def __init__(self):
        """Assumes a 1 square meter panel receiving 800 Watts from Sun, on a 300K day."""

        # Kelvins. This is about how hot I imagine a panel sitting in the sun with no cooling could get.
        self.temp = 320

        # Watts from the sun that are heating up the panel.
        # a typical square meter panel produces 150 watts out of the 800 from the sun. I am guessing 300 of them
        # heat the panel up, and the rest is reflected.
        self.sun_heat = 300

        # joules/degree K specific heat multiplied by mass of panel. Rough approximation
        self.spec_heat = 10000

        # Watts,this is the amount of heat the panel is conducting into the surrounding air.
        # It is at equilibrium with the sun heating up the panel at the start of the sim.
        self.heat_to_air = 300

        # Watts. The water pump is off at the beginning of the sim.
        self.heat_to_water = 0

        # Liters. I estimate there is this much water in contact with the panel while the pump is on.
        # Not to be confused with flow rate, this is just how much the panel holds.
        self._water_volume = 0.5

        # Watts per Kelvin. this is the heat_to_air divided by the difference between
        # the temp of the panel and the temp of the air, which is 50K in this example.
        self.cooling_air_const = 15

        # This is the temp of the water coming out of the panel.
        # I am starting the simulation as if the pump has just been turned on after being off for a while.
        self.water_out_temp = 296
        self.water_in_temp = 295

        # Watts/Kelvin. Did some research into heat transfer constants of materials and factored in that the water
        # would be in contact with most of the surface of the panel to come up with this approximation.
        self.cooling_water_const = 50

    def set_water_out_temp(self, temp_water_in, flow_rate):
        """This assumes that the amount of time the water is in contact with the panel is small,
        and that thus the water does not heat up much, thus the temperature difference between the water and panel is
        constant, thus the wattage heating up the water is constant. Indeed with the volume and flow rate assumed any
        element of water is in contact with the panel for 2 seconds (volume/flowrate)"""

        # Newton cooling says that the wattage is proportional to the temp differential
        self.heat_to_water = self.cooling_water_const * (self.temp - temp_water_in)

        # the resulting temperature change. heat wattage multiplied by the time the water is contacting the panel,
        # divided by specific heat
        water_temp_change = self.heat_to_water / (self._water_volume * 1000 * 4.186) * self._water_volume / flow_rate
        self.water_out_temp = temp_water_in + water_temp_change

    def set_heat_to_air(self):
        self.heat_to_air = self.cooling_air_const * (self.temp - 300)

    def change_temp(self, dt, temp_water_in, flow_rate):
        self.set_heat_to_air()
        self.set_water_out_temp(temp_water_in, flow_rate)
        self.temp += dt*(self.sun_heat - self.heat_to_air - self.heat_to_water) / self.spec_heat



class Tank:
    """This is 150L of water."""

    def __init__(self):
        self.vol = 150
        self.temp = 295  # Kelvin
        self.spec_heat = 627900  # J/ degree K specific heat multiplied by mass of water
        self.water_in_temp = 320  # K

    def set_temp_tank(self, water_in_temp, flow_rate, dt):
        """This assumes the water incoming mixes homogeneously with the water in the tank so that
        the temperatures average out."""
        volume_in = float(flow_rate*dt)
        volume_orig_temp = float(self.vol-volume_in)

        orig_temp = float(self.temp)

        self.temp = (volume_in*water_in_temp+volume_orig_temp*orig_temp)/self.vol



class Controller:

    def __init__(self):
        import time
        self.flow_rate = 0.25  # Liters/second. I read online that a solar panel uses about 4 gallons per minute.

        self.panel = Panel()
        self.tank = Tank()
        # The sim starts at time = 0
        self.time = 0


        # These three have to do with time. The way to interpret this, with these particular values, is:
        # the sim will do a physical calculation for every 0.1 second in sim-time.
        # It will run 600 of these calculations, and output the results to the user every 1 seconds.
        # So here we are getting an update for each minute of sim time every second.
        self.time_resolution = .1
        self.sim_runs = 600
        self.time_delay = 1


        while True:
            print(self.log_temps())
            for i in range(self.sim_runs):
                self.set_temps()

            time.sleep(1)
            self.time += self.time_resolution*self.sim_runs




    def set_temps(self):
        water_to_pan = float(self.tank.temp)
        water_to_tank = float(self.panel.water_out_temp)
        self.tank.set_temp_tank(water_to_tank, self.flow_rate, self.time_resolution)
        self.panel.change_temp(self.time_resolution, water_to_pan, self.flow_rate)


    def log_temps(self):
        return '{0}min Panel Temp: {1}, Tank Temp: {2}, Water to/from panel: {3}/{4}'.format(self.time/60,
            round(self.panel.temp, 2), round(self.tank.temp, 2), round(self.panel.water_in_temp, 2),
            round(self.panel.water_out_temp,2))


system = Controller()


# With the physical constants and initial conditions I have supplied, the panel seems to hit a low temperature at about
# 301 degrees 15min in, and then starts to climb. This is because in this model, the tank is a perfect insulator,
# in reality the tank has it's own cooling constant, hopefully it has some radiator pipes or the hot water is
# being used and replaced with cooler water. Of course all of this data could be generated with no delay,
# and could be stored/handled/displayed in any way desired. I just thought it was fun to watch it "live".

