"""
Python Wind Computation tool
Copyright (C) 2017  Jiri Dohnalek

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import power
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.legend_handler import HandlerLine2D


def plot_day_graph(data, settings, y_max, cp):

    """
    Comparance data web scrapped from BBC Weather for the upcomming day
    """

    radius = settings[0]
    altitude = settings[1]
    location = settings[2]

    x, y = [], []
    total_pwr = 0

    for i in range(len(data)):
        # kmph to mps
        meters_per_second = data[i][3] * 0.277778
        # Power output
        watt = power.turbine_power( meters_per_second, radius, altitude, data[i][1], data[i][2], cp)
        watt = round(watt, 0)
        # Total Watts generated by the wind
        total_pwr += watt
        # Append the power
        y.append(watt)
        # Append the hour
        x.append(data[i][0])


    # create the graph
    line1, = plt.plot(y, label=location, linewidth=2)
    plt.legend(handler_map={line1: HandlerLine2D(numpoints=4)})

    # label the x and y axes
    plt.xlabel('Time (Hours)', weight='bold', size='large')
    plt.ylabel('Estimate Power(Watts)', weight='bold', size='large')

    # format the x and y ticks
    plt.xticks(range(len(y)), x, rotation=90, weight='bold', size='large')
    plt.yticks(weight='bold', size='large')

    # give it a title
    title_label = "Power Generated: %dkW, Blade Radius: %dm" % (total_pwr / 1000, radius)
    plt.title(title_label, weight='bold')

    return plt


def variable_study(study, default=None, legend=True , density=None):
    """
    study   [study type, label title, start, end , increment]
    default [wind speed, radius, altitude, temperature, humidity, power coefficient]
    """
    # VARIABLES
    x, y = [], []
    var = study[2]  # starting value
    plt.xlabel( study[1] )
    plt.ylabel('Power output (Watts)')

    if default is None:
        df = [ 10 , 0.5 , 100 , 19 , 80 , 0.4 ]
    else:
        df = default

    while var < study[3]: # study[3] = end

        if study[0]   == 'w':
            df[0] = var
        elif study[0] == 'r':
            df[1] = var
        elif study[0] == 'a':
            df[2] = var
        elif study[0] == 't':
            df[3] = var
        elif study[0] == 'h':
            df[4] = var
        elif study[0] == 'c':
            df[5] = var
        else:
            pass

        x.append(var)

        if density is None:
            y.append(power.turbine_power( df[0], df[1], df[2], df[3], df[4], df[5]))
        else:
            y.append(power.turbine_power( df[0], df[1], df[2], df[3], df[4], df[5] , density))

        var += study[4] # study[4] = increment

    if study[0]   == 'r':
        text = "Constants: v = %sm/s; alt = %sm; t = %sC; RH = %s%%; Cp = %s" % (df[0],df[2],df[3],df[4],df[5])
        plt.title('Variable Radius Study')
    elif study[0] == 'w':
        text = "Constants: r = %sm; alt = %sm; t = %sC; RH = %s%%; Cp = %s" % (df[1],df[2],df[3],df[4],df[5])
        plt.title('Variable Wind Speed Study')
    elif study[0] == 'a':
        text = "Constants: v = %sm/s; r = %sm; t = %sC; RH = %s%%; Cp = %s" % (df[0],df[1],df[3],df[4],df[5])
        plt.title('Variable Altitude Study')
    elif study[0] == 't':
        text = "Constants: v = %sm/s; r = %sm; a = %sm; RH = %s%%; Cp = %s" % (df[0],df[1],df[2],df[4],df[5])
        plt.title('Variable Temperature Study')
    elif study[0] == 'h':
        text = "Constants: v = %sm/s; r = %sm; a = %sm; t = %sC; Cp = %s" % (df[0],df[1],df[2],df[3],df[5])
        plt.title('Variable Humidity Study')
    elif study[0] == 'c':
        text = "Constants: v = %sm/s; r = %sm; a = %sm; t = %sC; RH = %s%%" % (df[0],df[1],df[2],df[3],df[4])
        plt.title('Variable Coefficient of Power Study')

    line1, = plt.plot(x, y, label = text, linewidth=2)

    if legend:
        plt.legend(handler_map={line1: HandlerLine2D(numpoints=4)})

    return plt

"""
Class Study
-----------
Enables to study the interactions between variables of the power equation.
The results are displayed in graph for the user.
"""

class study:

    _type  = ''      # type of the study represented by one letter
    _label = ''      # title of the study
    _params = []     # [start, end , increment]
    _data = []       # [wind speed, radius, altitude, temperature, humidity, power coefficient]
    _density = None  # density of fluid

    def __init__(self, type, label):
        """
        :param type: type of the study represented by one letter
        :param title: title of the study
        """
        available_study = ['r','w','a','t','h','c']

        if type in available_study:
            self._type = type
            self._label = label

    def set_fluid_density(self, density):
        """
        :param density: fluid density
        for special cases when we are not dealing with fluid as air
        """
        self._density = float(density)

    def set_parameters(self, parameters, data=None):
        """
        :param parameters: study parameters
        parameters => [start, end , increment]
        :param data: study variables
        data => [wind speed, radius, altitude, temperature, humidity, power coefficient]
        """
        self._params = parameters

        if self._data is None:
            self._data = [ 10 , 0.5 , 100 , 19 , 80 , 0.4 ]
        else:
            self._data = data

    def execute(self):
        """
        Execute the simulation and display the result on graph
        """

        # VARIABLES
        x, y = [], []
        var = self._params[0]  # starting value
        plt.xlabel( self._label )
        plt.ylabel('Power output (Watts)')

        df = self._data

        # Select the study variable
        while var < self._params[1]: # _params[3] = end

            if self._type   == 'w':
                df[0] = var
            elif self._type == 'r':
                df[1] = var
            elif self._type == 'a':
                df[2] = var
            elif self._type == 't':
                df[3] = var
            elif self._type == 'h':
                df[4] = var
            elif self._type == 'c':
                df[5] = var

            x.append(var)

            if self._density is None:
                y.append(power.turbine_power( df[0], df[1], df[2], df[3], df[4], df[5]))
            else:
                y.append(power.turbine_power( df[0], df[1], df[2], df[3], df[4], df[5] , self._density))

            var += self._params[2] # self._params[2] = incrementation value

        text = ""
        if self._type == 'r':
            text = "Constants: v = %sm/s; alt = %sm; t = %sC; RH = %s%%; Cp = %s" % (df[0], df[2], df[3], df[4], df[5])
            plt.title('Variable Radius Study')
        elif self._type == 'w':
            text = "Constants: r = %sm; alt = %sm; t = %sC; RH = %s%%; Cp = %s" % (df[1], df[2], df[3], df[4], df[5])
            plt.title('Variable Wind Speed Study')
        elif self._type == 'a':
            text = "Constants: v = %sm/s; r = %sm; t = %sC; RH = %s%%; Cp = %s" % (df[0],df[1],df[3],df[4],df[5])
            plt.title('Variable Altitude Study')
        elif self._type == 't':
            text = "Constants: v = %sm/s; r = %sm; a = %sm; RH = %s%%; Cp = %s" % (df[0],df[1],df[2],df[4],df[5])
            plt.title('Variable Temperature Study')
        elif self._type == 'h':
            text = "Constants: v = %sm/s; r = %sm; a = %sm; t = %sC; Cp = %s" % (df[0],df[1],df[2],df[3],df[5])
            plt.title('Variable Humidity Study')
        elif self._type == 'c':
            text = "Constants: v = %sm/s; r = %sm; a = %sm; t = %sC; RH = %s%%" % (df[0],df[1],df[2],df[3],df[4])
            plt.title('Variable Coefficient of Power Study')

        line1, = plt.plot(x, y, label=text, linewidth=2)

        if legend:
            plt.legend(handler_map={line1: HandlerLine2D(numpoints=4)})

        return plt
