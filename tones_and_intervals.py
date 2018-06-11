






"""
This code implements selected parts of Western diatonic music theory.
"""

import re


# Translates diatonic intervals within one octave into the corresponding number of semi-tones
# We'll say there's no such thing as d1 or d8
diatonic_to_num_semitones = {
'p1': 0,
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
'p7': 11}

# Translates a number of semi-tones into a corresponding pure diatonic interval
num_semitones_to_pure = {
0: 'p1',
2: 'p2',
4: 'p3',
5: 'p4',
7: 'p5',
9: 'p6',
11: 'p7'}

# Translates a number of semi-tones into a corresponding augmented diatonic interval
num_semitones_to_augmented = {
1: 'a1',
3: 'a2',
5: 'a3',
6: 'a4',
8: 'a5',
10: 'a6'}

# Translates a number of semi-tones into a corresponding diminished diatonic inteval
num_semitones_to_diminished = {
1: 'd2',
3: 'd3',
4: 'd4',
6: 'd5',
8: 'd6',
10: 'd7'}


# Letter names of diatonic notes in order
letter_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g']








def semitones_to_diasteps(num_semitones):
    """
    Take an integer number of semitones and return a list of all possible diatonic intervals
    corresponding to that number. If num_semitones < 0, return a descending interval.
    
    This function doesn't actually act on any of our class objects below, so we define it
    in open code.
    
    For multi-valued outputs, we leave it to downstream processes to choose the correct version.
    
    Examples:
    semitones_to_diasteps(4) = 4 returns [p3+, d4+]
    semitones_to_diasteps(-5) returns [p4-, a3-]
    """
    
    # Make sure the input is an integer
    if type(num_semitones) != int:
        raise ValueError('num_semitones must be an integer')
    
    # We'll do all of our arithemtic in the positive world, then return the correct direction later
    raw_num_semitones = abs(num_semitones)
    
    # Get direction for final interval(s)
    if num_semitones < 0:
        new_direction = '-'
    elif num_semitones >= 0:
        new_direction = '+'
    
    base_num_semitones = raw_num_semitones % 12
    octave_offset = raw_num_semitones//12
    
    # Store our (possibly multi-valued) results in a list
    possible_results = []

    # Helper function for processing each of the three cases
    def process_interval_type_case(interval_type, dictionary_to_use):
        if base_num_semitones in dictionary_to_use:
            base_diatonic_interval = dictionary_to_use[base_num_semitones]
            new_interval_number = int(base_diatonic_interval[1:]) + 7*octave_offset
            possible_results.append(interval(interval_type + str(new_interval_number) + new_direction))
        else:
            pass

    # Process all three cases, appending to the list when necessary                
    process_interval_type_case('p', num_semitones_to_pure)
    process_interval_type_case('a', num_semitones_to_augmented)
    process_interval_type_case('d', num_semitones_to_diminished)

    return possible_results





