#!/bin/sh

# Run this while the example 1 is running, to illustrate
# that we're reloading the images.

cp assets/pyxel_logo_altered_38x16.png assets/pyxel_logo_38x16.png
echo "Changed logo image to an altered logo"
echo "Pausing 10s"
sleep 10
cp assets/pyxel_logo_original_38x16.png assets/pyxel_logo_38x16.png    
echo "Returned to the original logo"
