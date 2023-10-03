import numpy as np
def convert_K_to_RGB(colour_temperature):
    """
    Converts from K to RGB, algorithm pseudo-code credit to 
    http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/
    """
    #range check
    if colour_temperature < 1000: 
        return 0,0,0
    
    tmp_internal = colour_temperature / 100.0
    
    # red 
    if tmp_internal <= 66:
        red = 255
    else:
        red=tmp_internal-60
        red = 329.698727446 * (red**(-0.1332047592))
        if red < 0:
            red = 0
        elif red > 255:
            red = 255
    
    # green
    if tmp_internal <=66:
        green=tmp_internal
        green = 99.4708025861 * np.log(green) - 161.1195681661
        if green < 0:
            green = 0
        elif green > 255:
            green = 255
    else:
        green=tmp_internal-60
        green = 288.1221695283 * (green**(-0.0755148492))
        if green < 0:
            green = 0
        elif green > 255:
            green = 255
   
    # blue
    if tmp_internal >=66:
        blue = 255
    elif tmp_internal <= 19:
        blue = 0
    else:
        blue=tmp_internal-10
        blue = 138.5177312231 * np.log(blue) - 305.0447927307
        if blue < 0:
            blue = 0
        elif blue > 255:
            blue = 255   
    return red, green, blue

