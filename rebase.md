# Rebase algorithm
Solver 2.0

## Main
Debug - Show images of each step
Test - Show image of step then send via UART
Prod - Only UART

## ShapeDetection (with image loader)
- Grayscale (maybe also account for color -> make everything black except white)
- Blurred
- Threshold
- Disregard points out of bounding box (crop camera image to A4 place)
- Account for puzzle piece height 6mm (homography)
- Roughen the shape

**Do the above with different thresholds and take the best option**
- Area of all shapes should add up to A5 area
- Shape count should be 4 or 6

## PieceDetection
- Check biggest colinearities
- The formed line shouldn't touch another point ever again (forming hole inside or hitting rest of polygon)

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
