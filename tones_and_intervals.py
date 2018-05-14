

"""
This code implements selected parts of Western diatonic music theory.
"""

import re


# Translates diatonic intervals within one octave into the corresponding number of semi-tones
diatonic_to_num_semitones = {'p1': 0,
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
                              'd8': 11}

# Translates a number of semi-tones into a corresponding perfect diatonic interval
num_semitones_to_perfect = {0: 'p1',
                            2: 'p2',
                            4: 'p3',
                            5: 'p4',
                            7: 'p5',
                            9: 'p6',
                            11: 'p7'}

# Translates a number of semi-tones into a corresponding augmented diatonic interval
num_semitones_to_augmented = {1: 'a1',
                              3: 'a2',
                              5: 'a3',
                              6: 'a4',
                              8: 'a5',
                              10: 'a6'}

# Translates a number of semi-tones into a corresponding diminished diatonic inteval
num_semitones_to_diminished = {1: 'd2',
                               3: 'd3',
                               4: 'd4',
                               6: 'd5',
                               8: 'd6',
                               10: 'd7',
                               11: 'd8'}


# Letter names of diatonic notes in order
letter_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g']


class interval:
    """
    This class implements the concept of a musical interval in diatonic Western music
    """

    
    def __init__(self, interval_name):
        """
        Class to implement musical intervals.
        
        Perfect interval categories (fundamental plus octave shifted):
            Unison/Octave: p1, p8, p15, p22 (1 + 7n for n >= 0)      
            Second: p2, p9, p16, etc. (2 + 7n for n >= 0)
            Third: p3, p10, p17, etc. (3 + 7n for n >= 0)
            Fourth: p4, p11, p18, etc. (4 + 7n for n >= 0)
            Fifth: p5, p12, p19, etc. (5 + 7n for n >= 0)
            Sixth: p6, p13, p20, etc. (6 + 7n for n >= 0)
            Seventh: p7, p14, p21 etc. (7 + 7n for n >= 0)

            General: reduced_interval_number + 7*octave_offset

        Augmentable intervals: a1, a2, a3, a4, a5, a6 and further octave shifts
        Diminishable intervals: d2, d3, d4, d5, d6, d7, d8 and further octave shifts
        Basically, d1 doesn't exist, and a7, a14, a21 don't exist
        """
        
        self._interval_name = interval_name        
        self._interval_type = self._interval_name[0]
        self._interval_number = int(self._interval_name[1:])
        
        # Validate interval_name input
        # Has to be a string with a, d, or p followed by a number, and can't be d1 or a7, a14, a21, etc
        if (not re.match(r'[adp]\d+\b', self._interval_name) 
        or self._interval_name == 'd1'
        or (self._interval_type == 'a' and self._interval_number % 7 == 0)):
            raise ValueError('Invalid interval name specified')
            
        # Compute the equivalent diatonic interval name in one octave
        # We use mod 7 arithemtic, but we start sevenths with 7 instead of 0
        # (There is no diatonic '0' relationship)
        self._reduced_interval_number = self._interval_number % 7
        if self._reduced_interval_number == 0:
            self._reduced_interval_number = 7
            
        # Form the diatonic name of the reduced interval
        # Also compute the number of half steps in it as base_length
        self._reduced_interval_name = self._interval_type + str(self._reduced_interval_number)
        self._base_length = diatonic_to_num_semitones[self._reduced_interval_name]
            
        # Compute how many octaves above the first that our interval lies in
        self._octave_offset = int((self._interval_number - self._reduced_interval_number)/7)
                 
    
    def semitones_to_diasteps(num_semitones, interval_type):
        """
        Take a given number of semitones and translate it into the corresponding
        type of diatonic interval
        TODO: check this for invalid input?
        """
        base_num_semitones = num_semitones % 12
        octave_offset = num_semitones//12
        
        if interval_type == 'p':
            base_diatonic_interval = num_semitones_to_perfect[base_num_semitones]
        elif interval_type == 'a':
            base_diatonic_interval = num_semitones_to_augmented[base_num_semitones]
        elif interval_type == 'd':
            base_diatonic_interval = num_semitones_to_diminished[base_num_semitones]
            
        new_interval_number = int(base_diatonic_interval[1:]) + 7*octave_offset
        
        return interval(interval_type + str(new_interval_number))

    
    def __len__(self):
        """
        Return the number of semitones in the given interval
        This could also be called diasteps_to_semitones in comparison with the
        previous function.
        """
        return self._base_length + 12*self._octave_offset
    
    
    def run(self):
        """
        TODO: figure out how to get the desired output when we call an object
        """

        return self._interval_name
    
    def __eq__(self, other):
        return self._interval_name == other._interval_name
    
    def __ne__(self, other):
        return not self == other
    
        
    def __add__(self, other):
        """
        Figure out what happens when we add intervals together. 
        There are a few cases:
            perfect + perfect = perfect (unless adding perfect 4ths (up to octave shifts), then it's diminished)
            augmented + augmented = perfect, then augmented
            diminished + diminished = perfect, then diminished
            augmented + diminished = perfect, then diminshed (the second one)
            diminished + augmented = perfect, then augmented (the second one)  
        
        Strategy:
            Add the two lengths to get the number of semitones
            Divide this number into the form reduced_interval_number + 7*octave_offset
            Figure out what type of interval the result should be
            Look up reduced_interval_number in the dictionary
        """
        
        # Add the lengths of the two intervals to get the total number of semitones
        # in the new interval
        new_num_semitones = len(self) + len(other)
        
        # Implement the addition rules above
        if self._reduced_interval_name == 'p4' and other._reduced_interval_name == 'p4':
            final_interval_type = 'd'
        elif self._interval_type == 'p' and self._interval_type == 'p':
            final_interval_type = 'p'
        elif self._interval_type == 'a' and other._interval_type == 'a':
            try:
                final_interval_type = 'p'
            except:
                final_interval_type = 'a'
        elif self._interval_type == 'd' and other._interval_type == 'd':
            try:
                final_interval_type = 'p'
            except:
                final_interval_type = 'd'
        elif self._interval_type == 'a' and other._interval_type == 'd':
            try:
                final_interval_type = 'p'
            except:
                final_interval_type = 'd' 
        elif self._interval_type == 'd' and other._interval_type == 'a':
            try:
                final_interval_type = 'p'
            except:
                final_interval_type = 'a' 
        
        return self.semitones_to_diasteps(new_num_semitones, final_interval_type)
            

