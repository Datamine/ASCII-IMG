# John Loeber | Python 2.7.6 | Debian Linux | Oct. 5 2014 | www.johnloeber.com
# -- coding: utf-8 --

from PIL import Image
import sys
from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_diff import delta_e_cie2000
from math import floor

# Takes 2 command-line args:
# (1) Name of image to be converted
# (2) Basic/Extended Ascii to be used: 'b' or 'e'

def getTerminalSize():
    """
    Finds size of terminal. Technique from http://stackoverflow.com/a/566752
    """
    import os
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))
    return int(cr[1]), int(cr[0])

def makesize(im):
    """
    Computes the ascii-dimensions of the image.
    """
    # get terminal dims
    (twidth,theight) = getTerminalSize()
    print "Console Dimensions:", (twidth,theight)
    
    scalew = float(min(twidth,im.size[0]))
    # -1 on scaleh bc/ output will always end with user@pc $ line 
    scaleh = float(min(theight-1,im.size[1]-1))
    scalebyw = scalew/im.size[0]
    scalebyh = scaleh/im.size[1]
    
    # height
    try1 = im.size[1]*scalebyw
    # width
    try2 = im.size[0]*scalebyh
    if try1 <= theight:
        tup = (scalew,try1)
    else:
        tup = (try2,scaleh)
    return (int(tup[0]),int(tup[1]))
    # can optionally choose to hardcode a scaling, like:
    #return (45,int((45.0/im.size[0])*im.size[1]))

def colormatch(color):
    """
    Converts the image-color of a pixel to an ANSI color.
    """
    # need to cast to Lab Colorspace to do color distance computation
    rgb = sRGBColor(color[0]/255.0,color[1]/255.0,color[2]/255.0)
    labcol = convert_color(rgb, LabColor)
    
    # colors, ansicodes: black, red, green, yellow, blue, magenta, cyan, gray
    colors = [(0,0,0),(205,0,0),(0,205,0),(205,205,0),(0,0,238),(205,0,205),
              (0,205,205),(229,229,229)]
    colorlist = [sRGBColor(y[0]/255.0,y[1]/255.0,y[2]/255.0) for y in colors]
    labclist = [convert_color(x, LabColor) for x in colorlist]
    ansicodes = ["\x1b[3" + str(n) + "m" for n in range(8)]
    minimum = 1000
    potentialcolor = 0
    for i in range(len(colorlist)):
        distance = delta_e_cie2000(labclist[i],labcol)
        if distance < minimum:
            minimum = distance
            potentialcolor = i
    return ansicodes[potentialcolor]

def main():
    if not (sys.argv[2]=='e' or sys.argv[2]=='b'):
            print "Error --- Improper Input."
            sys.exit(0)
    
    # ascii extended gradient from http://ashiskumar.in/code/create-ascii-gradient/
    ascii_extended = ("ÆÑÊŒØMÉËÈÃÂWQBÅæ#NÁþEÄÀHKRŽœXgÐêqÛŠÕÔA€ßpmãâG¶øðé8ÚÜ$ëdÙýè"
                      "ÓÞÖåÿÒb¥FDñáZPäšÇàhû§ÝkŸ®S9žUTe6µOyxÎ¾f4õ5ôú&aü™2ùçw©Y£0VÍ"
                      "L±3ÏÌóC@nöòs¢u‰½¼‡zJƒ%¤Itocîrjv1lí=ïì<>i7†[¿?×}*{+()\/«•¬|"
                      "!¡÷¦¯—^ª„”“~³º²–°­¹‹›;:’‘‚’˜ˆ¸…·¨´`")
    ascii_short = [a for a in ascii_extended if ord(a) < 127]
    im = Image.open(sys.argv[1])
    
    # image size
    tup = makesize(im)
    im = im.resize(tup)
    
    gray = im.convert("L") # converts img to grayscale
    x = list(gray.getdata()) #note: grayscale is on [0,255]
    colordata = list(im.getdata())  
    y,outputcolordata = [],[]

    # note that length of ascii_extended = 349; length of ascii_short = 87;
    if sys.argv[2]=='b': ratio = 86/255.0 
    else: ratio = 348/255.0 
    for i in range(len(x)):
        if sys.argv[2]=='b':
            y.append(ascii_short[int(round(ratio*x[i]))])
        elif sys.argv[2]=='e':
            y.append(ascii_extended[int(floor(ratio*x[i]))])
        outputcolordata.append(colormatch(colordata[i]))

    w,h = im.size[0], im.size[1] #tuple: width, height
    for m in range(h):
        for n in range(w):
            sys.stdout.write(outputcolordata[m*h + n])
            sys.stdout.write(y[m*h + n])
        sys.stdout.write('\n')
    
    # reset ansi escape to normal
    sys.stdout.write('\x1b[0m')

if __name__=='__main__':
    main()