class interval:
    """
    This class implements the concept of a musical interval in diatonic Western music.
    """

    
    def __init__(self, interval):
        """
        Class to implement musical intervals.
        
        The interval_name paramter is something like p4+, a5+ or d6- to represent
        a pure fourth up, augmented fifth up, diminished sixth down and such like. We're going 
        to say there are no double diminished or double augmented intervals (or such like).
        
        The key thing we're trying to capture is the function of the note relative to the harmonic
        context. So in Gb, for us, a C# can't occur (this would be a double augmented interval--Cb raised by 2 steps)
        
        The last character of the string is either '+' or '-' depending on whether you mean
        the interval is going up or down. Everything we do below (with the exception of 
        interval addition) doesn't depend on the direction.
        
        We use '+' as the default direciton.
        
        Pure interval categories (fundamental plus octave shifted):
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
        Basically, d1 doesn't exist, and a7, a14, a21, etc. don't exist
        """
                
        self._interval = interval
        
        # Without the direction
        self._interval_name = self._interval[:-1]
        
        # _interval_type and _interval_number break up _interval_name = 'p5' into
        # _interval_type = 'p' and _interval_number = 5
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
        # TODO: check for p5 vs. p5+
        if (not re.match(r'[adp]\d+\b', self._interval_name)
        or type(self._interval_number) != int
        or self._interval_number < 1
        or self._interval_name == 'd1'
        or (self._interval_type == 'a' and self._interval_number % 7 == 0)
        or self._interval_direction not in ['+', '-']):
            raise ValueError('Invalid interval name')
            
        # Compute the equivalent diatonic interval name in one octave
        # We use mod 7 arithemtic
        # This way, we know that a pure 17th is just a pure third plus two octaves
        self._reduced_interval_number = self._interval_number % 7
        
        # We start pure sevenths with 7 instead of 0
        # (since here is no diatonic 'pure 0' relationship)
        # We also [etc]
        if self._reduced_interval_number == 0:
            self._reduced_interval_number = 7
        
        # Form the diatonic name of the reduced interval
        # Also compute the number of half steps in it as base_length
        # So for a pure 17th, _reduced_interval_name = 'p3' and _base_length = 4
        self._reduced_interval_name = self._interval_type + str(self._reduced_interval_number)
        self._base_length = diatonic_to_num_semitones[self._reduced_interval_name]
            
        # Compute how many octaves above the first that our interval lies in
        # So for a pure 17th, _octave_offset = 2
        self._octave_offset = int((self._interval_number - self._reduced_interval_number)/7)
                     
    def __len__(self):
        """
        Return the number of semitones in the given interval
        This could also be called diasteps_to_semitones in comparison with the
        previous function.
        """
        return self._base_length + 12*self._octave_offset
    
    def __str__(self):
        return self._interval
        
    def __repr__(self):
        return 'interval(' + self._interval + ')'
    
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
        What happens when we add two intervals together, including direction? We get a result
        that may have up to two different possible names. For this function, we return
        a list of such names. Depending on the situation, we'll use some rule to disambiguate
        the list.
        
        Use this code to convince yourself that we can add any two types of intervals, and have the result be any of the two types
        
        reduced_intervals = ['p1','a1','d2','p2','a2','d3','p3','d4','a3','p4','a4','d5','p5','a5','d6','p6','a6','d7','p7']
        directions = ['+', '-']
        
        results = []
        for first in reduced_intervals:
            for second in reduced_intervals:
                for first_direction in directions:
                    for second_direction in directions:
                                        
                        addition = interval(first + first_direction) + interval(second + second_direction)
                        
                        if len(addition) > 1:
                            str_to_add = ''
                            for i in addition:
                                str_to_add += str(i)[0]
                                
                            results.append(str(first)[0] + str(second)[0] + '__' + str_to_add)
        
        """
        
        # Add the lengths of the two intervals to get the total number of semitones
        # in the new interval
        new_num_semitones = self._interval_sign*len(self) + other._interval_sign*len(other)
        
        return semitones_to_diasteps(new_num_semitones)
    
    
    def __sub__(self, other):
        """
        Interval subraction is the opposite of interval addition.
        """
        return self + other.reverse_direction()
    






class scale:
    """
    A scale is an ordered list of (ascending or descending) interval strings starting with a unison (or 'p1+' 
    in our interval notation). Each string represents the distance between successive notes.
    There's also a continuation offset.
    
    So we could have major_scale = scale(['p2+', 'p2+', 'd2+', 'p2+', 'p2+', 'p2+'], 'd2+')
    
    We enter the ionian, melodic minor, and other base scales and tetrachords, and programmatically generate the modes    
    """

    def __init__(self, list_of_interval_strings, continuation_offset):
        """
        We take a list of interval strings and converts it into a list of intervals.
        
        So instead of initializing using 
    
            new_scale = [interval('p1+'), interval('p2+'), interval('p2+')] 
    
        we can initialize using
        
            new_scale = scale(['p1+', 'p2+', 'p3+'])
            
        continuation_offset is a parameter enabling hyperdiatonic systems
        """
        
        # Preserve the string version of all these for later
        self._str_list_of_interval_strings = list_of_interval_strings
        self._str_continuation_offset = continuation_offset
        
        converted_interval_strings = []
    
        for interval_string in list_of_interval_strings:
            converted_interval_strings.append(interval(interval_string))
            
        self._scale_steps = converted_interval_strings
        
        # make sure offset is an interval string
        self._offset = interval(continuation_offset)
       
    
    def __str__(self):
        """
        TODO
        """

    def __repr__(self):
        """
        We have to do a bit of work to return the appropriate string
        """
        return 'scale([' + ', '.join(self._str_list_of_interval_strings) + '], ' + self._str_continuation_offset + ')'
       
    
    def __getitem__(self, index):
        return self._scale_steps[index]
    
    def get_mode(self, mode_number):
        """
        Return the given mode of the given scale, meaning cyclically permute the list of
        interval strings and continuation offset right by one place
        
        We use modular arithmetic, so mode_number can be > len(self)
        """
        
        # Get a list of the interval strings because it's easier to work with
        full_interval_list = self._str_list_of_interval_strings + [self._str_continuation_offset]
        
        # Start at the appropriate element and add on each consecutive element, wrapping around
        # once we reach the end. This gives a list of intervals in the correct order
        new_mode = []
        num_elements = len(full_interval_list)
        for i in range(num_elements):
            new_mode.append(full_interval_list[(i + mode_number - 1) % num_elements])

        # Return a scale corresponding to this new permutation of interval strings
        return scale(new_mode[0:-1], new_mode[-1])
    
    def __len__(self):
        """
        The length of a scale is what we need to loop over when doing stuff,
        so we'll define it as the length of the interval string list. 
        The interavl string includes the continuoation offset, so we add one at the end
        Recall that for our purposes, a scale can be any length
        """
        return len(self._str_list_of_interval_strings) + 1
        
    def widest_interval(self):
        """
        Return the widest interval in the scale.
        We obviously need to do this on the absolute representation.
        If scales were forced to be monotonically increasing, we could just
        use the last interval, but here the widest interval need not be the last
        """
        
        scale_length = 0
        for interval in self._scale_steps:
            if len(interval) > scale_length:
                scale_length= len(interval)
                
        return scale_length


    
    def compute_interest(self):
        """
        A measure of how interesting the scale is--what proportion of the twelve tones
        does it include in its entirety?
        """
        
        # WLOG put it into C representation
        # Compute number of pitches out of 12



# Major scale harmony
major_scale = scale(['p2+', 'p2+', 'd2+', 'p2+', 'p2+', 'p2+'], 'd2+')
dorian_scale = major_scale.get_mode(2)
phrygian_scale = major_scale.get_mode(3)
lydian_scale = major_scale.get_mode(4) = p2, p2, p2, d2, p2, p2, d2
mixolydian_scale = major_scale.get_mode(5)
aeolian_scale = major_scale.get_mode(6)
locrian_scale = major_scale.get_mode(7)

# Melodic minor harmony
melodic_minor_scale = scale(['p2+', 'd2+', 'p2+', 'p2+', 'p2+', 'p2+'], 'd2+')
melodic_minor_scale

# Tetrachords
lydian_tetrachord = scale(['p2+', 'p2+', 'd2+'])

"""
ok, issue for converting to absolute representation: 
when we dereference each interval addition thing, we need to amke sure we're obeying
the diatonic pitch order. Like, we know the fourth of a lydian scale is raised,
so we shoudl choose that interval, and the reason is because it has to have 
that letter name! 

