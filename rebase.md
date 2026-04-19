# Rebase algorithm
Solver 2.0

# Matcher
- Try each combination of piece and edge placements
- Before placing the next edge check if
	- there is another edge of **the current piece** where the start is in proximity and in a 90 degree angle
	- there is another edge of **an already placed piece** where the start is in proximity and in a 0 **OR** 90 degree angle
- Consecutively place the next edge start to the current cursor position in a 0 **OR** 90 degree angle
- If the cursor ends up in the proximity of the start and the formed area is approximately A5 add this to the possible options

**Do the above loop with different margins**

- Evaluate the overlap and gap area of each option and choose the option with the least amount

The 90 degree angle placement account for diagonal corners
The continuous edge of another piece account for pieces with multiple non consecutive frame edges
