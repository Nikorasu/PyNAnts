![Preview](preview.gif "Preview")

# PyNAnts

### An Ant Simulation written in Python

This is an ant pheromone trail simulation, written in Python3,
with Pygame2 and Numpy.


**To use** save the `nants.py` file somewhere, and run via python.
(Example run command: `python3 nants_array.py`)

Left mouse click places food, right click removes food.

`Esc` key to quit.

I've included several tweakable settings near the top of the code. You can
adjust window size, fullscreen, fps, and how many ants to spawn.
The pixel resolution ratio of the pheromone trail surface is also tweakable,
although it alters how their pathfinding logic may work.

ToDo list of things that need improving/implementing:
- Obstacle/wall avoidance, especially when heading home to nest.
- Ants need to properly find and follow their own to-home trail.
- Food particles don't pickup/remove yet when ants 'grab' them.
If you have any suggestions for how to improve these, please contact me!

For more information, and future updates,
[see github page](https://github.com/Nikorasu/PyNAnts "PyNAnts").

---

        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with this program.
        If not, see: https://www.gnu.org/licenses/gpl-3.0.html

##### Copyright (c) 2021  Nikolaus Stromberg - nikorasu85@gmail.com
