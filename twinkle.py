from music21 import stream, note

melody = stream.Stream()

notes = [60, 60, 67, 67, 69, 69, 67,
         65, 65, 64, 64, 62, 62, 60]

for n in notes:
    melody.append(note.Note(n, quarterLength=1))

melody.write("midi", "twinkle.mid")