Maybe do a reference computation in C major in the scale class to do this 
computation--that tells us what letter name we're on, and shoudl result in no
loss of generality

Maybe a really simple specailized impoementation of pitch here just to keep
track of where we are on the diatonic spectrum

Like, something like [c0, 3] for c0 triple sharp

Have later pitch properties inherit from this?

Aaaah but what about scales that are not do re mi?

Ok--a simple scale class for a do re mi scale, then generalize lateR?

need a function for C# lydian: C#, D#, E#, F##, G#, ...
F## = G, but it has to be "Some kind of F"
curr_pitch_is_some_kind_of_ref_pitch(current_pitch, reference_pitch)

ok, look at the lydian thing up there. d2 is still correct in relative, but
in absolute, it needs to be p1, p2, p3, a4, p5, p6, p7, p8.
Is there some interval arithmetic we can do to make sure we're "on the next pitch?"
TO make sure p1, p2, p3, d5, p5, p6, p7 is not correct? Yes! We need just hte numbers!
We always choose the interval that has the next number in it.

Now is there a mathematical way to check that it's a do-re-mi scale? 
Yes! try to construct the absolute, but you can't find the right numbers!

STress test on extreme scales like
c des e f g aes b 
c des eeses f ges aeses beseses c
No, any 7-note scale with pitches within an octave you can do it with enough accidentals (assuming monotonic)

what about pentatonic scales, tetrachords, super sparse scales



"""




def add_one_scale_degree(starting_interval, interval_to_add):
    """
    One way of dereferencing multivalued interval addition.
    In diatonic harmony, for absolute representation, each scale degree needs to have _interval_number one greater
    than the previous one. This function adds the next scale degree by looking for such a number
    """

    list_of_results = starting_interval + interval_to_add
    
    # Iterate over the possible results of the addition
    # Pick the interval from the list that has the next scale degree number if possible
    # The + 1 down there means "take the next scale degree"
    for element in list_of_results:
        if element._interval_number == starting_interval._interval_number + 1:
            return element
        
    # If we haven't found a match, it's an error
    raise ValueError('What you are trying to do is impossible.')
    





def absolute_scale_repr(scale):
    """
    Take relative scale representation:
        
        major_scale = scale(['p2+', 'p2+', 'd2+', 'p2+', 'p2+', 'p2+'], 'd2+')
        
    and make it into absolute representation:
        
        asdf
    """
    
    # Start out with a unison
    current_interval = interval('p1+')
    
    for element in scale:
        current_interval = add_one_scale_degree(current_interval, element)
        print(current_interval)
        

    




lydian_scale = major_scale.get_mode(4)
lydian_scale
absolute_scale_repr(lydian_scale)





full_interval_list = major_scale._str_list_of_interval_strings + [major_scale._str_continuation_offset]
full_interval_list 

mode_number = 4

new_mode
new_mode[0:-1]
new_mode[-1]
asdf = scale(new_mode[0:-1], new_mode[-1])
asdf







    
def new_iterated_scale:    
def scale_widest






class pitch:
    
    """
    For this system, a pitch corresponds to a key on a theoretically infinite piano. For practical
    purposes, most of the stuff we do takes place on the 88 actual piano keys.

    There are several important representations for each pitch. We'll use middle C as an example.

    There is only one unique representation (i.e., no enharmonic or other equivalents):
    note_number_rep: 48 (the 48th key from the left on a piano)
    
    The rest of the representations admit of various enharmonic spellings:
    tonal_center_rep: tonal_center = 'aes', interval_from_root = 'p3', scale = major_scale
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
TODO:
implement compute_interest
figure out why __repr__ is not working
do melodic minor and tetrachords


To Generate:
mirror exercises
negative harmony 
scales with tetrachords
harmonica the quadruple flat 3 is just the #4
modes of limited transposition
russ ferrante voice leading thing
random diatonic stuff

"""
