#!/bin/sh

# Run this while the example 1 is running, to illustrate
# that we're reloading the images.

cp assets/urban_rpg_altered.png assets/urban_rpg.png
echo "Changed logo image to an altered logo"
echo "Pausing 10s"
sleep 10
cp assets/urban_rpg_original.png assets/urban_rpg.png    
echo "Returned to the original logo"
