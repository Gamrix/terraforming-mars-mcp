Tharsis board coordinates (full): one line per board coordinate with canonical `spaceId`, type, bonus, and restrictions.

`01` and `02` are off-board colony spaces. The Mars board itself runs from `03` to `63`.

`03` (4,0): land, +2 steel
`04` (5,0): ocean, +2 steel
`05` (6,0): land, no bonus
`06` (7,0): ocean, +1 card
`07` (8,0): ocean, no bonus
`08` (3,1): land, no bonus
`09` (4,1): volcanic area, +1 steel, volcanic-eligible space
`10` (5,1): land, no bonus
`11` (6,1): land, no bonus
`12` (7,1): land, no bonus
`13` (8,1): ocean, +2 cards
`14` (2,2): volcanic area, +1 card, volcanic-eligible space
`15` (3,2): land, no bonus
`16` (4,2): land, no bonus
`17` (5,2): land, no bonus
`18` (6,2): land, no bonus
`19` (7,2): land, no bonus
`20` (8,2): land, +1 steel
`21` (1,3): volcanic area, +1 plant, +1 titanium, volcanic-eligible space
`22` (2,3): land, +1 plant
`23` (3,3): land, +1 plant
`24` (4,3): land, +1 plant
`25` (5,3): land, +2 plants
`26` (6,3): land, +1 plant
`27` (7,3): land, +1 plant
`28` (8,3): ocean, +2 plants
`29` (0,4): volcanic area, +2 plants, volcanic-eligible space
`30` (1,4): land, +2 plants
`31` (2,4): land, +2 plants, reserved for Noctis City
`32` (3,4): ocean, +2 plants
`33` (4,4): ocean, +2 plants
`34` (5,4): ocean, +2 plants
`35` (6,4): land, +2 plants
`36` (7,4): land, +2 plants
`37` (8,4): land, +2 plants
`38` (1,5): land, +1 plant
`39` (2,5): land, +2 plants
`40` (3,5): land, +1 plant
`41` (4,5): land, +1 plant
`42` (5,5): land, +1 plant
`43` (6,5): ocean, +1 plant
`44` (7,5): ocean, +1 plant
`45` (8,5): ocean, +1 plant
`46` (2,6): land, no bonus
`47` (3,6): land, no bonus
`48` (4,6): land, no bonus
`49` (5,6): land, no bonus
`50` (6,6): land, no bonus
`51` (7,6): land, +1 plant
`52` (8,6): land, no bonus
`53` (3,7): land, +2 steel
`54` (4,7): land, no bonus
`55` (5,7): land, +1 card
`56` (6,7): land, +1 card
`57` (7,7): land, no bonus
`58` (8,7): land, +1 titanium
`59` (4,8): land, +1 steel
`60` (5,8): land, +2 steel
`61` (6,8): land, no bonus
`62` (7,8): land, no bonus
`63` (8,8): ocean, +2 titanium

How spaces relate to each other:

- The map is a 9-row hex layout with row widths 5,6,7,8,9,8,7,6,5.
- Coordinates use (x,y); y increases downward, and x is shifted by row (top row starts at x=4, middle row starts at x=0).
- Each non-edge space can have up to 6 adjacent neighbors (hex adjacency), used for city/greenery scoring and ocean adjacency MC bonuses.
- Adjacent coordinate rule: candidates are left/right `(x-1,y),(x+1,y)` plus four diagonals; for `y<4` use `(x-1,y-1),(x,y-1),(x-1,y+1),(x,y+1)`, for `y=4` use `(x-1,y-1),(x,y-1),(x,y+1),(x+1,y+1)`, for `y>4` use `(x,y-1),(x+1,y-1),(x,y+1),(x+1,y+1)`.
- Ocean spaces are fixed board slots that can only hold ocean-type tiles; land and volcanic spaces are used for most other tile placements.
- Volcanic areas are still land for normal placement, but are specifically valid for effects that require volcanic placement.
