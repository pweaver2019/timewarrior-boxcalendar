# timew-boxcalendar

A timewarrior report to show the total hours logged per day in a "standard" month calendar.
Times are rounded up to the nearest quarter hour and displayed as fractions.

## Installation

Copy boxcalendar.py to your extensions directory.
To find your extensions directory use the command timew extensions which displays your extension directory and all extensions available.
If your directory is ~/.timewarrior/extensions/ then copy the source file there and make it executable.

```
cp boxcalendar.py ~/.timewarrior/extensions/boxcalendar.py
chmod +x ~/.timewarrior/extensions/boxcalendar.py
```

The command timew extensions will show if if you copied it correctly

If you name the report anything other than boxcalendar.py then use your new name in the examples below.
For example, if you name it mycalendar.py then use "reports.mycalendar.weekdays" instead of "reports.boxcalendar.weekdays."
Do not name the report calendar.py, that will cause some calls to datetime to fail.

## Usage

Use timew to run this as a report passing it a date range that contains intervals of time worked.

```
timew boxcalendar :month
timew boxcalendar :lastmonth
timew boxcalendar 2025-02-01 - 2025-03-01
timew boxcalendar january
timew boxcalendar 31d after 2025-03-01
```

## Details

The report should work without any setup.
You can change the colours by using a theme or specifying a specific colour.
You can change the weekday labels.
You can change the starting day for the week.
You can turn on verbose and/or debug mode.

### Colours

This report uses the "color" configuration to determine if we should use the theme colours.
If "color" is set then this uses the label, today and holiday colours, they should be defined already.
To modify them you can use these commands;

```
   timew config theme.colors.label "red on gray4"
   timew config theme.colors.today "underline green on red"
   timew config theme.colors.holiday rgb002
```

### Weekday Labels

The default is that week starts on Monday and the days are labeled Mo, Tu, We, Th, Fr, Sa and Su.

You can change the weekday labels by adding reports.boxcalendar.weekdays to your timewarrior.cfg.
You can specify one to three characters per day.
For instance Sunday can be Su or Sun or ☼.
Always make sure the first day in reports.boxcalendar.weekdays is Monday.

This is how you can change the labels.

```
   # This is the default setting if it is not defined
   timew config reports.boxcalendar.weekdays Mo,Tu,We,Th,Fr,Sa,Su
   # Some unicode characters work when using Courier New on PuTTY
   # They may or may not work in your OS/terminal
   timew config reports.boxcalendar.weekdays Mo,Tu,We,Th,☻,☺,☼
```

### Week Start Day

To change the start day of the report set reports.boxcalendar.start to a number from 0 through 6.
The values of the number are;
0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday

To change the starting weekday use.

```
   # Set the start day to Sunday
   timew config reports.boxcalendar.start 6
   # Set to Monday, if not defined this is the default
   timew config reports.boxcalendar.start 0
```

### Debug and verbose modes.

If verbose is on then the report turns on the Special Day list, if any, and adds debug info if debug is on.
If debug is on then the reports dumps debugging info, if verbose is also on then get more debug details.

```
   timew config verbose on
   timew config debug on
```

## Sample output


```
Calendar for June, 2025
_____________________________
|Sun|Mon|Tue|Wed|Thu|Fri|Sat|
-----------------------------
| 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| . | . | 8 | 8 | 9¼| . | . |
-----------------------------
| 8 | 9 |10 |11 |12 |13 |14 |
| . | . | 8 | . | 8 | . | . |
-----------------------------
|15 |16 |17 |18 |19 |20 |21 |
| . | 2½| 8 | 8 | 8 | 1¾| . |
-----------------------------
|22 |23 |24 |25 |26 |27 |28 |
| . | . | 8 | 8 | 8 | . | . |
----------------------------
|29 |30 |
| . | . |
---------

List of special days
2025-06-24 CA National Holiday
2025-06-25 Birthday Mom
2025-06-30 Today
```

On a terminal there would be theme.colors.holiday highlighting on the 24th, 28th.
The 30th would be highlighted based on whatever is in theme.colors.today.
The text "Calendar for June, 2025" and the text "List of special days" would be highlighted based on whatever is in theme.colors.label.
The text "List of special days" and the dates below only appear if there are special days and verbose is on.
The horizontal line of '-' characters will actually be underlines instead of the dashes shown here.

## showcolours.py

I createa a little utility to dump out the colours in a timewarrior config without needing to turn on debug mode.
Just copy it to your extensions directory, chmod +x showcolours.py, timew showcolours.

![image](https://github.com/user-attachments/assets/1596f66c-ef72-4d2b-adb6-c025e3b02f85)

## Notes

When you pass the report a range the report will create the calendar for the first year/month it finds in the range.
For example, if you use the command 'timew boxcalendar Client1 jan - apr' and there were no records with the tag Client1 in January or February, but one in March and multiple entries in April you will only get the calendar for March.
Also, if you specify an interval for part of the month you will only get totals for days that fall in that interval.
For example, 'timew boxcalendar 2025-06-10 - 2025-06-14' will only show totals for those dates, the rest of the month will show 0 hours.

This is a section of the code that looks for a tag named "Standard day" and reports that interval as eight hours.
I do this for steady clients that I dedicate one day a week for.
If that day is interrupted by another client then one day might be physically less than eight hours where the next week might be over eight hours, they get billed for eight hours per week since the time averages out over the month and they have a fixed budget for their expenses.
If you use the tag "Standard day" for another purpose you can remove that one line and the two comments above it.

To get birthdays on the report create a file named birthdays.
The file should look the sample below, the text between the 'en-' and the ":" will appear in the list of special days followed by the text after the " = " separator.
Then add a line in your timewarrior.cfg file to import this new file.

```
define holidays:
  en-Birthday:
    2025_06_25 = Mom
```

This code does nothing with the 'confirmation' config setting since it does not modify any data, only report on what it finds.

This has been tested with version 1.7.1 of timewarrior.
