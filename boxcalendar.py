#!/usr/bin/env python3

# Peter Weaver, 08-JUN-2025

# named boxcalendar.py because naming it calendar.py broke datetime

# Examples of how to use.
#   timew boxcalendar :lastmonth
#   timew boxcalendar :month
#   timew boxcalendar 2025-02-01 - 2025-03-01
#   timew boxcalendar january
#   timew boxcalendar 31d after 2025-02-01
#
# This uses the label, today and holiday colours, they should be defined already,
# to modify them these commands work.
#   timew config theme.colors.label "red on gray4"
#   timew config theme.colors.today "black on yellow"
#   timew config theme.colors.holiday rgb002
#
# The weekday labels can change and the week start day can change.
# Use one to three characters for each day of the week in reports.boxcalendar.weekdays.
# This is how you can change the labels
#    timew config reports.boxcalendar.weekdays Mo,Tu,We,Th,Fr,Sa,Su # if not defined this is the default
#    timew config reports.boxcalendar.weekdays Mo,Tu,We,Th,☻,☺,☼ # some unicode characters work when using Courier New on PuTTY
# The week start date can be changed by specifying the number of the weekday to use
# 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday
#    timew config reports.boxcalendar.start 6 # Sunday
#    timew config reports.boxcalendar.start 0 # Monday if not defined this is the default
#
# Debug and verbose modes.
# timew config verbose on # turns on Special Day list, if any and adds debug info if debug is on
# timew config debug on # dumps debugging info, if verbose is also on then get more debug details

import datetime
import json
import sys
import os


# Get the full path to the current script
full_path = __file__

# figure out what config entries we should be using
report_name = os.path.basename(full_path)
config_name = os.path.splitext(report_name)[0]
config_start = 'reports.' + config_name + '.start'
config_weekdays = 'reports.' + config_name + '.weekdays'

# This gets the data that was passed by timewarior,
# walks through it, putting the first part into
# the config dictionary, then when it finds the
# blank line it puts the rest of the json data
# into the data list.

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

    jsondata = json.loads("".join(data[line:]))

    return jsondata,config


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


# The timewarrior guidelines say that 'on','1','yes','y',and 'true' are all
# treated as True, all other values are False.
def check_true(invalue):
    truevalues = ['on','1','yes','y','true']
    tmpvalue = False
    for value in truevalues:
        if invalue.lower() == value:
           tmpvalue = True
           break

    return tmpvalue

# If the date passed matches today return True
def check_today(invalue):
    tmpvalue = False
    if invalue.strftime('%Y-%m-%d') == datetime.date.today().strftime('%Y-%m-%d'):
        tmpvalue = True

    return tmpvalue

# If the date passes matches a loaded holiday then return True
# Note that this only tells us if we have a holiday on this date,
# since there might be duplicates we walk through the list in
# the special dates section
def check_holiday(invalue,holidays):
    tmpvalue = False
    invalue_str = invalue.strftime('%Y_%m_%d')
    if invalue_str in holidays:
       tmpvalue = True

    return tmpvalue

def main():
# Start by reading in the data that timewarrior sent. The data will
# have the configuration data first, then a blank line, then the
# time intervals
    data,config = get_timew()

# if we did not get any intervals from timew then there is nothing to do
    if len(data) == 0:
        print("No data selected")
        return

# Change debug, verbose and color into boolean
    config['debug'] = check_true(config['debug'])
    config['verbose'] = check_true(config['verbose'])
    config['color'] = check_true(config['color'])

# Display debug messages if needed
    if config['debug']: print('Debug is enabled')

    if config['debug']: print('We are using config',config_weekdays,'and',config_start)

    if config['debug'] and config['verbose']: print ("data=",data)
    if config['debug'] and config['verbose']: print ("config",config)

    if config['debug']: print("Week start =",config[config_start])

# setup default escape sequences in case config['color'] is not set
# or some colours are not defined
    colourescape={}

    colourescape['theme.colors.holiday','FG'] = ''
    colourescape['theme.colors.holiday','BG'] = ''
    colourescape['theme.colors.label','FG'] = ''
    colourescape['theme.colors.label','BG'] = ''
    colourescape['theme.colors.today','FG'] = ''
    colourescape['theme.colors.today','BG'] = ''
    colourescape['underline'] = '\033[4m'
    colourescape['off'] = '\033[0m'

