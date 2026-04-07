import music21 as m21

# load mxl file
score = m21.converter.parse("Happy_Birthday_To_You_Piano.mxl")

# convert to midi
score.write("midi", "happybirthday.mid")

print("Conversion done: happybirthday.mid created")