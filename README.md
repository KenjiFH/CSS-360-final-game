Places emphasis on wave survival aspect of the game

## CHANGES:
 - Updated shotgun sound to remove high, piercing frequencies
 - Changed title name
 - Changed map to be more open and arena-like
 - Increased enemies spawned per wave. It is currently double whatever wave number it is
 - Removed enemy hp bar so player can't see them behind walls
 - Increased player speed by 33% for faster-paced gameplay
 - Increased player shotgun damage from 10 to 25. Now kills enemies in two hits instead of 5
 - Enemies now have a hit accuracy of 50%
 - Converted player taking damage hard code into a function in player.py 
 - Added a red "blood" screen indicator function in object_renderer.py when the player takes damage

## ISSUES (ranked by severity):
- Chance to spawn outside the map or in walls.
- Enemies spawn way too close to the player, instead of around the map. (This and the previous issue are probably due to some enemy spawning function not being too compatible with the map)
- You can see being unrendered too early at the left and right edges of the game screen
- Sounds are too loud, especially on stacking gunshot sounds from groups of enemies attacking at the same time
- Enemy attack rate is a bit inconsistent when they have line of sight with you