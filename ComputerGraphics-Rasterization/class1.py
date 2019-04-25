from abc import ABC, abstractmethod
from PIL import Image, ImageTk
from tkinter import Tk, Frame, Menu, Button, Radiobutton, Canvas, PhotoImage, IntVar
from tkinter import LEFT, TOP, X, FLAT, RAISED, NW, RIGHT
import sys
import constants
from math import sqrt, pi, acos, modf, floor, ceil
import numpy as np

 
class Example(Frame):
  
    def __init__(self):
        super().__init__()
         
        self.initUI()

        
    def initUI(self):
      
        self.master.title(constants.APP_NAME)
        self.thickness = 5
        
        toolbar = Frame(self.master, bd=0, relief=RAISED)

        v = IntVar()
        midpoint_line_button = Radiobutton(toolbar, text="Midpoint Line",variable=v, value=1,
                                           indicatoron=0, command=self.button1_click)
        midpoint_line_button.pack(side=LEFT)

        symmetric_midpoint_line_button = Radiobutton(toolbar, text="Symmetric midpoint Line", variable=v, value=2,
            indicatoron=0, command=self.button2_click)
        symmetric_midpoint_line_button.pack(side=LEFT)

        dda_line_button = Radiobutton(toolbar, text="DDA Line", variable=v, value=3,
            indicatoron=0, command=self.button3_click)
        dda_line_button.pack(side=LEFT)

        midpoint_circle_button = Radiobutton(toolbar, text="Midpoint Circle", variable=v, value=4,
            indicatoron=0, command=self.button4_click)
        midpoint_circle_button.pack(side=LEFT)

        midpoint_circle_add_only_button = Radiobutton(toolbar, text="Midpoint Circle ADD", variable=v, value=5,
            indicatoron=0, command=self.button5_click)
        midpoint_circle_add_only_button.pack(side=LEFT)

        gupta_sproul_button = Radiobutton(toolbar, text="Gupta Sproul Line", variable=v, value=6,
            indicatoron=0, command=self.button6_click)
        gupta_sproul_button.pack(side=LEFT)

        wu_line_button = Radiobutton(toolbar, text="WU Line", variable=v, value=7,
            indicatoron=0, command=self.button7_click)
        wu_line_button.pack(side=LEFT)

        wu_circle_button = Radiobutton(toolbar, text="WU Circle", variable=v, value=8,
            indicatoron=0, command=self.button8_click)
        wu_circle_button.pack(side=LEFT)

        reset_button = Button(toolbar, text="Reset canvas", command=self.button9_click)
        reset_button.pack(side=RIGHT)

        toolbar.pack(side=TOP, fill=X)

        self.drawingArea = Canvas(self.master, cursor="circle", bg="#FFFFFF")
        self.drawingArea.pack(fill="both", expand=True)
        Tk.update(self)
        x = self.drawingArea.winfo_width()

        self.image = np.zeros([1200,1400,3],dtype=np.uint8)
        self.image.fill(255)
        self.img =  ImageTk.PhotoImage(image=Image.fromarray(self.image))
       
        self.test = self.drawingArea.create_image(0,0, anchor=NW, image=self.img, state="normal")
        self.drawingArea.bind("<Button-1>", self.setStartingPoint)
        self.drawingArea.bind("<B1-Motion>", self.drawTempLine)
        self.drawingArea.bind("<ButtonRelease-1>", self.finish_drawing)

        self.pack()
        
       
    def button1_click(self):
        self.shape = MidpointLine(self.thickness)
        self.pen = Pen((0,0,0))

    def button2_click(self):
        self.shape = SymmetricMidpointLine(self.thickness)
        self.pen = Pen((0,0,0))

    def button3_click(self):
        self.shape = DDALine(self.thickness)
        self.pen = Pen((0,0,0))
    
    def button4_click(self):
        self.shape = MidpointCircle(self.thickness)
        self.pen = Pen((0,0,0))
    
    def button5_click(self):
        self.shape = MidpointCircleAdditionsOnly(self.thickness)
        self.pen = Pen((0,0,0))

    def button6_click(self):
        self.shape = AntiAliasedGuptaSproullLine(self.thickness)
        self.pen = AntialiasedPen((255,255,255),(0,0,0))

    def button7_click(self):
        self.shape = WuAntialiasedLine(self.thickness)
        self.pen = AntialiasedPen((255,255,255),(0,0,0))

    def button8_click(self):
        self.shape = WuAntialiasedCircleDrawer(self.thickness)
        self.pen = AntialiasedPen((255,255,255),(0,0,0))
    
    def button9_click(self):
        self.image = np.zeros([1200,1920,3],dtype=np.uint8)
        self.image.fill(255)
        self.img =  ImageTk.PhotoImage(image=Image.fromarray(self.image))
        self.drawingArea.itemconfig(self.test, image=self.img)
        Tk.update(self)  

    def setStartingPoint(self, event):
        self.x_start = event.x
        self.y_start = event.y

    def drawTempLine(self, event):
        self.tmpImg = self.image.copy()
        self.shape.reset_shape()
        self.shape.draw(self.x_start, self.y_start, event.x, event.y)
        self.pen.draw_shape(self.tmpImg, self.shape.shape_pixels)
        self.img = ImageTk.PhotoImage(image=Image.fromarray(self.tmpImg))
        self.drawingArea.itemconfig(self.test, image=self.img)
        Tk.update(self)      
    
    def finish_drawing(self, event):
        self.image = self.tmpImg
        
       


