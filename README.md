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
