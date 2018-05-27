

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

# Translates a number of semi-tones into a corresponding pure diatonic interval
num_semitones_to_pure = {0: 'p1',
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

    
    def __init__(self, interval):
        """
        Class to implement musical intervals.
        
        The interval_name paramter is something like p4+, a5+ or d6- to represent
        a pure fourth up, augmented fifth up, diminished sixth down and such like. We're going 
        to say there are no double diminished or double augmented intervals for now.
        
        The key thing we're trying to capture is the function of the note relative to the harmonic
        context. So in Gb, for us, a C# can't occur (this would be a double augmented interval)
        
        The last character of the string is either '+' or '-' depending on whether you mean
        the interval is going up or down. Everything we do below (with the exception of 
        interval addition) doesn't depend on the direction.
        
        pure interval categories (fundamental plus octave shifted):
            Unison/Octave/Fifteenth: p1, p8, p15, etc. (1 + 7n for n >= 0)      
            Second/Ninth/Sixteenth: p2, p9, p16, etc. (2 + 7n for n >= 0)
            Third/etc.: p3, p10, p17, etc. (3 + 7n for n >= 0)
            Fourth: p4, p11, p18, etc. (4 + 7n for n >= 0)
            Fifth: p5, p12, p19, etc. (5 + 7n for n >= 0)
            Sixth: p6, p13, p20, etc. (6 + 7n for n >= 0)
            Seventh: p7, p14, p21 etc. (7 + 7n for n >= 0)

            General: reduced_interval_number + 7*octave_offset

        Augmentable intervals: a1, a2, a3, a4, a5, a6 and further octave shifts
        Diminishable intervals: d2, d3, d4, d5, d6, d7, d8 and further octave shifts
        Basically, d1 doesn't exist, and a7, a14, a21 don't exist
        """
        
        # _interval_type and _interval_number break up _interval_name = 'p5' into
        # _interval_type = 'p' and _interval_number = 5
        self._interval = interval
        self._interval_name = self._interval[:-1]
        self._interval_type = self._interval_name[0]
        self._interval_number = int(self._interval_name[1:])
        self._interval_direction = self._interval[-1:]
        
        if self._interval_direction == '+':
            self._interval_sign = 1
        elif self._interval_direction == '-':
            self._interval_sign = -1
        
        # Validate interval_name input
        # Has to be a string with a, d, or p followed by an integer > 1, 
        # and can't be d1 or a7, a14, a21, etc
        if (not re.match(r'[adp]\d+\b', self._interval_name)
        or type(self._interval_number) != int
        or self._interval_number < 1
        or self._interval_name == 'd1'
        or (self._interval_type == 'a' and self._interval_number % 7 == 0)
        or self._interval_direction not in ['+', '-']):
            raise ValueError('Invalid interval name')
            
        # Compute the equivalent diatonic interval name in one octave
        # We use mod 7 arithemtic, but we start pure sevenths with 7 instead of 0
        # (since here is no diatonic 'pure 0' relationship)
        # We also start diminished sevenths with 8 instead of 1
        # (since there is no 'diminished 1' relationship)
        # This way, we know that a pure 17th is just a pure third plus two octaves
        self._reduced_interval_number = self._interval_number % 7
        if self._reduced_interval_number == 0:
            self._reduced_interval_number = 7
        elif self._reduced_interval_number == 1:
            self._reduced_interval_number = 8
            
        # Form the diatonic name of the reduced interval
        # Also compute the number of half steps in it as base_length
        # So for a pure 17th, _reduced_interval_name = 'p3' and _base_length = 4
        self._reduced_interval_name = self._interval_type + str(self._reduced_interval_number)
        self._base_length = diatonic_to_num_semitones[self._reduced_interval_name]
            
        # Compute how many octaves above the first that our interval lies in
        # So for a pure 17th, _octave_offset = 2
        self._octave_offset = int((self._interval_number - self._reduced_interval_number)/7)
                 
    
    def semitones_to_diasteps(num_semitones):
        """
        Take a given number of semitones and translate it into the corresponding
        type of diatonic interval. If num_semitones < 0, return a descending interval
        
        Return a list of all possible intervals
        
        Examples:
        num_semitones = 4 and interval_type = 'p' returns 'p3'
        num_semitones = 4 and interval_type = 'd' returns 'd4'
        num_semitones = 4 and interval_type = 'a' gives an error because there is no such thing
        """
        
        # We'll do all of our arithemtic in the positive world, then return the correct direction later
        raw_num_semitones = abs(num_semitones)
        
        if raw_num_semitones < 0:
            new_direction = '-'
        elif raw_num_semitones >= 0:
            new_direction = '+'
        
        base_num_semitones = raw_num_semitones % 12
        octave_offset = raw_num_semitones//12
        
        # Store our (possibly multi-valued) results in a list
        possible_results = []

        # Helper function for processing each of the three cases
        def process_interval_type_case(interval_type, dictionary_to_use, base_num_semitones, octave_offset, new_direction):
            if base_num_semitones in dictionary_to_use:
                base_diatonic_interval = dictionary_to_use[base_num_semitones]
                new_interval_number = int(base_diatonic_interval[1:]) + 7*octave_offset
                possible_results.append(interval(interval_type + str(new_interval_number) + new_direction))
            else:
                raise ValueError('Invalid interval relationship ' + str(raw_num_semitones) + ' ' + interval_type)

        # Process all three cases, appending to the list when necessary                
        process_interval_type_case('p', num_semitones_to_pure, base_num_semitones, octave_offset, new_direction)
        process_interval_type_case('a', num_semitones_to_augmented, base_num_semitones, octave_offset, new_direction)
        process_interval_type_case('d', num_semitones_to_diminished, base_num_semitones, octave_offset, new_direction)

        return possible_results

    
    def __len__(self):
        """
        Return the number of semitones in the given interval
        This could also be called diasteps_to_semitones in comparison with the
        previous function.
        """
        return self._base_length + 12*self._octave_offset
    
    
    def __repr__(self):
        """
        Print the name of the interval when we run one of these objects
        https://stackoverflow.com/questions/12412324/python-class-returning-value
        """
        return self._interval
    
    def __eq__(self, other):
        return self._interval == other._interval
    
    def __ne__(self, other):
        return not self == other
    
    def reverse_direction(self):
        """
        Reverse the direction of the interval
        """
        if self._interval_direction == '+':
            new_direction = '-'
        elif self._interval_direction == '-':
            new_direction = '+'
            
        return interval(self._interval_name + new_direction)
    
        
    def __add__(self, other):
        """
        We need to define rules for adding arbitrary intervals together, including direction.
        
        How about this: add the number of semitones and find out what intervals are available
        and use some rule to decide between temn
        
        Strategy:
            Add the two lengths to get the number of semitones
            Divide this number into the form reduced_interval_number + 7*octave_offset
            Figure out what type of interval the result should be
            Look up reduced_interval_number in the dictionary
        """
        
        # Add the lengths of the two intervals to get the total number of semitones
        # in the new interval
        new_num_semitones = self._interval_sign*len(self) + other._interval_sign*len(other)
        
        return semitones_to_diasteps(new_num_semitones)
        
          
        



a = interval('p3+')
b = interval('p3+')
a+b


c = interval('a5+')
len(c)

"""
p = pure (used to be perfect)
d and a are the same
test reverse direction function
fix interval arithmetic
interval regression tests


"""






















class scale:
    """
    A scale is an ordered collection of ascending intervals starting with a unison (or 'p1' 
    in our interval notation), wh
    
    We enter the ionian, melodic minor, and other scales, and programmatically generate the modes    
    
    For example:    
    Ionian scale: ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7']
    Dorian scale: ['p1', 'p2', 'm3', 'p4', 'p5', 'p6', 'm7']


    """











class pitch:
    
    """
    For this system, a pitch corresponds to a key on a theoretically infinite piano. For practical
    purposes, most of the stuff we do takes place on the 88 actual piano keys.

    There are several important representations for each pitch. We'll use middle C as an example.

    There is only one unique representation (i.e., no enharmonic or other equivalents):
    note_number_rep: 48 (the 48th key from the left on a piano)
    
    The rest of the representations admit of various enharmonic spellings:
    tonal_center_rep: tonal_center = 'aes', interval_from_root = 'p3', harmonic_env = 'major'
    piano_key_rep: "C4" (the fourth C from the bottom)
    lilypond_rep: "c'" (one octave above C in the middle of bass clef)

    or:
    tonal_center_rep: tonal_center = 'gis', interval_from_root = 'p3', harmonic_env = 'major'
    piano_key_rep: "B#4" (the fourth B# from the bottom)
    lilypond_rep: "bis" (within one octave above C in the middle of bass clef)
    
    or:
    tonal_center_rep: tonal_center = 'ces', interval_from_root = 'd2', harmonic_env = 'major'
    piano_key_rep: "Dbb4" (the fourth Dbb from the bottom)
    lilypond_rep: "deses'" (one octave above C in the middle of bass clef)
    
    Other possibilities
    sargam_rep: tonal_center = 'aes', sargam_from_root = 'ga'
    frequency_rep (something about Easley Blackwood tunings and such)
    
    ---------
    So in B major, for example with B = 47, the third is 51, how do we know it should be D# and not Eb?
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

map to frequencies
mirror exercises
negative harmony 
scales with tetrachords
harmonica the quadruple flat 3 is just the #4

indian music frequencies and just intonation

define arbitrary microtonal "diatonic" systems in terms of frequency

"""
