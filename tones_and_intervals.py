

"""
This code implements music.
"""

import re


# Relates interval names with number of semi-tones
# We will use code later to modify it for higher octaves
distances = {'p1': 0,
             'a1': 1,
             'd2': 1,
             'p2': 2,
             'a2': 3,
             'd3': 3,
             'p3': 4,
             'd4': 4,
             'a3': 5,
             'p4': 5,
             'a4': 6,
             'd5': 6,
             'p5': 7,
             'a5': 8,
             'd6': 8,
             'p6': 9,
             'a6': 10,
             'd7': 10,
             'p7': 11,
             'd8': 11,
             'p8': 12
             }


class interval:
    """
    This class implements a musical interval
    """

    
    def __init__(self, interval_name):
        """
        Class to implement musical intervals.
        
        Perfect interval categories (fundamental plus octave shifted):
            Unison: p1
            Second: p2, p9, p16, etc. (2 + 7n for n >= 0)
            Third: p3, p10, p17, etc. (3 + 7n for n >= 0)
            Fourth: p4, p11, p18, etc. (4 + 7n for n >= 0)
            Fifth: p5, p12, p19, etc. (5 + 7n for n >= 0)
            Sixth: p6, p13, p20, etc. (6 + 7n for n >= 0)
            Seventh: p7, p14, p21 etc. (7 + 7n for n >= 0)
            Octave: p8, p15, p22, etc. (8 + 7n for n >= 1)
            
            So we can have perfect intervals of form p + [any integer >= 1] 
            
        Augmentable intervals: a1, a2, a3, a4, a5, a6 and octave shifts
        Diminishable intervals: d2, d3, d4, d5, d6, d7, d8 and octave shifts
        """
        
        # Validate interval_name input
        if (not re.match(r'[adp]\d+\b', interval_name) or interval_name == 'd1'):
            raise ValueError('Invalid interval name specified')
            
        self._interval_name = interval_name
        
    
    def __len__(self):
        """
        Use our distance dictionary to figure out how many semitones
        a given interval represents
        """
        if self._interval_name == 'p1':
            return distances['p1']
        else:
            # the number in the interval is x + 7n for some x we need to find
            # use mod 7, but handle exceptions for sevenths and octaves
            interval_type = self._interval_name[0]
            interval_number = int(self._interval_name[1:])
            reduced_interval_number = interval_number % 7
            
            if reduced_interval_number == 0:
                reduced_interval_number = 7
            elif reduced_interval_number == 1:
                reduced_interval_number = 8
            
            reduced_interval_name = self._interval_name[0] + str(reduced_interval_number)
            
            base_length = distances[reduced_interval_name]
            
            # every additional 7 beyond base_length  in interval_number adds an octave, or 12 semitones
            octave_offset = 12*(interval_number - base_length)/7
            
            # augment or diminish the interval if necessary
            if interval_type == 'a':
                a_d_offset = 1
            elif interval_type == 'd':
                a_d_offset = -1
            else:
                a_d_offset = 0
                
            return base_length + octave_offset + a_d_offset
    
        
    def __add__(self, other):
        print(distances['p1'])




a = interval('p22')

len(a)

asdf = 'p22'
int(asdf[1:])%7


































if not re.match(r'[adp]\d+\b', 'd23489'):
    print('hey!')
else:
    print('NOOOOOOOOOOO')





def transpose(note_num, interval, direction):
    """
    Transpose note_num by the number of semi-tones indicated by interval
    Shit, we need to be able to do interval arithmetic
    Or do we?
    perfect + perfect = perfect (unless adding perfect 4ths, then it's diminished)
    augmented + augmented = perfect, then augmented
    diminished + diminished = perfect, then diminished
    augmented + diminished = perfect, then diminshed (the second one)
    diminished + augmented = perfect, then augmented (the second one)
    so we need an INTERVAL CLASS! with __add__
    
    """
    
    
    
    return note_num




















class pitch:
    
    """
    Class: pitch
    A pitch is one of the Western 12 tones plus which octave it is in.
    It corresponds to a key on the piano (A0-C8, C4 is middle C), plus 
    the correct enharmonic name.
    The note name is specified in lilypond notation for ease of notation later.
    
    Fields:
    _note_num - integer distance from C1 = 0, C4 = middle C = 48 on a piano keyboard, the unique identifier
    _tonal_center - tonal center of the harmonic environment we have in mind
    _harmonic_env - harmonic environment: ionian, lydian, dorian, etc.
    _note_name - enharmonically correct name in lilypond notation
    
    Behaviors:
    transpose(note, interval)    
    """
    
    def __init__(self, note_num, tonal_center, interval_from_root):
        """
        docstring
        """
        
        self._note_num = note_num
        self._tonal_center = tonal_center
        self._interval_from_root = interval_from_root
        
    def get_note_name(self):
        """
        Returns the name of the pitch in lilypond notation
        """
        letter_names = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
        interval_type = self._interval_from_root[0]
        interval_distance = self._interval_from_root[1]
        new_letter_name = letter_names[(int(letter_names.index(self._tonal_center)) + int(interval_distance) - 1)%7]
        if interval_type == 'p':
            return new_letter_name
        elif interval_type == 'a':
            return new_letter_name + 'is'
        elif interval_type == 'd':
            return new_letter_name + 'es'
            


"""
C: P1,
C#, Db: A1, D2
D: P2
D#, Eb: A2, D3
E, Fb: P3, D4
E#, F: A3, P4
F#, Gb: A4, D5
G: P5
G#, Ab: A5, D6
A: P6
A#, Bb: A6, D7
B: P7, D8
-----
C: P8
C#, Db: A8, D9
...
"""







def get_note_name(root_note_name, root_note_num, interval_from_root):
    """
    Returns the name of the pitch in lilypond notation
    """

    letter_names = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
    
    interval_type = interval_from_root[0]
    interval_distance = int(interval_from_root[1])
    
    new_letter_num = (letter_names.index(root_note_name) + interval_distance - 1)%7
    new_letter_name = letter_names[new_letter_num]
    
    if interval_type == 'p':
        return new_letter_name
    elif interval_type == 'a':
        return new_letter_name + 'is'
    elif interval_type == 'd':
        return new_letter_name + 'es'

get_note_name('b', 47, 'p3')




So in B major, with B = 47, the third is 51, how do we know that's D# not Eb?
pitch = 51
tonal_center = B
harmonic_env = major
interval_from_root = P3
So since it's a third away from B, it has to be some kind of D and not some kind of E

# so like C# in A dorian can be a #17
# A C E G B D F# A C# E G# B D# F# 
# E in C dorian is a "#17" it's Eb#
# C Eb G Bb D F A C E G

"""       
 










       
    