# If colour is enabled in the confuration file then load all the colours, the only colours
# used are the ones listed above
    if config['color']:
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
    if config['debug'] and config['verbose']:
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

#       for key in colourescape:
#           print (f"Colour: {key}: {colourescape[key]}Example Text{colourescape['off']}")
    # print(colourescape)

# Create a dictionary of the holidays loaded, if more than one holiday per date we create a
# sub dictionary
    holidays = {}
    for key in config:
        if key.startswith('holidays.'):
           tmpvalue = key.split(".")
           if tmpvalue[2] not in holidays:
               holidays[tmpvalue[2]]={}
               holidays[tmpvalue[2]]['maxforday'] = 0
               i = 0
           else:
               holidays[tmpvalue[2]]['maxforday'] += 1

           tmpmax = holidays[tmpvalue[2]]['maxforday'] # just to make the next lines readable
           holidays[tmpvalue[2]][tmpmax]={}
           holidays[tmpvalue[2]][tmpmax]['country']=tmpvalue[1]
           holidays[tmpvalue[2]][tmpmax]['description']=config[key]
    if config['debug'] and config['verbose']: print(holidays)
    if config['debug']:
        print("temp.report.start=",config['temp.report.start'])
        print("temp.report.end=",config['temp.report.end'])

# Create a list of the hours for each day that we have an interval for
    month_hours = {}
    have_month = False

    for interval in data:
        if "start" not in interval:
            print("No start date found in the data.")
            return
        else:
            starttime = datetime.datetime.strptime(interval["start"],"%Y%m%dT%H%M%SZ")
            starttime = starttime.replace(tzinfo=datetime.timezone.utc)
            starttime = starttime.astimezone()
            startmonth = starttime.strftime("%m")
            startyear = starttime.strftime("%Y")
            startday = starttime.strftime("%d")

# Force an end time if we have an open item
        if "end" not in interval:
            interval["end"] = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")

        endday = datetime.datetime.strptime(interval["end"],"%Y%m%dT%H%M%SZ")
        endday = endday.replace(tzinfo=datetime.timezone.utc)
        endday = endday.astimezone()

# Create some variables based on the first record we hit
        if not have_month:
            have_month = True
            first_month = startmonth
            first_year = startyear
            first_day = starttime.replace(day=1)
# Add 31 days to the first day which will get us to the next month,
# then replace the day part with 1, so that gives us the first day
# of the next month, then subtract one day to get the last day of
# the month.
            last_day_of_month = first_day + datetime.timedelta(days=31)
            last_day_of_month = last_day_of_month.replace(day=1) - datetime.timedelta(days=1)
            first_monthtxt = first_day.strftime('%B')

            if (config['debug']): print("month:", first_month, "year:", first_year, "first_day:", first_day.strftime('%Y-%m-%d'), "last_day:", last_day_of_month.strftime('%Y-%m-%d'))

        if "duration" in interval:
            duration = datetime.timedelta(seconds=interval["duration"])
        else:
            duration = endday - starttime

# Special code for me, if the tag is "Standard day" then set the hours to 8 no matter
# how many hours were worked for that customer that day.
        if "Standard day" in interval["tags"]: duration = datetime.timedelta(hours=8.0)

        if startmonth == first_month and startyear == first_year:

            if startday not in month_hours:
                month_hours[startday] = duration
            else:
                month_hours[startday] += duration

# Create an list of days in the month filling in the time worked
# if we have any time that day
    month_days = []
    for day in range(1, 32):
        if f"{day:02d}" in month_hours:
            month_days.append(month_hours[f"{day:02d}"])
        else:
            month_days.append(datetime.timedelta(seconds=0))

    if config_weekdays in config:
        config[config_weekdays] = config[config_weekdays].split(',')
    else:
        config[config_weekdays] = ['Mo','Tu','We','Th','Fr','Sa','Su']

    if config_start in config:
       if config['debug']: print('we have .start in the config file')
       weekoffset = config[config_start]
    else:
       weekoffset = 0

    i = int(weekoffset) - 1
    dayheading = "|" + f"{colourescape['underline']}"
    for _ in range(7):
       i += 1
       if i > 6: i = 0
       tmpfield = config[config_weekdays][i]
       dayheading += f"{tmpfield[:3]:<3}" + "|"

    dayheading += f"{colourescape['off']}"