"""
TODO: interval regresion tests

a = interval('p3')
b = interval('p4')
len(a)

c = a + b
c._interval_name
"""





class pitch:
    
    """
    A pitch is one of the Western 12 tones plus which octave it is in.
    It corresponds to a key on the piano (A0-C8, C4 is middle C), plus 
    the correct enharmonic name.
    The note name is specified in lilypond notation for ease of notation later.
    We represent a pitch as a root plus an interval for enharmonic purposes
    
    So in B major, with B = 47, the third is 51, how do we know that's D# not Eb?
    pitch = 51
    tonal_center = B
    harmonic_env = major
    interval_from_root = P3
    So since it's a third away from B, it has to be some kind of D and not some kind of E
    
    so like C# in A dorian can be a #17
    A C E G B D F# A C# E G# B D# F# 
    E in C dorian is a "#17" it's Eb#
    C Eb G Bb D F A C E G

    """
    
    def find_note_name(note_num, direction):
        """
        Quick helper function to return a lilypond note name for a given note_num
        """
        
        if direction == 'neutral':
            find_note_name_dict = {0: 'c',
                                   2: 'd',
                                   4: 'e',
                                   5: 'f',
                                   7: 'g',
                                   9: 'a',
                                   11: 'b'}
        elif direction == 'sharp':
            find_note_name_dict = {0: 'c',
                                   1: 'cis',
                                   2: 'd',
                                   3: 'dis',
                                   4: 'e',
                                   5: 'f',
                                   6: 'fis',
                                   7: 'g',
                                   8: 'gis',
                                   9: 'a',
                                   10: 'ais',
                                   11: 'b'}
        elif direction == 'flat':
            find_note_name_dict = {0: 'c',
                                   1: 'des',
                                   2: 'd',
                                   3: 'ees',
                                   4: 'e',
                                   5: 'f',
                                   6: 'ges',
                                   7: 'g',
                                   8: 'aes',
                                   9: 'a',
                                   10: 'bes',
                                   11: 'b'}
        
        return find_note_name_dict[note_num % 12]
            
    
    def __init__(self, root_note_num, root_note_name, interval_from_root):
        """
        root_note_num is a number from -3 to X representing the number of key on piano
        root_note_name is one of the possible names for the root note, such as cisis
        interval_from_root is how far the actual pitch is from the root note
        """
        
        # Check that root_note_num and root_note_name are consistent
        count_sharp = root_note_name.count('is')
        count_flat = root_note_name.count('es')
        
        if count_sharp == 0 and count_flat == 0:
            try:
                self.find_note_name[root_note_num, 'neutral']
            except:
                raise ValueError('Invalid pitch parameters')
        elif count_sharp == 1 and count_flat == 0:
            try:
                self.find_note_name
        
        
        # Initialize attributes
        self._root_note_num = root_note_num
        self._root_note_name = root_note_name
        self._interval_from_root = interval_from_root
        self._note_name = self.get_note_name(self)
        
        self._dereferenced_pitch = asdf
        
        
    def get_note_name(self):
        """
        Returns the name of the pitch in lilypond notation
        """
        
        interval_type = self._interval_from_root[0]
        interval_distance = self._interval_from_root[1]
        new_letter_name = letter_names[(int(letter_names.index(self._tonal_center)) + int(interval_distance) - 1)%7]
        if interval_type == 'p':
            return new_letter_name
        elif interval_type == 'a':
            return new_letter_name + 'is'
        elif interval_type == 'd':
            return new_letter_name + 'es'
        
    def transpose(note_num, interval, direction):
        """
        Transpose note_num by the number of semi-tones indicated by interval
        Shit, we need to be able to do interval arithmetic
        """
    


a = 'deses'
a.count('es')




"""
classes: scale
map to frequencies
mirror exercises
negative harmony 
scales with tetrachords
harmonica the quadruple flat 3 is just the #4
"""
