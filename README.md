# PyImageViewer

Simple image viewer built in PyGame.

## Current Features
 - Drag mouse
 - Zoom on cursor
 - Reset to centre
 - Tile image (enable/disable)
 - Smoothing (enable/disable)
 - Optimisation (enable/disable)
   - Use numpy to slice the image to avoid scaling a large pygame surface
   - Reuse same surface over threshold of tiles
   - Only redraw background if image doesn't take up entire canvas

## Possible Updates
 - Optimisation
   - Mipmaps for large images
 - Preload
   - Previous image (more if browsing backwards)
   - Next image (more if browsing forwards)
 - Rotate
   - All images
   - Single
 - Saving
   - Manual
   - Toggle to autosave after rotate
 - Clipboard
   - Load image
   - Copy to
