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
    
pygame.init()

width, height = 720, 720

display = pygame.display.set_mode((width, height))
im_path = 'checkerboard-pattern.jpg'
current_image = np.rot90(load_image(im_path))[::-1,]
x_min = y_min = 0
image_size = x_max, y_max = current_image.shape[:2][::-1]


running = True
update = True
zoom_factor = 0.5
x_offset = y_offset = -50
tile = False
optimise = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            continue
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_LCTRL]:
                    x_offset += 40
                elif pressed[pygame.K_LSHIFT]:
                    y_offset -= 40
                else:
                    zoom_factor *= 1.1
                update = True
            if event.button == 5:
                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_LCTRL]:
                    x_offset -= 40
                elif pressed[pygame.K_LSHIFT]:
                    y_offset += 40
                else:
                    zoom_factor /= 1.1
                update = True
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
    
    if update:
        display.fill((0, 0, 0))
        max_width = width * zoom_factor
        max_height = height * zoom_factor
        canvas_width = width / zoom_factor
        canvas_height = height / zoom_factor
        x_mult = image_size[0] / max_width
        y_mult = image_size[1] / max_height
        
        tile_coords_x = [x_offset]
        tile_coords_y = [y_offset]
        
        x_pixels = image_size[0] / x_mult
        y_pixels = image_size[1] / y_mult
        
        if tile:
            #Get positive x tiles
            multiplier = 1
            while True:
                new_x = x_pixels * multiplier - x_offset
                if new_x > width:
                    break
                tile_coords_x.append(-new_x)
                multiplier += 1
                
            #Get negative x tiles
            multiplier = -1
            while True:
                new_x = x_pixels * multiplier - x_offset
                if new_x + x_pixels < 0:
                    break
                tile_coords_x.append(-new_x)
                multiplier -= 1
                
            #Get positive y tiles
            multiplier = 1
            while True:
                new_y = y_pixels * multiplier - y_offset
                if new_y > width:
                    break
                tile_coords_y.append(-new_y)
                multiplier += 1
                
            #Get negative y tiles
            multiplier = -1
            while True:
                new_y = y_pixels * multiplier - y_offset
                if new_y + y_pixels < 0:
                    break
                tile_coords_y.append(-new_y)
                multiplier -= 1
        
        count = 0
        pixels = 0
        tile_optimise = len(tile_coords_x) > 2 and len(tile_coords_y) > 2
        for x_current in tile_coords_x:
            for y_current in tile_coords_y:
                new_width = max_width
                new_height = max_height
                
                #Set to max size if tiled
                if tile_optimise or not optimise:
                    x_origin = -x_current
                    x_min = 0
                    x_max = image_size[0]
                    copy_image = True
                
                #Calculate x offset and slicing
                else:
                    if x_current <= 0:
                        x_origin = -x_current
                        x_min = 0
                        
                        #Canvas contains left of image
                        if x_origin + x_pixels > width:
                            new_width = width + x_current
                            x_max = image_size[0] * new_width / max_width
                        
                        #Whole image on canvas
                        else:
                            x_max = image_size[0]
                            new_width = min(width, new_width)
                            
                    #Trim left side of canvas
                    else:
                        x_origin = 0
                        x_min = x_current * x_mult
                    
                        if x_pixels > width:
                        
                            #Entire canvas is inside image
                            if x_current + width <= max_width:
                                new_width = width
                                x_max = image_size[0] * (new_width + x_current) / max_width
                                
                            #Canvas contains right of image
                            else:
                                x_max = image_size[0]
                                new_width = (x_max - x_min) / x_mult
                       
                        #Image crosses left side of canvas
                        else:
                            x_max = image_size[0]
                            new_width -= x_current
                
                
                #Set to max size if tiled
                if tile_optimise or not optimise:
                    y_origin = -y_current
                    y_min = 0
                    y_max = image_size[1]
                
                #Calculate y offset and slicing
                else:
                    if y_current <= 0:
                        y_origin = -y_current
                        y_min = 0
                        
                        #Image crosses bottom of canvas
                        if y_origin + y_pixels > height:
                            new_height = height + y_current
                            y_max = image_size[1] * new_height / max_height
                        
                        #Whole image on canvas
                        else:
                            y_max = image_size[1]
                            new_height = min(height, new_height)
                            
                    else:
                        y_origin = 0
                        y_min = y_current * y_mult
                    
                        if y_pixels > height:
                        
                            #Entire canvas is inside image
                            if y_current + height <= max_height:
                                new_height = height
                                y_max = image_size[1] * (new_height + y_current) / max_height
                                
                            #Canvas contains bottom of image
                            else:
                                y_max = image_size[1]
                                new_height = (y_max - y_min) / y_mult
                       
                        #Image crosses top of canvas
                        else:
                            y_max = image_size[1]
                            new_height -= y_current
                
                #Only draw if image is on screen
                if new_width > 0 and new_height > 0 and x_min < x_max and y_min < y_max:
                    
                    #Convert numpy array to surface
                    #Use numpy slicing for high zooms, use duplicate surfaces for many tiles
                    if not tile_optimise or not count and tile_optimise or not optimise:
                        new_array = current_image[int(x_min):ceil(x_max), int(y_min):ceil(y_max),]
                        surface = pygame.surfarray.make_surface(new_array)
                        resolution = (intr(new_width), intr(new_height))
                        try:
                            surface = pygame.transform.scale(surface, resolution)
                        except pygame.error:
                            print('Error with width ({}) or height ({}).'.format(*resolution))
                        pixels += new_array.size
                    
                    display.blit(surface, (x_origin, y_origin))
                    count += 1
        if count > 1:
            print('Drew {} tiles'.format(count))
        if pixels:
            pygame.display.set_caption('Drawn pixels: {}'.format(pixels))
        pygame.display.update()
        update = False
        
pygame.quit()
