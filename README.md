# gloomhaven-monster-ai
gloomhaven boardgame monster AI

Development order:
* accept simple input -- assume infinite hexes with no walls, provide allies (with initiative), monsters, and obstacles.  Name the monster of interest and their movement.  As simple as possible
* convert input to internal representation
* build and test simple path calulation methods: distance (both "movement distance" taking difficult terrain and obstacles into account) and proximity distance, components of focus logic (targettable hexes, movement distance, initiative.
* Provide simple output containing focus, all targets (in case of multi-target attck), and possible targetting hexes (so players can decide and break a tie).  This is the bulk of the logic
* Make the input move complex, including all walls.  Check that the walls form a closed shape.
* Build a library of stock rooms that may be merged with a simpler input of monsters and allies (so that we don't need to always provide walls, obstacles, etc -- things that rarely change)
* wrap the whole thing in a GUI

initial input format proposal.  A Json list containing board elements and descriptions:
* walls as individual segments.  A wall is named by the 2 hexes whose adjacent side is a wall.  We name segments, not hexes, as adjacent valid hexes may still have a wall separating them (e.g., those next to doors).  It is assumed and validated that walls form a closed shape
* obstacles
* coins
* treasure tiles
* traps
* difficult terrain
* hazardous terrain
* closed doors
* characters and allies, including initiative (which includes 2nd card) and status (notably invisible)
* character allies and summons, including initiative
* non-moving enemies, including initiative (for heal and other ally-targetting moves)
* enemy in question, including initiative and move description.

Coordinates:
I'm going to arbitrarily choose Axial coordinates -- https://www.redblobgames.com/grids/hexagons/#coordinates-axial
I will always assume horizontal hexes (pointy tops), where (x, y) uses x as the horizontal dimension, and y is the dimension that forms a negative slope moving to the right (looks like "\").  We'll call z the dimension forming a positive slope the right (looks like "/") and this is omitted from the coordinates.
When using vertical hexes (flat tops) you must rotate the map 90 degrees to make it horizontal.  Hopefully in the future once we have a GUI we'll do this for the user.

individual component json definition: always provide an attribute "type"
* walls: name the 2 hexes whose adjoining side forms a wall: {"type" : "wall", "hex1_x" : 0, "hex1_y" : 0, "hex2_x" : 0, "hex2_y" : 1}
* obstacles: a list of the coordinates making up the obstacle: {"type" : "obstacle", "hexes" : [{"x" : 0, "y", 0}]}
* coins: hex and coin count: {"type" : "coin", "x" : 0, "y" : 0, "count" : 2}
* treasure: hex: {"type" : "treasure", "x" : 0, "y" : 0}
* traps: hex: {"type" : "trap", "x" : 0, "y" : 0}
* hazardous terrain: {"type" : "hazardous_terrain", "x" : 0, "y" : 0}
* difficult terrain: {"type" : "difficult_terrain", "x" : 0, "y" : 0}
* closed door: {"type" : "closed_door", "x" : 0, "y" : 0}
* characters and allies: {"type" : "character", "x" : 0, "y" : 0, "initiative" : 50, "secondary_initiative" : 70, "summon_rank" : 1, "is_invisible" : false}.  Notes: secondary_initiative may be omitted for allies without cards, and will be the 2nd card for characters and character summons.  summon_rank should be 0, null, or omitted for allies and characters, and will be the 1-based rank describing the order in which summons were summoned by a character; for matching initiative and secondary_initiative (assumed to be associated with the same summoner) characters move in order of summon_rank 1, 2, 3, ..., 0.
* monsters: {"type" : "monster", "x" : 0, "y" : 0, "initiative" : 50, "move" : {}}.  move will only be provided for the monster in question and should be null for all other monsters.

Let's ignore other status effects on characters and monsters right now.  If stunned don't move.  If immobilized it's usually obvious.  If disarmed move as if you have a simple melee attack.

Move description ("move" attribute of "monster" document):
A json list of the individual move components.  Each move component may have the following fields, and any of these fields may be omitted or its value null if not applicable
* attack X
* range X.  Can range 1 indicate melee or is there such a thing as range 1 (that would have disadvantage)?
* target X
* move X
* heal self X
* heal target X
* AoE description -- TBD.  Likely json documents of form {"x" : 0, "y" : 0, "is_actor" : true} where is_actor is true in only one hex (if the AoE is a melee attack, this indicates the hex where the actor must be standing).

I don't think we need to consider status effects yet.  They shouldn't impact movement.

list other move attributes:
* adjacent enemies suffer damage
* enemies adjacent to target suffer damage (can monsters do this?)
* add damage if target adjacent/not adjacent to any of the actor's allies/enemies.
