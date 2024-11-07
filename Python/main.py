import skeletion
import depth
import sys

size = (640, 480)
skeletion.run(sys.argv[1], depth.Depth(size), size, visible=True)

