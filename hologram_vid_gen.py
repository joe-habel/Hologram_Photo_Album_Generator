import ctypes
import cv2
from math import sqrt, floor
import numpy as np
import sys
from glob import glob


def get_screen_size():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    return user32.GetSystemMetrics(1), user32.GetSystemMetrics(0)


def square_bounds(diagonal,pyramid_length,width,length):
    if width is None or length is None:
        width, length = get_screen_size()
    pixel_diag = sqrt(width**2 + length**2)
    pixel_per_inch = float(pixel_diag)/float(diagonal)
    center_x = width/2.
    center_y = length/2.
    pixel_per_side = pixel_per_inch*pyramid_length
    x_bound = (floor(center_x-pixel_per_side/2.),floor(center_x+pixel_per_side/2.))
    y_bound = (floor(center_y-pixel_per_side/2.),floor(center_y+pixel_per_side/2.))
    return (x_bound,y_bound)


def diagonals(diagonal,pyramid_length,width,length):
    x_bound,y_bound = square_bounds(diagonal,pyramid_length,width,length)
    if width is None or length is None:    
        width, length = get_screen_size()
    diags = []
    for i,a in enumerate(x_bound):
        for j,b in enumerate(y_bound):
            diag = []
            x_pos, y_pos = a, b
            diag.append((a,b))
            while x_pos != width-1 and x_pos != 0 and y_pos != length-1 and y_pos != 0:
                if i < 1 and j < 1:
                    x_pos -= 1
                    y_pos -= 1
                    diag.append((x_pos,y_pos))
                elif i < 1:
                    x_pos -= 1
                    y_pos += 1
                    diag.append((x_pos,y_pos))                    
                elif i > 0 and j < 1:
                    x_pos += 1
                    y_pos -= 1
                    diag.append((x_pos,y_pos))
                else:
                    x_pos += 1
                    y_pos += 1
                    diag.append((x_pos,y_pos))
            diags.append(diag)
    return diags, x_bound, y_bound

def find_diag_val(diags,point,axis):
    if axis == 'X':
        vals = []
        for diag in diags:
            for pair in diag:
                if pair[0] == point:
                    vals.append(pair[1])
    else:
        vals = []
        for diag in diags:
            for pair in diag:
                if pair[1] == point:
                    vals.append(pair[0])
    return vals

def add_img_bottomed(img_path,diagonal,pyramid,screen_width, screen_height):
    if screen_width is None or screen_height is None:
        screen_width, screen_height = get_screen_size()
    canvas = np.zeros((screen_width,screen_height,3))
    img = cv2.imread(img_path)
    height, width = img.shape[0], img.shape[1]
    diags, y_bound, x_bound = diagonals(diagonal,pyramid,screen_width, screen_height)
    x_min = x_bound[0]
    x_max = x_bound[1]
    y_top = y_bound[0]
    y_bottom = y_bound[1]
    x_size = x_max - x_min
    ratio = float(x_size)/float(width)
    y_size = floor(height*ratio)
    img = cv2.resize(img, (x_size,y_size))
    canvas[y_top-y_size:y_top,x_min:x_max] = img
    
    img = np.rot90(img)
    rotH, rotW = img.shape[0], img.shape[1]
    canvas[y_top:y_bottom,x_min-rotW:x_min] = img
    
    img = np.rot90(img)
    rotH, rotW = img.shape[0], img.shape[1]
    canvas[y_bottom:y_bottom+rotH,x_min:x_max] = img
    
    img = np.rot90(img)
    rotH, rotW = img.shape[0], img.shape[1]
    canvas[y_top:y_bottom,x_max:x_max+rotW] = img

    return canvas
    
def add_img_cent(img_path,diagonal,pyramid,screen_width, screen_height):
    if screen_width is None or screen_height is None:
        screen_width, screen_height = get_screen_size()
    canvas = np.zeros((screen_width,screen_height,3))
    img = cv2.imread(img_path)
    height, width = img.shape[0], img.shape[1]
    diags, y_bound, x_bound = diagonals(diagonal,pyramid,screen_width, screen_height)
    x_min = x_bound[0]
    x_max = x_bound[1]
    y_top = y_bound[0]
    y_bottom = y_bound[1]
    y1_cent = floor(y_top/2.)
    y_dist = 1
    x_dist = 1
    x1_cent = floor((x_max - x_min)/2.) + x_min
    bounding = False
    x_shift = 0
    y_shift = 0
    cutoff = min(screen_width,screen_height)
    if screen_width == cutoff:
        x_shift = floor((screen_height - cutoff) / 4.)
    else:
        y_shift = floor((screen_width - cutoff) / 4.)
    aspect = float(width)/(float(height))
    while bounding is False:
        x_dist = y_dist*(2.*aspect)
        left_x = floor(x1_cent-x_dist/2.)
        right_x = floor(x1_cent+x_dist/2.)
        points = find_diag_val(diags,floor(y1_cent+y_dist),'X')
        if points[0] >= left_x or points[1] <= right_x:
            break
        y_dist += 1
    x_size = right_x - left_x
    y_size = int(2*y_dist)
    img = cv2.resize(img, (x_size,y_size))
    canvas[y1_cent - y_dist + y_shift: y1_cent+ y_dist+y_shift, left_x: right_x] = img

    y2_cent = floor((y_bottom - y_top)/2.) + y_top
    x2_cent = floor(x_min/2.)
    img = np.rot90(img)
    rotH, rotW = img.shape[0], img.shape[1]
    canvas[floor(y2_cent-rotH/2):floor(y2_cent+rotH/2),floor(x2_cent-rotW/2)+x_shift:floor(x2_cent+rotW/2)+x_shift] = img
    

    y3_cent = floor((cutoff-y_bottom)/2.) + y_bottom
    x3_cent = floor((x_max-x_min)/2.) + x_min
    img = np.rot90(img)
    rotH, rotW = img.shape[0], img.shape[1]
    canvas[floor(y3_cent-rotH/2)+y_shift:floor(y3_cent+rotH/2)+y_shift,floor(x3_cent-rotW/2):floor(x3_cent+rotW/2)] = img    
    
    y4_cent = floor((y_bottom - y_top)/2.) + y_top
    x4_cent = floor((cutoff - x_max)/2.) + x_max
    img = np.rot90(img)
    rotH, rotW = img.shape[0], img.shape[1]
    canvas[floor(y4_cent-rotH/2):floor(y4_cent+rotH/2),floor(x4_cent-rotW/2)+x_shift:floor(x4_cent+rotW/2)+x_shift] = img
        
    return canvas
    
    
def write_video(image_directory,diagonal,pyramid,screen_width, screen_height,alignment):
    fps = 15
    fourcc = cv2.VideoWriter_fourcc('M','P','4','V')
    out = cv2.VideoWriter('photo_album.mp4', fourcc, fps, (screen_height,screen_width))
    for image in glob(image_directory + '/*.[pnjp]g'):
        if alignment is not 'B':
            holo_image = add_img_cent(image,diagonal,pyramid,screen_width,screen_height)
        else:
            holo_image = add_img_bottomed(image,diagonal,pyramid,screen_width,screen_height)
        for i in range(150):
            out.write(holo_image)
    
    out.release()
    
image_directory = sys.argv[1]
diagonal = float(sys.argv[2])
pyramid = float(sys.argv[3])
screen_height = int(sys.argv[4]) 
screen_width = int(sys.argv[5])
alignment = sys.argv[6]

write_video(image_directory,diagonal,pyramid,screen_height,screen_width,alignment)
    

                                                    
                
