from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from PIL.Image import ENCODERS
import numpy as np
import math
import os

this_dir, this_filename = os.path.split(__file__)

# scroll wheel to select color
# push mouse middle to change color to black or white
# push 'c' to clear all the lines 

class drawColorPalette(Entity):
    # ==entity==
    __player = 0
    pointer = 0
    __black_block = 0
    __white_block = 0
    black_select_sign = 0
    white_select_sign = 0
    __trail = 0
    # == png ===
    color_bar_png = 0
    color_bw_select_png = 0
    color_pointer_png = 0
    # ==========
    pos = 0
    length = 0
    width = 0
    color_stride = 1
    thickness = 4
    draw_color = rgb(255, 0, 0)
    draw_canvas = []    # list of draw lines
    __draw_point_set = []
    __now_black = False
    __pointer_y = 0.0    
    __pointer_y_stride = 0.0
    __color_index = 0
    __color_mtx = (np.array([[0,0,1], 
                             [0,0,0], 
                             [1,0,0]]),
                   np.array([[0,1,0], 
                             [0,0,0], 
                             [0,0,1]]),
                   np.array([[0,0,0], 
                             [1,0,0], 
                             [0,0,1]]),
                   np.array([[0,0,0], 
                             [0,0,1], 
                             [0,1,0]]),
                   np.array([[1,0,0], 
                             [0,0,1], 
                             [0,0,0]]),
                   np.array([[0,0,1], 
                             [0,1,0], 
                             [0,0,0]])
                  )

    # conver the number of self.__color_index(0 ~ 1530) to rgb                      
    def __set_rgb(self):
        num1 = self.__color_index % 256
        num2 = self.__color_index * -1 % 256
        choise = np.array([num1, num2, 255])
        self.draw_color = rgb(*(self.__color_mtx[self.__color_index // 256].dot(choise)))

    def __init__(self, player, length = 0.7, width = 0.05, pos = Vec2(0.8, 0), color_stride = 1, thickness = 4):

        self.__player = player
        self.pos = pos
        self.length = length
        self.width = width
        self.color_stride = color_stride
        self.thickness = thickness
        self.__pointer_y_stride = length / 1531 * color_stride
        # == load png ===    
        self.color_bar_png = load_texture("color_bar.png", path = this_dir)
        self.color_bw_select_png = load_texture("color_bw_select.png", path = this_dir)
        self.color_pointer_png = load_texture("color_pointer.png", path = this_dir)
        
        def draw_camera_input(key):
            if(key == Keys.scroll_up):
                self.pointer.color = color.white
                self.black_select_sign.color = color.clear
                self.white_select_sign.color = color.clear
                #self.__now_black = False
                self.__pointer_y  += self.__pointer_y_stride
                self.pointer.y = self.__pointer_y % self.length - self.length / 2
                self.__color_index = (self.__color_index + self.color_stride) % 1531
                # set global var draw_color to new color
                self.__set_rgb()
            if(key == Keys.scroll_down):   
                self.pointer.color = color.white
                self.black_select_sign.color = color.clear
                self.white_select_sign.color = color.clear
                self.__pointer_y  -= self.__pointer_y_stride
                self.pointer.y = self.__pointer_y % self.length - self.length / 2
                self.__color_index = (self.__color_index - self.color_stride) % 1531
                # set draw_color to new color
                self.__set_rgb()
            # select color
            if(key == Keys.middle_mouse_down):
                if(self.__now_black):
                    self.pointer.color = color.white33
                    self.white_select_sign.color = color.white
                    self.black_select_sign.color = color.clear
                    self.draw_color = color.white
                    self.__now_black = False
                else:
                    self.pointer.color = color.white33
                    self.black_select_sign.color = color.white
                    self.white_select_sign.color = color.clear
                    self.draw_color = color.black
                    self.__now_black = True
            if(key == Keys.right_mouse_down):
                # if draw_canvas is NOT empty
                if(self.draw_canvas):
                    destroy(self.draw_canvas[-1], delay = 0)
                    self.draw_canvas.pop()

        super().__init__(parent = camera.ui,
                         model = 'quad',
                         color = color.white,
                         texture = self.color_bar_png,
                         rotate_x = 90,
                         scale = (width, length),
                         position = pos
                        )
        self.pointer = Entity(parent = camera.ui,
                              model = 'quad',
                              color = color.white,
                              texture = self.color_pointer_png,
                              rotate_x = 90,
                              scale = (width + 0.01, 0.01),
                              position = pos + Vec2(0, length / 2)
                             )
        self.__black_block = Entity(parent = camera.ui,
                                    model = 'quad',
                                    color = color.black,
                                    rotate_x = 90,
                                    scale = width,
                                    position = pos - Vec2(0, length / 2 + 0.03)
                                   )
        self.__white_block = Entity(parent = camera.ui,
                                    model = 'quad',
                                    color = color.white,
                                    rotate_x = 90,
                                    scale = width,
                                    position = pos - Vec2(0, length / 2 + 0.04 + width)
                                   )
        self.black_select_sign = Entity(parent = camera.ui,
                                   model = 'quad',
                                   color = color.clear,
                                   texture = self.color_bw_select_png,
                                   rotate_x = 90,
                                   scale = width,
                                   position = pos - Vec2(0, length / 2 + 0.03)
                                  )
        self.white_select_sign = Entity(parent = camera.ui,
                                   model = 'quad',
                                   color = color.clear,
                                   texture = self.color_bw_select_png,
                                   rotate_x = 90,
                                   scale = width,
                                   position = pos - Vec2(0, length / 2 + 0.04 + width)
                                  )
        camera.input = draw_camera_input        

    def update(self):

        if(held_keys['c']):
            for line in self.draw_canvas:
                destroy(line, delay = 0)
        if(mouse.left):
            a = (self.__player.camera_pivot.world_rotation[0] + 90) / 180 * math.pi
            b = (self.__player.camera_pivot.world_rotation[1] * -1 + 90) / 180 * math.pi      
            pos = Vec3(math.sin(a) * math.cos(b), math.cos(a), math.sin(a) * math.sin(b)) * 3 + self.__player.position + Vec3(0, self.__player.height, 0)
            self.__draw_point_set.append(pos)
            # if __draw_point_set is NOT empty
            if(len(self.__draw_point_set) > 1):
                #draw the trail
                destroy(self.__trail, delay = 0)
                self.__trail = Entity(model = Mesh(vertices = self.__draw_point_set, mode = "line", thickness = self.thickness), color = self.draw_color)
        else:        
            # if __draw_point_set is NOT empty
            # draw points in the set        
            if(self.__draw_point_set):
                destroy(self.__trail, delay = 0)
                new_line = Entity(model = Mesh(vertices = self.__draw_point_set, mode = "line", thickness = self.thickness), color = self.draw_color)
                self.draw_canvas.append(new_line)
                self.__draw_point_set = []