class Shape(ABC):
    def __init__(self, thickness):
        self.thickness_offset = int(floor(thickness/2))
        self.shape_pixels = []
    
    @abstractmethod
    def draw(self, x_start, y_start, x_end, y_end):
        pass
    def reset_shape(self):
        self.shape_pixels = []

    def pixel_copy(self, x, y, **kwargs):      
        #Function by default expands pixels horizontally, optional argument vertical=True to switch expanding axis
        vertical = kwargs.get('vertical', False)
        self.shape_pixels.append((x, y))
        if vertical:
            for offset in range (1, self.thickness_offset):
                self.shape_pixels.append((x, y+offset))
                self.shape_pixels.append((x, y-offset))
        else:
            for offset in range (1, self.thickness_offset):
                self.shape_pixels.append((x+offset, y))
                self.shape_pixels.append((x-offset, y))

class MidpointLine(Shape):
    def draw(self, x_start, y_start, x_end, y_end):
        if abs(y_end - y_start) < abs(x_end-x_start):
            if x_start > x_end:
                self.plot_x_domain(x_end, y_end, x_start, y_start)
            else:
                self.plot_x_domain(x_start, y_start, x_end, y_end)
        else:
            if y_start > y_end:
                self.plot_y_domain(x_end, y_end, x_start, y_start)
            else:
                self.plot_y_domain(x_start, y_start, x_end, y_end)

    def plot_x_domain(self, x0, y0, x1, y1):
        dx = x1-x0
        dy = y1-y0
        yi = 1
        
        if dy<0:
            yi = -1
            dy = -dy
        
        d = 2*dy - dx
        dE = 2*dy
        dNE = 2*(dy - dx)
        y = y0

        for x in range(x0, x1):
            self.pixel_copy(x, y, vertical=True)            
            if d<0:
                d += dE
            else:
                d += dNE
                y += yi
            
    def plot_y_domain(self, x0, y0, x1, y1):
        dx = x1-x0
        dy = y1-y0
        xi = 1
        
        if dx<0:
            xi = -1
            dx = -dx
        
        d = 2*dx - dy
        dE = 2*dx
        dNE = 2*(dx - dy)
        x = x0

        for y in range(y0, y1):
            self.pixel_copy(x, y)
            if d<0:
                d += dE
            else:
                d += dNE
                x += xi
  