# print the heading with the month, year and days of the week

    print(f"{colourescape['theme.colors.label','FG']}{colourescape['theme.colors.label','BG']}Calendar for {first_monthtxt}, {first_year}{colourescape['off']}",sep="")
    print("_____________________________")
    print(dayheading)
    current_day = first_day

    specialdaylist = []

    hour_line = colourescape['underline']

    first_day_of_week = first_day.weekday() - int(weekoffset)
    if first_day_of_week < 0: first_day_of_week += 7

    # Print leading spaces for the first week
    for _ in range(first_day_of_week):
        print("|   ", end="")
        hour_line = hour_line + "|   "
    # Print the days of the month

    last_day_of_week = int(weekoffset) - 1
    if last_day_of_week < 0: last_day_of_week += 6

    after_first_day = False

    while current_day <= last_day_of_month:

        if current_day.weekday() == int(weekoffset) and after_first_day:
            print ("|")
            print (hour_line,'|',colourescape['off'], sep="")
            hour_line=colourescape['underline']

        if check_today(current_day):
           todayon = colourescape['theme.colors.today','FG'] + colourescape['theme.colors.today','BG']
           todayoff = colourescape['off']
           specialdaylist.append (current_day.strftime('%Y-%m-%d') + ' Today')

        else:
           todayon = ''
           todayoff = ''
        if check_holiday(current_day,holidays):
           holidayon = colourescape['theme.colors.holiday','FG'] + colourescape['theme.colors.holiday','BG']
           holidayoff = colourescape['off']
# Walk through the whole holiday list in case there is more than one to report
           searchdate = current_day.strftime('%Y_%m_%d')
           for key in holidays:
               if key == searchdate:
                   for i in range(holidays[key]['maxforday'] + 1):
                       specialdaylist.append (current_day.strftime('%Y-%m-%d') + ' ' + holidays[key][i]['country'] +' ' + holidays[key][i]['description'])
        else:
           holidayon = ''
           holidayoff = ''

        print("|",f"{todayon}{holidayon}{current_day.day:2d}{todayoff}{holidayoff}",sep="", end=" ")

        hours_today = month_days[current_day.day - 1].total_seconds() / 3600
        if hours_today == 0:
            hour_line = hour_line + "| . "
        else:
            hours_fraction = hours_today % 1
            minutes = hours_fraction * 60
            hour_line = hour_line + "|" + f"{int(hours_today):2d}"
            # print("hours_fraction",hours_fraction,"hours_today=",hours_today)
            if minutes == 0:
                hour_line = hour_line + " "
            elif minutes < 16:
                hour_line = hour_line + "\u00BC"  # 1/4
            elif minutes >= 16 and minutes < 31:
                hour_line = hour_line + "\u00BD"  # 1/2
            elif minutes >= 31 and minutes < 46:
                hour_line = hour_line + "\u00BE"  # 3/4
            else:
                hour_line = hour_line[:-2]
                hour_line = hour_line + f"{int(hours_today+1):2d} "  # round up to the next hour

        if current_day.strftime('%Y-%m-%d') >= last_day_of_month.strftime('%Y-%m-%d'):
            print("|  ")
            print (hour_line,"|",colourescape['off'],sep="")



        current_day += datetime.timedelta(days=1)
        after_first_day = True

    if config['verbose']:
        if len(specialdaylist) > 0:
            print ('')
            print (f"{colourescape['theme.colors.label','FG']}{colourescape['theme.colors.label','BG']}List of special days{colourescape['off']}")
            for item in specialdaylist:
                print (item)


    if (config['debug']):
       print(f"End of interval: {endday.strftime('%Y-%m-%d %H:%M:%S')}")
       print("Unicode for fractions are: 1/4=\u00BC, 1/2=\u00BD, 3/4=\u00BE")
       print("Unicode for happy face=\u263A, reverse happy face=\u263B, Sun=\u263C")


if __name__ == "__main__":
    main()
