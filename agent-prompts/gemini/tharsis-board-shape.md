Tharsis board coordinates (full): one line per board coordinate with type, bonus, and restrictions.

(4,0): land, +2 steel
(5,0): ocean, +2 steel
(6,0): land, no bonus
(7,0): ocean, +1 card
(8,0): ocean, no bonus
(3,1): land, no bonus
(4,1): volcanic area, +1 steel, volcanic-eligible space
(5,1): land, no bonus
(6,1): land, no bonus
(7,1): land, no bonus
(8,1): ocean, +2 cards
(2,2): volcanic area, +1 card, volcanic-eligible space
(3,2): land, no bonus
(4,2): land, no bonus
(5,2): land, no bonus
(6,2): land, no bonus
(7,2): land, no bonus
(8,2): land, +1 steel
(1,3): volcanic area, +1 plant, +1 titanium, volcanic-eligible space
(2,3): land, +1 plant
(3,3): land, +1 plant
(4,3): land, +1 plant
(5,3): land, +2 plants
(6,3): land, +1 plant
(7,3): land, +1 plant
(8,3): ocean, +2 plants
(0,4): volcanic area, +2 plants, volcanic-eligible space
(1,4): land, +2 plants
(2,4): land, +2 plants, reserved for Noctis City
(3,4): ocean, +2 plants
(4,4): ocean, +2 plants
(5,4): ocean, +2 plants
(6,4): land, +2 plants
(7,4): land, +2 plants
(8,4): land, +2 plants
(1,5): land, +1 plant
(2,5): land, +2 plants
(3,5): land, +1 plant
(4,5): land, +1 plant
(5,5): land, +1 plant
(6,5): ocean, +1 plant
(7,5): ocean, +1 plant
(8,5): ocean, +1 plant
(2,6): land, no bonus
(3,6): land, no bonus
(4,6): land, no bonus
(5,6): land, no bonus
(6,6): land, no bonus
(7,6): land, +1 plant
(8,6): land, no bonus
(3,7): land, +2 steel
(4,7): land, no bonus
(5,7): land, +1 card
(6,7): land, +1 card
(7,7): land, no bonus
(8,7): land, +1 titanium
(4,8): land, +1 steel
(5,8): land, +2 steel
(6,8): land, no bonus
(7,8): land, no bonus
(8,8): ocean, +2 titanium

How spaces relate to each other:

- The map is a 9-row hex layout with row widths 5,6,7,8,9,8,7,6,5.
- Coordinates use (x,y); y increases downward, and x is shifted by row (top row starts at x=4, middle row starts at x=0).
- Each non-edge space can have up to 6 adjacent neighbors (hex adjacency), used for city/greenery scoring and ocean adjacency MC bonuses.
- Adjacent coordinate rule: candidates are left/right `(x-1,y),(x+1,y)` plus four diagonals; for `y<4` use `(x-1,y-1),(x,y-1),(x-1,y+1),(x,y+1)`, for `y=4` use `(x-1,y-1),(x,y-1),(x,y+1),(x+1,y+1)`, for `y>4` use `(x,y-1),(x+1,y-1),(x,y+1),(x+1,y+1)`.
- Ocean spaces are fixed board slots that can only hold ocean-type tiles; land and volcanic spaces are used for most other tile placements.
- Volcanic areas are still land for normal placement, but are specifically valid for effects that require volcanic placement.