class SymmetricMidpointLine(MidpointLine):
    def plot_x_domain(self, x0, y0, x1, y1):
        dx = x1-x0
        dy = y1-y0
        yi = 1  
        
        if dy<0:
            yi = -1
            dy = -dy 
            
        d = 2*dy - dx
        dE = 2*dy
        dNE = 2*(dy - dx)
        y = y0 
        
        while x0 <= x1:
            self.pixel_copy(x0, y0, vertical=True)
            self.pixel_copy(x1, y1, vertical=True)
            x0 += 1
            x1 -= 1
            if d<0:
                d += dE
            else:
                d += dNE
                y0 += yi
                y1 -= yi
            
    def plot_y_domain(self, x0, y0, x1, y1):
        dx = x1-x0
        dy = y1-y0
        xi = 1

        if dx<0:
            xi = -1
            dx = -dx
            
        d = 2*dx - dy
        dE = 2*dx
        dNE = 2*(dx - dy)

        while y0 <= y1:
            self.pixel_copy(x0, y0)
            self.pixel_copy(x1, y1)
            y0 += 1
            y1 -= 1
            if d<0:
                d += dE
            else:
                d += dNE
                x0 += xi
                x1 -= xi

class DDALine(MidpointLine):
    def plot_x_domain(self, x0, y0, x1,y1):
        dx = x1 - x0
        dy = y1 - y0
        m = dy/dx       
        for x in range(x0, x1):
            self.pixel_copy(x, round(y0), vertical=True)
            y0 += m

    def plot_y_domain(self, x0, y0, x1,y1):
        dx = x1 - x0
        dy = y1 - y0
        m = dx/dy    
        for y in range(y0, y1):
            self.pixel_copy(round(x0), y)
            x0 += m

class MidpointCircle(Shape):
    def draw(self, x_start, y_start, x_end, y_end):
        x_center = round((x_start + x_end) / 2)
        y_center = round((y_start + y_start) / 2)
        radius = round(sqrt((x_start - x_end)**2 + (y_start - y_start)**2))
        self.plot_circle(x_center, y_center, radius)
    
    def plot_circle(self, x_center, y_center, radius):
        d = 1 - radius
        u = 0
        v = radius
        while v > u:
            if d < 0:
                d += 2*u + 3
            else:
                d += 2*u - 2*v + 5
                v-=1
            self.plot_symmetric_point(x_center, y_center, u, v)
            u += 1

    def plot_symmetric_point(self, x_center, y_center, u, v):
        #Top and bottom, horizontal orientation, vertical expand
        self.pixel_copy(x_center + u,y_center + v, vertical=True)
        self.pixel_copy(x_center - u,y_center + v, vertical=True)
        self.pixel_copy(x_center + u,y_center - v, vertical=True)
        self.pixel_copy(x_center - u,y_center - v, vertical=True)

        #If the line is thick, there is too much space at the quadrants intersections, need to fill it, hence additional copy
        if u+self.thickness_offset*2 > v:
            self.pixel_copy(x_center + u,y_center + v)
            self.pixel_copy(x_center - u,y_center + v)
            self.pixel_copy(x_center + u,y_center - v)
            self.pixel_copy(x_center - u,y_center - v)
        
        #Left and right, vertical orientation    
        self.pixel_copy(x_center + v,y_center + u)
        self.pixel_copy(x_center - v,y_center + u)
        self.pixel_copy(x_center + v,y_center - u)
        self.pixel_copy(x_center - v,y_center - u)  

class MidpointCircleAdditionsOnly(MidpointCircle):
    #Different version of an algorithm, no floating point multiplications in a loop
    def plot_circle(self, x_center, y_center, radius):
        dE = 3
        dSE = 5-2*radius
        d = 1 - radius
        u = 0
        v = radius
        while v > u:
            if d < 0:
                d += dE
                dSE += 2
            else:
                d += dSE
                dSE += 4
                v -= 1
            self.plot_symmetric_point(x_center, y_center, u, v)
            dE += 2
            u += 1

