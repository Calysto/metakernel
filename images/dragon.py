from Graphics import *
from Myro import show

# positive to left
def dragon(arrow, level=4, size=200, direction=45):
    if level:
        arrow.rotate(direction)
        dragon(arrow, level-1, size/1.41421356237, 45)
        arrow.rotate(-direction * 2)
        dragon(arrow, level-1, size/1.41421356237, -45)
        arrow.rotate(direction)
    else:
        arrow.forward(size)

def draw_dragon4(center, size, counts, colors, angle=0):
    for color, count in zip(colors, counts):
        if color is not None:
            arrow = Arrow(center)
            arrow.pen.color = Color(color)
            arrow.penDown()
            arrow.draw(win)
            arrow.rotate(angle + 45)
            dragon(arrow, count, size)
            arrow.penUp()
            arrow.undraw()
        angle += 90

def makePicture(size):
    global win
    size2 = size / 2

    win = Window(size, size)
    bg = "white"
    win.setBackground(Color(bg))
    win.Hide()

    blue = Color(36, 136, 192)
    yellow = Color(255, 199, 0)

    darkblue = Color(35, 115, 160)
    darkyellow = Color(211, 166, 0)

    angle = -90
    # Shadow:
    if size > 128:
        scolor = darkblue
        yscolor = darkyellow
        draw_dragon4((size2 - 0, size2 + 2), size2, [16] * 4, [None, scolor, None, yscolor], angle)
        draw_dragon4((size2 + 2, size2 - 0), size2, [16] * 4, [None, scolor, None, yscolor], angle)
        draw_dragon4((size2 - 2, size2 + 0), size2, [16] * 4, [None, scolor, None, yscolor], angle)
        draw_dragon4((size2 + 0, size2 - 2), size2, [16] * 4, [None, scolor, None, yscolor], angle)

    draw_dragon4((size2, size2), size2, [16] * 4, [None, blue, None, None], angle)
    draw_dragon4((size2, size2), size2, [16] * 4, [None, None, None, yellow], angle)

    pic = Picture(win)
    pic.setTransparent(Color(bg))
    #pic.flipHorizontal()
    #show(pic)
    pic.savePicture("logo-%dx%d.png" % (size, size))
    return pic



for size in [32, 64]: # 16, 32, 64, 128, 256, 512]:
    pic = makePicture(size)
    show(pic, "%sx%s" % (size, size))
    #pic.savePicture("metakernel-logo-%sx%s.gif" % (size, size))
    #pic.savePicture("metakernel-logo-%sx%s.jpg" % (size, size))
