from __future__ import division
import pygame
import numpy as np
import math
from PIL import Image
from scipy.ndimage.interpolation import zoom


def load_image( infilename ) :
    img = Image.open( infilename )
    img.load()
    data = np.asarray( img, dtype="int32" )
    return data


def save_image( npdata, outfilename ) :
    img = Image.fromarray( np.asarray( np.clip(npdata,0,255), dtype="uint8"), "L" )
    img.save( outfilename )


def intr(i):
    return int(round(i, 0))


def ceil(i):
    return int(i) + 1 if float(i) != int(i) else int(i)
    

def get_mouse_percentage(display_width, display_height, padding=0):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_x /= display_width
    mouse_y /= display_height
    if padding:
        mouse_x += padding * (mouse_x - 0.5)
        mouse_y += padding * (mouse_y - 0.5)
    return (mouse_x, mouse_y)
    

pygame.init()
display_width, display_height = 1280, 720
display = pygame.display.set_mode((display_width, display_height), pygame.RESIZABLE)
background = pygame.Surface((display_width, display_height))
background.fill((0, 0, 0))
im_path = 'checkerboard-rectangle.jpg'
#im_path = 'hires.jpg'
current_image = np.rot90(load_image(im_path))[::-1,]
x_min = y_min = 0
image_width, image_height = current_image.shape[:2]

#Toggleable options
tile = False
optimise = True
smooth = False

running = True
update = True
x_offset_temp = y_offset_temp = 0
reset = True

#Zoom options
zoom_factor = 1
zoom_speed = 1.2
zoom_displacement_x = display_width * (zoom_speed - 1)
zoom_displacement_y = display_height * (zoom_speed - 1)
zoom_padding = 0

#Set image to centre of canvas
x_offset = (display_width - image_width * zoom_factor) / 2
y_offset = (display_height - image_height * zoom_factor) / 2