class AntiAliasedGuptaSproullLine(Shape):
    def draw(self, x_start, y_start, x_end, y_end):
        if self.thickness_offset == 0:
            self.thickness_offset = 1

        if abs(y_end - y_start) < abs(x_end-x_start):
            if x_start > x_end:
                self.plot_x_domain(x_end, y_end, x_start, y_start, self.thickness_offset)
            else:
                self.plot_x_domain(x_start, y_start, x_end, y_end, self.thickness_offset)
        else:
            if y_start > y_end:
                self.plot_y_domain(x_end, y_end, x_start, y_start, self.thickness_offset)
            else:
                self.plot_y_domain(x_start, y_start, x_end, y_end, self.thickness_offset)

    def plot_x_domain(self,x0, y0, x1, y1, thickness_offset):
        dx = x1 - x0
        dy = y1 - y0
        yi = 1
        
        if dy<0:
            yi = -1
            dy = -dy
        dE = 2*dy
        dNE = 2*(dy-dx)
        d = 2*dy - dx        
        two_v_dx = 0
        inverted_denominator = 1/(2*sqrt(dx**2 + dy**2))
        two_dx_inverted_denominator = 2 * dx * inverted_denominator
        while x0 < x1:
            i = 1
            self.__intensify_pixel(x0, y0, thickness_offset, two_v_dx * inverted_denominator)
            while self.__intensify_pixel(x0, y0 + i, thickness_offset, i*two_dx_inverted_denominator - yi*two_v_dx*inverted_denominator):
                i += 1
            i = 1
            while self.__intensify_pixel(x0, y0 - i, thickness_offset, i*two_dx_inverted_denominator + yi*two_v_dx*inverted_denominator):
                i += 1           
            x0 += 1
            if d < 0:
                two_v_dx = d + dx
                d += dE
            else:
                two_v_dx = d - dx
                d += dNE
                y0 += yi
    
    def plot_y_domain(self,x0, y0, x1, y1, thickness):
        dx = x1 - x0
        dy = y1 - y0
        xi = 1
        
        if dx<0:
            xi = -1
            dx = -dx

        dE = 2*dx
        dNE = 2*(dx-dy)
        d = 2*dx - dy
        two_v_dy = 0
        inverted_denominator = 1/(2*sqrt(dy**2 + dx**2))
        two_dy_inverted_denominator = 2 * dy * inverted_denominator
        while y0 < y1:
            i = 1
            self.__intensify_pixel(x0, y0, thickness, two_v_dy * inverted_denominator)
            while self.__intensify_pixel(x0 + i, y0, thickness, i*two_dy_inverted_denominator - xi*two_v_dy*inverted_denominator):
                i += 1
            i = 1
            while self.__intensify_pixel(x0 - i, y0, thickness, i*two_dy_inverted_denominator + xi*two_v_dy*inverted_denominator):
                i+=1
           
            y0 += 1
            if d < 0:
                two_v_dy = d + dy
                d += dE
            else:
                two_v_dy = d - dy
                d += dNE
                x0 += xi

    
    def __intensify_pixel(self, x, y, thickness_offset, distance):
        radius = 0.5
        cov = self.__coverage(thickness_offset, distance, radius)
        if cov > 0:
            self.shape_pixels.append((x,y,cov))
            return True
        else:
            return False

    def __coverage(self, thickness, distance, radius):
        if thickness > radius:
            if thickness < distance:
                return self.__cov(distance - thickness, radius)
            else:
                return 1 - self.__cov(thickness - distance, radius)
        else:
            if distance < thickness:
                return 1 - self.__cov(thickness - distance, radius) - self.__cov(thickness + distance, radius)
            elif distance < radius - thickness:
                return self.__cov(distance - thickness, radius) - self.__cov(distance + thickness, radius)
            else:
                return self.__cov(distance - thickness, radius)
        
    def __cov(self, d, radius):
        if d < radius:
            return (1/pi) * acos(d/radius) - (d/(pi*radius**2))*sqrt(radius**2-d**2)
        else:
            return 0

    


