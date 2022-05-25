from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import palette as PT

game = Ursina()

player = FirstPersonController()
palette = PT.drawColorPalette(player = player, color_stride = 20)

sky = Sky()

ground = Entity(model = "plane",
                color = color.lime,
                texture = "grass",
                collider = "mesh",
                position = (0, 0, 0),
                scale = (50, 1, 50)
               )

my_pumpkin = Entity(model = "Pumpkin/Pumpkin.obj",
                    texture = "Pumpkin/Pumpkin_Color.png",
                    position = (3, 0, 3),
                   )


game.run()