mouse_held = False
refresh_background = True
pixels = 0
clock = pygame.time.Clock()
background_replace = [(0, 0, display_width, display_height)]
smooth_options = (pygame.transform.scale, pygame.transform.smoothscale)
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            continue
        if event.type == pygame.MOUSEBUTTONDOWN:
            update = True
            
            #Drag mouse
            if event.button == 1:
                mouse_x_origin, mouse_y_origin = pygame.mouse.get_pos()
                x_offset_temp = x_offset
                y_offset_temp = y_offset
                mouse_held = True
            
            #Centre image
            if event.button == 2:
                x_offset = (display_width - image_width * zoom_factor) / 2
                y_offset = (display_height - image_height * zoom_factor) / 2
                
            #Zoom in
            if event.button == 4:
                zoom_factor *= zoom_speed
                x_offset *= zoom_speed
                y_offset *= zoom_speed
                x_mult, y_mult = get_mouse_percentage(display_width, display_height, zoom_padding)
                x_offset -= x_mult * zoom_displacement_x
                y_offset -= y_mult * zoom_displacement_y
            
            #Zoom out
            if event.button == 5:
                zoom_factor /= zoom_speed
                x_offset /= zoom_speed
                y_offset /= zoom_speed
                x_mult, y_mult = get_mouse_percentage(display_width, display_height, zoom_padding)
                x_offset += x_mult * zoom_displacement_x / zoom_speed
                y_offset += y_mult * zoom_displacement_y / zoom_speed
            
            #Go back an image
            if event.button == 6:
                pass
            
            #Go forward an image
            if event.button == 7:
                pass
                
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t:
                tile = not tile
                update = True
                if tile:
                    print('Enabled image tiling.')
                else:
                    print('Disabled image tiling.')
            if event.key == pygame.K_o:
                optimise = not optimise
                update = True
                if optimise:
                    print('Enabled optimisation.')
                else:
                    print('Disabled optimisation.')
            if event.key == pygame.K_s:
                smooth = not smooth
                update = True
                if smooth:
                    print('Enabled smoothing.')
                else:
                    print('Disabled smoothing.')
    
        if event.type == pygame.VIDEORESIZE:
            display_width = event.w
            display_height = event.h
            zoom_displacement_x = display_width * (zoom_speed - 1)
            zoom_displacement_y = display_height * (zoom_speed - 1)
            display = pygame.display.set_mode((display_width, display_height), pygame.RESIZABLE)
            background = pygame.Surface((display_width, display_height))
            background.fill((0, 0, 0))
            update = True
    
    #Drag canvas
    if mouse_held and pygame.mouse.get_pressed()[0]:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x_offset = x_offset_temp + mouse_x - mouse_x_origin
        y_offset = y_offset_temp + mouse_y - mouse_y_origin
        update = True
    elif mouse_held:
        mouse_held = False
    
    if not update:
        clock.tick(60)
    
    #Update the image
    else:
        max_width = image_width * zoom_factor
        max_height = image_height * zoom_factor
        
        x_mult = image_width / max_width
        y_mult = image_height / max_height
        x_pixels = image_width / x_mult
        y_pixels = image_height / y_mult
        
        tile_coords_x = [x_offset]
        tile_coords_y = [y_offset]
        if tile:
            multiplier = -x_offset // x_pixels
            while True:
                x_start = x_offset + x_pixels * multiplier
                if x_start > display_width:
                    break
                if multiplier:
                    tile_coords_x.append(x_start)
                multiplier += 1
                
            multiplier = -y_offset // y_pixels
            while True:
                y_start = y_offset + y_pixels * multiplier
                if y_start > display_height:
                    break
                if multiplier:
                    tile_coords_y.append(y_start)
                multiplier += 1
            
        count = 0
        pixels = 0
        
        num_tiles = len(tile_coords_x) * len(tile_coords_y)
        tile_optimise = num_tiles > 1 and (num_tiles > 3 or x_pixels < display_width or y_pixels < display_height)
        
        refresh_background = not tile
        for x_current in tile_coords_x:
            for y_current in tile_coords_y:
            
                canvas_width = x_pixels
                canvas_height = y_pixels
                
                x_min = y_min = 0
                x_max, y_max = image_width, image_height
                x_origin = x_current
                y_origin = y_current
                
                #Calculate the minimum and maximum values to use as part of the array
                if optimise and not tile_optimise:
                    vis_left = x_current > 0
                    vis_right = x_current + x_pixels < display_width
                    vis_top = y_current > 0
                    vis_bottom = y_current + y_pixels < display_height
                    
                    if not any((vis_left, vis_right, vis_top, vis_bottom)):
                        refresh_background = False
                    
                    if not vis_left:
                        x_min = -x_current / zoom_factor
                        x_origin = 0
                        canvas_width -= max_width - (x_current + x_pixels)
                    if not vis_right:
                        x_max = (display_width - x_current) / zoom_factor
                        canvas_width -= max_width - zoom_factor * x_max
                    if not vis_top:
                        y_min = -y_current * y_mult
                        y_origin = 0
                        canvas_height -= max_height - (y_current + y_pixels)
                    if not vis_bottom:
                        y_max = y_mult * (display_height - y_current)
                        canvas_height -= max_height - zoom_factor * y_max
        
                
                #Only draw if image is on screen
                if canvas_width > 0 and canvas_height > 0 and x_min < x_max and y_min < y_max:
                
                    #Refersh the background once if image doesn't take entire screen
                    if refresh_background:
                        display.blit(background, (0, 0))
                        refresh_background = False
                
                    #Convert numpy array to surface
                    #Use numpy slicing for high zooms, use duplicate surfaces for many tiles
                    if not tile_optimise or not count and tile_optimise or not optimise:
                        new_array = current_image[int(x_min):ceil(x_max), int(y_min):ceil(y_max),]
                        surface = pygame.surfarray.make_surface(new_array)
                        resolution = (intr(canvas_width), intr(canvas_height))
                        try:
                            surface = smooth_options[smooth](surface, resolution)
                        except pygame.error:
                            print('Error: Width ({}) or height ({}) is too large.'.format(*resolution))
                        pixels += new_array.size
                    
                    display.blit(surface, (x_origin, y_origin))
                    count += 1
                    
        if count > 1:
            print('Drew {} tiles with tile optimisation {}'.format(count, 'enabled' if tile_optimise else 'disabled'))
        pygame.display.update()
        update = False
        clock.tick(120)
    pygame.display.set_caption('{} fps, {} pixels'.format(int(clock.get_fps()), int(pixels // 3)))
        
pygame.quit()
