# How to

1. Create .txt file containing airway definition. Coordinates need to be in decimal format. The plotter will draw the line referring to the last coordinate in this file, so it makes sense to use the COP or reference point for spacing as last coordinate in this file.
2. Run script.py by this command ```py script.py airway.txt 5```. The last digit is the requested length for dashes and spaces in nautical miles (5 NM in this case).
3. Coordinates for airway drawing will be returned in topsky line format.
