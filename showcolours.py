#!/usr/bin/env python3

# Peter Weaver, 08-JUL-2025, taken from boxcalendar.py as an easy way to see the colours used by timewarrior without turning on debug

import sys


def get_timew():
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as file_:
            data = file_.read().splitlines()
    else:
        data = sys.stdin.read().splitlines()
    line = None

    config={}

# Walk through the data, when "not value" is hit we are
# at the line between the cofig data and the json intervals
    for line, value in enumerate(data):
        if not value:
            break
        else:
            key,*value2 = value.split(': ')
            config[key] = " ".join(value2)

    if line is None:
        return

    return config


# This converts the various text colour definitions into escape sequences

def convert_colour(ground,colour):

# set the foreground or background values

    if ground == 'FG':
       ground = 38
    else:
       ground = 48

# Named colour is \033[38;5;xm where x is one of the numbers in colours_num
    colours_txt = ['nocolor', 'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    colours_num = [0,         0,       1,     2,       3,        4,      5,         6,      7]
    attributes_txt = ['bold', 'underline', 'inverse']
    attributes_num = [1,      4,            7]

    if colour in colours_txt:
        number = colours_num[colours_txt.index(colour)]
        colour = f"\033[{ground};5;{number}m"
# If the colour is bold, underline or inverse then it is an attribute
    elif colour in attributes_txt:
        number = attributes_num[attributes_txt.index(colour)]
        colour = f"\033[{number}m"
    elif colour.startswith('color'):
        number = colour[5:]
        colour = f"\033[{ground};5;{number}m"
# If the colour starts with rgb we use this syntax \033[38;5;(16 + R*36 + G*6 + B)m
    elif colour.startswith('rgb'):
        r = colour[3:4]
        g = colour[4:5]
        b = colour[5:6]
        rgb = 16 + int(r) * 36 + int(g) * 6 + int(b)
        colour = f"\033[{ground};5;{rgb}m"
# If the colour starts with 0x then we use 0xRRGGBB 0 <= R,G,B <= FF  \033[38;2;R;G;Bm
    elif colour.startswith('0x'):
        hex_value = colour[2:]
        if len(hex_value) == 6:
            r = int(hex_value[0:2], 16)
            g = int(hex_value[2:4], 16)
            b = int(hex_value[4:6], 16)
            colour = f"\033[{ground};2;{r};{g};{b}m"
        else:
            print(f"Invalid hex format: {colour}")
            return None
# grayN    0 <= N <= 23     \033[38;5;(232 + N)m
    elif colour.startswith('gray'):
        number = int(colour[4:]) + 232
        colour = f"\033[{ground};5;{number}m"
# greyN    0 <= N <= 23     \033[38;5;(232 + N)m
    elif colour.startswith('grey'):
        number = int(colour[4:]) + 232
        colour = f"\033[{ground};5;{number}m"
    elif colour == 'bright':
        colour = 'bright'
    else:
        print(f"Unknown color format: {colour}")
        return None

    return colour

def check_bright(colourescape):

    for key in colourescape:
       if colourescape[key].find('bright') > -1:
           colourescape[key].replace('bright','')
           temp = colourescape[key].split(';')
           newescape = ''
           for key2 in temp:
               if key2[1:2] == 'm':
                   colour = int(key2[0:1])
                   if colour < 8:
                       colour = colour + 8
                       newescape = newescape + str(colour) + key2[1:] + ';'
               else:
                   newescape += key2 + ';'
           if newescape[-1:] == ';': newescape=newescape[:-1]
           colourescape[key] = newescape.replace('bright','')

    return colourescape

def main():
# Start by reading in the data that timewarrior sent. The data will
# have the configuration data first, then a blank line, then the
# time intervals
    config = get_timew()

    if 'theme.description' in config: print ('Using', config['theme.description'],'\n')

    colourescape = {}
    colourescape['off'] = '\033[0m'

    for key in config:
        if key.startswith('theme.colors.') or key.startswith('theme.palette'):
            ground = 'FG'
            for colour in config[key].split():
               if colour == "on":
                  ground = 'BG'
               else:
                  if tuple((key,ground)) in colourescape.keys():
                      colourescape[key,ground] += convert_colour(ground,colour)
                  else:
                      colourescape[key,ground] = convert_colour(ground,colour)
    check_bright(colourescape)

# Dump out the colours used in this theme
    already_shown = []
    for key in colourescape:
        key2 = key[0]
        if key2 not in already_shown:
           if tuple((key2,'FG')) in colourescape and tuple((key2,'BG')) in colourescape:
               print ('Colour:',key2,'-',config[key[0]],':',colourescape[key],colourescape[tuple((key2,'BG'))],'Example Text',colourescape['off'])
               already_shown.append(key[0])
           else:
               if tuple((key2,'FG')) in colourescape or tuple((key2,'BG')) in colourescape:
                   print ('Colour:',key2,key[1],'-',config[key[0]],':',colourescape[key],'Example Text',colourescape['off'])
                   already_shown.append(key[0])



if __name__ == "__main__":
    main()