class WuAntialiasedLine(MidpointLine):
    def plot_x_domain(self, x0, y0, x1, y1):
        dx = x1 - x0
        dy = y1 - y0
        if dx != 0:
            m = dy/dx
        else:
            m = 1
        while x0 < x1:
            self.shape_pixels.append((x0, floor(y0), 1 - modf(y0)[0]))
            self.shape_pixels.append((x0, floor(y0) + 1, modf(y0)[0]))
            y0 += m
            x0 += 1
    
    def plot_y_domain(self, x0, y0, x1, y1):
        dx = x1 - x0
        dy = y1 - y0
        if dy != 0:
            m = dx/dy
        else:
            m = 1
        while y0 < y1:
            self.shape_pixels.append((floor(x0), y0, 1 - modf(x0)[0]))
            self.shape_pixels.append((floor(x0) + 1, y0, modf(x0)[0]))
            x0 += m
            y0 += 1


class WuAntialiasedCircleDrawer(MidpointCircle):
    def draw(self, x_start, y_start, x_end, y_end):
        x_center = round((x_start + x_end) / 2)
        y_center = round((y_start + y_start) / 2)
        radius = round(sqrt((x_start - x_end)**2 + (y_start - y_start)**2))
        self.__plot_circle(x_center, y_center, radius)
        
    def __plot_circle(self, x_center, y_center, radius):
        x = 0
        y = radius
        self.shape_pixels.append((x_center, y_center + y, 1))
        self.shape_pixels.append((x_center, y_center - y, 1))
        self.shape_pixels.append((x_center - y, y_center, 1))
        self.shape_pixels.append((x_center + y, y_center, 1))
        while y > x:
            x += 1
            y = ceil(sqrt(radius**2 - x**2))
            T = y - sqrt(radius**2 - x**2)
            
            self.shape_pixels.append((x_center + x, y_center + y, 1-T))
            self.shape_pixels.append((x_center + x, y_center + y - 1, T))
            
            self.shape_pixels.append((x_center - x, y_center + y, 1-T))
            self.shape_pixels.append((x_center - x, y_center + y - 1, T))
            
            self.shape_pixels.append((x_center + x, y_center - y, 1-T))
            self.shape_pixels.append((x_center + x, y_center - y + 1, T))

            self.shape_pixels.append((x_center - x, y_center - y, 1-T))
            self.shape_pixels.append((x_center - x, y_center - y + 1, T))
            
            self.shape_pixels.append((x_center + y, y_center + x, 1-T))
            self.shape_pixels.append((x_center + y - 1, y_center + x, T))
            
            self.shape_pixels.append((x_center - y, y_center + x, 1-T))
            self.shape_pixels.append((x_center - y + 1, y_center + x, T))
            
            self.shape_pixels.append((x_center + y, y_center - x, 1-T))
            self.shape_pixels.append((x_center + y - 1, y_center - x, T))

            self.shape_pixels.append((x_center - y, y_center - x, 1-T))
            self.shape_pixels.append((x_center - y + 1, y_center - x, T))
             

class Pen(object):
    def __init__(self, color):
        self.color = color;
    def draw_shape(self, image_pixels, shape):
        for point in shape:
            x,y = point
            image_pixels[y,x] = self.color

class AntialiasedPen(object):
    def __init__(self, bg_color, drawing_color):
        self.bg_color = bg_color
        self.drawing_color = drawing_color

    def draw_shape(self, image_pixels, shape):
        for point in shape:
            x, y, factor = point
            image_pixels[y, x] = self.__lerp(self.bg_color, self.drawing_color, factor)
    
    def __lerp(self, color1, color2, factor):
       
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        
        new_red = round((r2 - r1) * factor + r1)
        new_green = round((g2 - g1) * factor + g1)
        new_blue = round((b2 - b1) * factor + b1)
       
        return (new_red, new_green, new_blue)


def main():
  
    root = Tk()
    root.geometry("1200x800")
    app = Example()
    root.mainloop()  

