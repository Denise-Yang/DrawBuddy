#Denise Yang
#Test SVG converter

import os


def main():
    convert = os.system("vtracer --input test1.png --output output.svg")
    print("ran with exit code %d" % convert)

main()
    
