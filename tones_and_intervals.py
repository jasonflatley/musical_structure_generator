

"""
ideas for generalization
define letter names/codes for number of pitches in a generalized octave
everything follows from there

abcdefg for ionian diatonic

maybe intervals follow from "prototypical scale" like C ionian, and you have 'p2', 'p3', ... for pure/perfect
then each interval can be augmented/diminished an arbitrary number of times
unison is a p1. "+" is default so you can leave it out
can have different prototypical scales. You could have melodic minor-centric western harmony where c-eb is a "p3" and c-e is an "a3"
atonal music can be chromatic-scale centric
figure out how to express whatever xenharmonic system. western equally tempered should fall out of this
maybe use scala/.kbd files
generalize chorales/voice leading/counterpoint?
should it accomodate the WAMatthieu derivation of just intonation? So in a just intonation system, the frequencies
are computed on the fly based on the diatonic intervals?

arbitrary octave length
some rule for assigning frequency to pitch (like 19TET or whatever)

"""


"""
I like complex, highly structured melodies and harmonies. I also like everything to be
spelled enharmonically correctly. 

We proceed as in harmony and voice-leading
intervals form a group

So I made this package to implement a very general 
and flexible jazz scale theory that can be used to programmatically generate many different
pan-diatonic musical structures derived from things like
-Basic scales
-Jacob Collier hyper mega meta ultra lydian scale and its generalizations
-Arbitrary chord extensions like #15 or b39
-Dave Liebman's whole chromatic theory, including synthetic scales
-Mick Goodrick's system of voice-leading
-Slonimsky's scales
-Tonino Miano's whole atonal system
-Hindustani and Carnatic ragas (what of them fits in our Western system)
-canonic variations

Once we have these we can use them for
-Basic diatonic structures such as scales, thirds etc
-Generating families of lines according to certain shapes
-Vardan Ovsepian mirror exercises
-Randomly iterating relevant parts of the above
-Aydin Esin high-information lines
-Dave Liebman "use only fourths and minor seconds"
-Dividing into pitch classes such as {[c, f, e, g], [f#, a#, b, c#], [d, eb, ab, a]}
-Putting any of these together contrapuntally
-Negative harmony
-Modes of limited transposition (not just with one octave)
-Diatonic voice leading like Mick Goodrick
-Generate diatonic exercise books
-Do all of this within the compass of a particular voice or instrument
-Writing out samchillian-style riffs

We incorporate rhythmic patterns such as
-Different time signatures
-Eric Demaine's rhythmic necklaces
-Arbitrary accent patterns
-Many different polyrhythms

We'll be able to do cute tricks like
-Crazy computations in quintuple flats
-Howard Levy "the 2 of the 5 is the 3 of the 2"
-Something dan tepfer
    -visualize complicated chromatic structures while they play?
    -translate pictoral or other input into structured lines, relative to some scale? (like nok)
-Take numeric input (like from transcendental numbers) and hear it

We strive for high generality here, but note that enharmonic naming conventions are relative
to the ionian scale (white keys on the piano), so we can't treat all 12 pitches equally
for the purposes of notation (though when we're just listening, the way the performer might spell
the pitches is irrelevant)

TODO:
-input validation on all of these...
-implement compute_interest and compute how diatonic something is
-figure out why __repr__ is not working
-do melodic minor and tetrachords
-when we're doing scale output, we need to be able to output the chord!
-add a class for pitch
-then a class for note
-then time sigunature stuff like that eric demaine essay
-add an option to expand pitches with enclosures
-hindustani raga stuff?
-a rendered scale is just a starting note + a scale, then extend that over the whole piano in both directions
-implement quartertones? F, Fh#, F#, Ghb, Gb
-implement overtone series 7th -31 pivot?
-mick goodrick/dan tepfer voice leading?
-make the exercise generator an iterator?
"""



import re
import math
import numpy as np
import pandas as pdf


class geninterval:
    """
    This class implements the concept of a generalized musical interval in Western equally-tempered tuning.
    We phrase everything in terms of integer numbers of semi-tones
    A generalized musical interval is the distance between an implicit base tone and a target tone, with an adjustment.
    The adjustment is just the number of times it's augmented or diminished, which can be arbitrary.
    We can derive standard Western music theory by stopping off at all the points in a major scale.
    But we can use other scales too!
    
    Intervals form an abelian group under addition.
    """

    
    def __init__(self, distance, adjustment):
        """
        Docstring
        """
        
        # The distance and adjustment have to be integer numbers of semi-tones
        if type(distance) != int:
            raise ValueError('Interval distance must be an integer number of semi-tones')
            
        if type(adjustment) != int:
            raise ValueError('Interval adjustment must be an integer number of semi-tones')
        
        # Define basic parameters
        self._distance = distance
        self._adjustment = adjustment
        
        # The size is just the total number of semitones, including adjustment
        self._size = self._distance + self._adjustment
        
        # Define the direction of the interval, including adjustment
        # Note that we can have positive distance, but negative size, as in (2, -3), a triply diminished major 2nd
        if self._size < 0:
            self._direction = '-'
        elif self._size == 0:
            self._direction = 'u'
        elif self._size > 0:
            self._direction = '+'
            
    def __len__(self):
        return self._size
    
    def __str__(self):
        return 'geninterval(' + str(self._distance) + ', ' + str(self._adjustment) + ')'
        
    def __repr__(self):
        return 'geninterval(' + str(self._distance) + ', ' + str(self._adjustment) + ')'
    
    def __invert__(self): 
        # Switch the direction of the interval
        return geninterval(-1*self._distance, -1*self._adjustment)
                
    def __add__(self, other):
        # Add two intervals by adding the components
        return geninterval(self._distance + other._distance, self._adjustment + other._adjustment)

    def __sub__(self, other):
        # Subtract by adding the inverse
        return self + ~other
    
    def reduce(self, equiv_length):
        # Normally a reduce method here would reduce an interval to the lowest
        # octave, so reduce(geninterval(13, 0)) = geninterval(1, 0). But we're 
        # not assuming that an "octave" is 12 semitones here, so we include
        # the equiv_length parameter.
        if ~(type(equiv_length) == 'int' and equiv_length > 0):
            raise ValueError('Transposition amount must be an integer')
        return geninterval(self._distance % equiv_length, self._adjustment)
    
    def transpose(self, transposition):
        # Transpose the interval by the specified transposition
        if type(transposition) != 'int':
            raise ValueError('Transposition amount must be an integer')
        return geninterval(self._distance + transposition, self._adjustment)
    
    def adjust(self, additional_adjustment):
        # Diminish or augment an interval the specified number of times
        if type(additional_adjustment) != 'int':
            raise ValueError('Transposition amount must be an integer')
        return geninteval(self._distance, self._adjustment + additional_adjustment)
    
    def __abs__(self):
        # Return the equivalent ascending interval
        if self._direction in ('+', 'u'):
            return self
        elif self._direction == ('-'):
            return ~self
    
    def __eq__(self, other):
        # Here we use mathematical equality so we can order intervals by length
        # We'll have a separate method for enharmonic inequality, where a 
        # diminished 3rd isn't the same as an augmented second
        return self._size == other._size
    
    def __ne__(self, other):
        return not self == other
    
    def __lt__(self, other):
        return self._size < other._size
    
    def __le__(self, other):
        return self._size <= other._size
    
    def __gt__(self, other):
        return self._size > other._size
    
    def __ge__(self, other):
        return self.__size >= other._size
    
    def enharm_eq(self, other):
        # We test theoretical equality, where the distance and adjustment both have to be equal
        # (This is not the same as enharmonic equality, where two intervals are equal if they're the same size)
        return self._distance == other._distance and self._adjustment == other._adjustment        

    #def equal_div(self):
        # Return all equal divisions of the interval


#%%


a = geninterval(-13, 5)
b = geninterval(24, 100)
a > b


#%%
class diatonic_prototype:
    """
    Western tonal harmony identifies intervals based on the major scale.
    The major scale is like the "white notes" on a piano
    
    major_scale_prototype = diatonic_prototype([0, 2, 2, 1, 2, 2, 2], 1, ['C', 'D', 'E', 'F', 'G', 'A', 'B'], [0, 5, 7])
    
    The arguments are
    -a list of semi-tone offsets forming the scale degrees
    -a scale continuation offset
    -a list of note letter names
    -a list of "perfect" intervals (that behave differently than regular intervals... 
                                    here we have perfect unisons, perfect 4ths (5 semitones), 
                                    and perfect 5ths(7 semitones))
    
    But this is not the only possible choice. The diatonic prototype specifies
    what we mean by "diatonic"
    It looks similar to a scale (which we define later)
    """
    
    def __init__(self, scale_degrees, continuation_offset, letter_names, perfect_intervals):
        """
        Docstring.
        """
        
        # Validate input
        # TODO
        # This has to be monotonically non-decreasing, no repeats
        # all absolute intervals have to be less than the octave 
        
        # Initialize basic parameters
        self._scale_degrees = scale_degrees
        self._continuation_offset = continuation_offset
        self._letter_names = letter_names
        self._perfect_intervals = perfect_intervals
        
        # Compute block_size (typically it's an octave)
        self._block_size = sum(scale_degrees) + continuation_offset
        
        # Compute diatonic scale size (typically it's 7 notes)
        self._diatonic_scale_size = len(self._letter_names)
        
        # Compute absolute representation
        self._absolute_representation = [self._scale_degrees[0]]
        for i in range(len(self._scale_degrees) - 1):
            self._absolute_representation.append(self._scale_degrees[i+1] + self._absolute_representation[i])
        
        # Compute non-perfect (major/minor intervals) within the octave
        self._maj_min_intervals = sorted(list(set(self._absolute_representation) - set(self._perfect_intervals)))
        
    def __repr__(self):
        return "diatonic_prototype(" + str(self._scale_degrees) + ", " + str(self._continuation_offset) + ", " + str(self._letter_names) + ", " + str(self._perfect_intervals) + ")"
    




#%%
major_scale_prototype = diatonic_prototype([0, 2, 2, 1, 2, 2, 2], 1, ['C', 'D', 'E', 'F', 'G', 'A', 'B'], [0, 4, 5])
major_scale_prototype._block_size

diatonic_prototype_to_use = major_scale_prototype        
        

i = 'ddddddd34+'
d = re.search(r'\d', i).start()
e = re.search(r'[+-]', i).start()

i[:re.search(r'\d', i).start()]
i[e:]
        
#%%
class interval():
    """
    This is our implementation of a western diatonic interval because it's in terms of 
    the major_scale_prototype by assumption (we could define more general interval classes also)
    """
    
    prototype = major_scale_prototype
    
    def __init__(self, interval):
        """
        Class to implement musical intervals. We follow Harmony and Voice Leading
        
        The interval parameter is something like p4+, a5+ or d6- to represent
        a pure fourth up, augmented fifth up, diminished sixth down and such like. We're going 
        to say there are no double diminished or double augmented intervals (or such like).
        
        The key thing we're trying to capture is the function of the note relative to the harmonic
        context.
        
        The last character of the string is either '+' or '-' depending on whether you mean
        the interval is going up or down. The only thing below that depends on direction is
        interval addition.
        
        Perfect intervals can be diminshed or augmented any number of times.
        
        Major intervals can be augmented any number of times. They can become minor,
        and after that they can be diminished any number of times.
        
        We can say things like 'p5+', 'ddddd3+', 'A8-', etc.
        
        The numbers here are in terms of diatonic pitches (not semi-tones)
        """
        
        # Make sure interval string is well-formed
        if not re.match(r'([MmP]|D+|A+)\d+[+-]', interval):
            raise ValueError('Invalid interval name string: must be ([MmP]|D+|A+)\d+[+-]')
                
        # Record this
        self._interval = interval
        
        # Parse the interval string into parts
        interval_first_number = re.search(r'\d', self._interval).start()
        interval_direction_index = re.search(r'[+-]', self._interval).start()
        
        # The interval without the direction
        self._interval_name = self._interval[:interval_direction_index]
        
        # The interval type (just the letter part)
        self._interval_type = self._interval[:interval_first_number]
        
        # How many letters in the interval type (to capture how many times we diminish/augment)
        self._interval_type_length = len(self._interval_type)
        
        # The interval number (just the number)
        #print(self._interval[interval_first_number:interval_direction_index])
        self._interval_number = int(self._interval[interval_first_number:interval_direction_index])
        
        # Reduce the interval number with respect to the block size
        self._interval_number_reduced = self._interval_number % self.prototype._block_size
        
        # Map the interval number to Group 1/Group 2
        if self._interval_number_reduced in self.prototype._perfect_intervals:
            self._interval_group = 'perfect'
        elif self._interval_number_reduced not in self.prototype._perfect_intervals:
            self._interval_group = 'maj/min'
        else:
            self._interval_group = 'error'
        
        # Need to make sure that Group 1/Group 2 intervals are correctly specified
        if self._interval_type == 'P' and self._interval_group == 'perfect':
            pass
        elif self._interval_type in ['M', 'm'] and self._interval_group == 'maj/min':
            pass
        elif self._interval_type[0] in ['d', 'A']:
            pass
        else:
            raise ValueError('Interval type and interval number inconsistent with diatonic prototype')
            
        # Compute the chromatic offset. The rules are different for each group
        if self._interval_group == 'perfect':
            if self._interval_type == 'P':
                self._chromatic_offset = 0
            elif self._interval_type[0] == 'd':
                self._chromatic_offset = -1*self._interval_type_length
            elif self._interval_type[0] == 'A':
                self._chromatic_offset = self._interval_type_length
            else:
                self._chromatic_offset = 'error'
        elif self._interval_group == 'maj/min':
            if self._interval_type == 'M':
                self._chromatic_offset = 0
            elif self._interval_type == 'm':
                self._chromatic_offset = -1
            elif self._interval_type[0] == 'd':
                self._chromatic_offset = -1*(self._interval_type_length + 1)
            elif self._interval_type[0] == 'A':
                self._chromatic_offset = self._interval_type_length + 1
        
        # The interval direction
        self._interval_direction = self._interval[-1:]
        
        # P1s (unisons) have positive direction by convention
        if self._interval_direction == '+':
            self._interval_sign = 1
        elif self._interval_direction == '-':
            self._interval_sign = -1
                      
        # Reduce diatonically
        # Normally this is modding by 7, the number of letter names in a diatonic scale
        self._reduced_diatonic_number = self._interval_number % len(self.prototype._letter_names)
        self._octave_offset = self._interval_number // len(self.prototype._letter_names)
        
        # Compute the underlying non-chromatically adjusted number of semitones
        # using the octave prototype.
        self._reduced_semitones = self.prototype._absolute_representation[self._reduced_diatonic_number - 1]
        self._semitones_unadj = self._reduced_semitones + self.prototype._block_size * self._octave_offset

        # Form the underlying unreduced and reduced generalized intervals
        if self._interval_direction == '+':
            self._geninterval = geninterval(self._semitones_unadj, self._chromatic_offset)
            self._geninterval_reduced = geninterval(self._reduced_semitones, self._chromatic_offset)
        elif self._interval_direction == '-':
            self._geninterval = ~geninterval(self._semitones_unadj, self._chromatic_offset)
            self._geninterval_reduced = ~geninterval(self._reduced_semitones, self._chromatic_offset)
     
    def __repr__(self):
        return "interval(" + self._interval + ")"
    
    def reduce(self):
        return interval(self._interval_type + str(self._reduced_diatonic_number) + self._interval_direction)



#%%
    
asdf = interval('P4+')

intervals_to_test = []
parameters_to_test = []


#%%








































###################################################################################









# Translates diatonic intervals within one octave into the corresponding number of semi-tones
# We'll say there's no such thing as d1 or d8 (diminished unison or diminished octave)
diatonic_to_num_semitones = {
    'p1': 0,
'a1': 1,
'd2': 1,
'p2': 2,
'a2': 3,
    'i3': 3,
    'm3': 4,
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
10: 'd7',
11: 'd8'}











def semitones_to_diasteps(num_semitones):
    """
    Take an integer number of semitones and return a list of all possible diatonic intervals
    corresponding to that number. If num_semitones < 0, return a descending interval.
    
    This function is not actually a method that operates on intervals, though it returns intervals,
    so we define it here in open code, not in the interval class
    
    For multi-valued outputs of this function, we leave it to downstream processes to choose a unique value
    when necessary.
    
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
    
    # Account for numbers higher than 12 (one octave)
    base_num_semitones = raw_num_semitones % 12
    octave_offset = raw_num_semitones // 12
    
    # Store our (possibly multi-valued) results in a list
    possible_results = []

    # Helper function for processing each of the three cases
    def process_interval_type_case(interval_type, dictionary_to_use):
        if base_num_semitones in dictionary_to_use:
            base_diatonic_interval = dictionary_to_use[base_num_semitones]
            new_interval_number = int(base_diatonic_interval[1:]) + 7*octave_offset
            print('new_interval_number is ' + str(interval(interval_type + str(new_interval_number) + new_direction)))
            possible_results.append(interval(interval_type + str(new_interval_number) + new_direction))
        else:
            pass

    # Process all three cases, appending to the list when necessary                
    process_interval_type_case('p', num_semitones_to_pure)
    process_interval_type_case('a', num_semitones_to_augmented)
    process_interval_type_case('d', num_semitones_to_diminished)

    return possible_results
semitones_to_diasteps(11)
11 // 12
"""
interval('d8+') problem: this doesn't exist' because this below looks up 'd1'
self._base_length = diatonic_to_num_semitones[self._reduced_interval_name]
"""

def dereference_diasteps_output(list_of_ints, target_num):
    """
    We need to be able to dereference a multivalued list of intervals from 
    semitones_to_diasteps. Usually we do this by choosing what degree of the
    scale we're talking about. We implement that here via target_num
    """
    for i in range(len(list_of_ints)):
        if list_of_ints[i]._interval_number == target_num:
            return list_of_ints[i]
        
    # if we found nothing
    raise ValueError("No interval with that number can be found")
    


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
        context.
        
        The last character of the string is either '+' or '-' depending on whether you mean
        the interval is going up or down. The only thing below that depends on direction is
        interval addition.
        
        We use '+' as the default direciton.
        
        Pure interval categories (fundamental plus octave shifted):
            Unison/Octave/Fifteenth: p1+, p8+, p15+, etc. (1 + 7n for n >= 0)      
            Second/Ninth/Sixteenth: p2+, p9+, p16+, etc. (2 + 7n for n >= 0)
            Third/etc.: p3+, p10+, p17+, etc. (3 + 7n for n >= 0)
            Fourth: p4+, p11+, p18+, etc. (4 + 7n for n >= 0)
            Fifth: p5+, p12+, p19+, etc. (5 + 7n for n >= 0)
            Sixth: p6+, p13+, p2+0, etc. (6 + 7n for n >= 0)
            Seventh: p7+, p14+, p21+ etc. (7 + 7n for n >= 0)

            General: reduced_interval_number + 7*octave_offset

        Augmentable intervals: a1+, a2+, a3+, a4+, a5+, a6+ and further octave shifts
        Diminishable intervals: d2+, d3+, d4+, d5+, d6+, d7+, d8+ and further octave shifts
        Basically, d1+ doesn't exist, and a7+, a14+, a21+, etc. don't exist
        """
        
        # Validate interval_name input
        # Has to be a string with a, d, or p followed by an integer > 1 followed by + or -
        # and can't be d1 or a7, a14, a21, etc
        
        if not re.match(r'[adp]\d+[+-]', interval):
            raise ValueError('Interval name must be [adp] followed by a number > 1 followed by a + or -')
            
        if int(interval[:-1][1:]) < 1:
            raise ValueError('Interval number must be > 1')
        
        if interval[:-1] == 'd1':
            raise ValueError("diminshed 1s don't exist in this system")
        
        if interval[:-1][0] == 'a' and int(interval[:-1][1:]) % 7 == 0:
            raise ValueError("augmented sevenths (and octave shifts) don't exist in this system")
            
                
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
        a list of such names, and leave it to each downstream process to choose the right enharmonic value from
        the list where a single value is required.
        
        Use this code to convince yourself that we can add any two types of intervals, and have the result be any of the two types.
        
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
        
        # Use the non-class function to compute all allowable interval representations for the number
        # of semitones we computed.
        print(new_num_semitones)
        return semitones_to_diasteps(new_num_semitones)
    
    
    def __sub__(self, other):
        """
        Interval subraction is the opposite of interval addition.
        
        Again, we return a list of all possible results, to be disambiguated later.
        """
        return self + other.reverse_direction()
    
    def reduce(self):
        """
        We store the components of this as strings when we initialize an interval. Here's a way
        to get the reduced interval form as an interval object to be used for computations.
        """
        
        reduced_interval_string = self._reduced_interval_name + self._interval_direction
        return interval(reduced_interval_string)
    
    
    def invert(self, wrt):
        """             
        Invert an interval with respect to (wrt) an octave up, or some other
        (positive or negative) distance that we specify.
        """
        return wrt - self
    
    def enharmonically_equal(self, other):
        """
        This is an equality function for two intervals that are enharmonically equivalent. In practice, this means that 
        their interval strings are identically equal, so 'a4+' == 'a4+' but 'a4+' != 'd5-'. (We save the __eq__ method for
        testing if the intervals have the same length on a piano keyboard, and 'a4+' == 'd5+'.)
        """
        
        if self._interval == other._interval:
            return True
        else:
            return False
    
    
    def __eq__(self, other):
        """
        We need a way to order intervals. We'll do it by how wide they are, so an augmented fourth is equal to a diminished fifth.
        Of course, enharmonically they are very different, but when comparing intervals, we'd like to be able to say things like 
        "any interval equal to or smaller than a tritone"--that is, use the <= operator without caring about enharmonicism            
        
        We'll say that descending intervals have "negative width". 
        
            'p1+' < 'a1+' = 'd2+' < 'p2+' < 'a2+' = 'd3+' < 'p3+' = 'd4+' < 'a3+' = 'p4+' < 'a4+'= 'd5+' < 'p5+' < 'a5+' = 'd6+' < 'p6+'< 'a6+' = 'd7+' < 'p7+' < 'p8' < ...
        
        So:
            -the numbers break order around the half step between the 3 and 4 in an ionian scale
            -if the interval numbers are equal, we have dX < pX < aX
            -if we have intervals with number x and x + 1, 
                -a(x) = d(x+1)
                -p3 = d4 and a3 = p4, and anything else with the numbers congruent to this mod 7
            -if we have intervals with numbers x and y >= x + 2, y > x
            -descending intervals are ordered in reverse of the corresponding ascending intervals (so 'p5-' < 'd5-' < ... < 'd5+' < 'p5+')
        """
        
        # Compute these to make it easier to compare our intervals in a second
        self_comp = self.reduce()._interval_name
        other_comp = other.reduce()._interval_name
        
        # if they're literally the same string
        if self.enharmonically_equal(other) == True:
            return True
        # if they have the same direction
        elif self._interval_direction == other._interval_direction:
            # handle the case of the half step between 3 and 4 in an ionian scale in the first four lines
            if (self_comp == 'p3' and other_comp == 'd4') or \
               (self_comp == 'd4' and other_comp == 'p3') or \
               (self_comp == 'a3' and other_comp == 'p4') or \
               (self_comp == 'p4' and other_comp == 'a3') or \
               (self_comp == 'a4' and other_comp == 'a3'):
                   return True
            # handle the standard case where stuff is equal (don't need to reduce here)
            elif (self._interval_number + 1 == other._interval_number and self._interval_type == 'a' and other._interval_type == 'd') or \
                 (self._interval_number == other._interval_number + 1 and self._interval_type == 'd' and other._interval_type == 'a'):
                     return True
            else:
                return False
        # if they have different directions then they're trivially not equal
        elif self._interval_direction != other._interval_direction:
            return False
        else:
            raise ValueError('Interval comparison case not handled!')
        

    def __lt__(self, other):
        """
        See the discussion of __eq__ for this.
        """
        
        # If self's interval number is one or more less than other, and they're not equal, then self < other.
        if self._interval_number + 1 <= other._interval_number and self.__eq__(other) == False:
            return True
        # if interval numbers are equal
        if self._interval_number == other._interval_number:
                # here it differs based on interval direction
                if (self._interval_type == 'd' and other._interval_type == 'p') or (self._interval_type in ['d', 'p'] and other._interval_type == 'a'):
                    result_for_pos_int_dir = True
                else:
                    result_for_pos_int_dir = False                 
                if self._interval_direction == '+':
                    return result_for_pos_int_dir
                else:
                    return not result_for_pos_int_dir
        else:
            #raise ValueError('Interval comparison case not handled!')
            return False
        
    def __le__(self, other):
        """
        Use __eq__ and __lt__.
        """
        
        return self.__eq__(other) or self.__lt__(other)
    
    def __ne__(self, other):
        """
        Negate __eq__.
        """

        return not self.__eq__(other)
    
    def __gt__(self, other):
        """
        Negate __le__.
        """
        
        return not self.__le__(other)
    
    def __ge__(self, other):
        """
        Negate __lt__.
        """
        
        return not self.__lt__(other)
    
    def __abs__(self):
        """
        |p4+| == |p4-| == p4+, and so on.
        """
        
        if self._interval_direction == '+':
            return self
        elif self._interval_direction == '-':
            corresponding_positive_interval = self._interval_name + '+'
            return interval(corresponding_positive_interval)
        

#%%
            
interval('p2+') + interval('p6+')        
        
a = interval('p4+')
b = interval('p4-')
#abs(b)

interval('p2+') < interval('p1+')
    
#%%

class scale:
    """
    A scale is an ordered list of intervals, a continuation offset, and a degree list.
    
    We allow for a great deal of generality. We can represent
    -Non-monotonic scales (ones where the next pitch is not necessarily higher than the previous)
    -Scales that don't repeat at the octave (they can have any positive integer period)
    -Scales that don't start on the root (like playing G pentatonic over a C root)
    
    We do, however, limit ourselves to western equally-tempered 12-tone theory when constructing our scales.
     
    The list of intervals starts out with the root, which is the identity 'p1+' for rooted scales. Subsequent intervals tell how far to
    go to get to the next note.   
    
    But scales can be rootless and not have a 'p1+' in their interval list. For example, we might imagine playing a G pentatonic
    scale [D, E, G, A, B] with respect to a C root. Here, the first interval would be 'p2+' (the distance from C to D).
    
    The subsequent intervals give the distance to the next note relative to the previous note. This list does not include the "top" pitch of the scale.
    For example, a C ionian scale is commonly played as C D E F G A B C, where that last C is just a pivot point for beginning the descent,
    or continuing into a second octave. For us, though, a C ionian scale is just the ordered pitch collection C D E F G A B--we don't repeat the C at the end.
    Instead, we give a continuation offset which says how far to go from B to continue playing the scale. In this case, the continuation
    offset would be 'd2+', representing the half step from B to C. Then a 2-octave version of this scale would be C D E F G A B C D E F G A B C.
    Of course, if we used 'p2+', we'd get C D E F G A B C# D# E# F# G# A# B#. So the continuation offset enables us to achieve pan-octave
    generality in the scales we represent.
    
    The intervals in a C ionian scale are commonly given as WWHWWWH, where W is a whole step and H is a half step. For us, the interval list
    plus the continuation offset is as follows (with the next line showing an example with C ionian):
    
                    ['p1+', 'p2+', 'p2+', 'd2+', 'p2+', 'p2+', 'p2+'], 'd2+'
        (C root)          C      D       E     F      G      A        B     C
    
    Giving scales in terms of relative intervals like this is simple and compact. We can easily calculate the corresponding absolute scale representation.
    And in the pitch class, we will "render" scales with a given pitch as the root as a list of the corresponding pitches built off of that root.
    
    There's also the degree list which tells us what diatonic function each abstract relative pitch in the scale has with respect to the root. This encodes each
    pitch's functionality and enables us to use it later. Of course, we don't need to specify actual pitches to do this. Let's put a line for the degree
    list in our example above:

                    ['p1+', 'p2+', 'p2+', 'd2+', 'p2+', 'p2+', 'p2+'], 'd2+'
        (C root)          C      D       E     F      G      A        B     C
                    [     1,     2,      3,    4,     5,     6,       7,    8]
        
    This represents things like "E is a diatonic 3 in C ionian" and "when continuing a C scale past the first period, the next note is C, which is a 
    diatonic 8 (octave) in C ionian".
    
    Let's recall what a "diatonic 3" is, because it's important for what we're doing. When moving up steps of scales with degree list [1, 2, 3, 4, 5, 6, 7],
    the pitches need to be spelled in some mathematical interval of the repeated list of diatonic pitches, [A, B, C, D, E, F, G]*n for some n, with chromatic
    alterations to match. For example, an E ionian scale is E F# G# A B C# D#, where we wrap around the list of pitches going from G# back to A. We wouldn't
    write E F# Ab A B C# D#. Ab is not a 3 in the key of E--we've skipped the letter G. Ab is the same pitch, but it represents a "flat 4" in the key of E, which
    is weird. Unless something very special is going on, we shouldn't spell that pitch this way when writing an E scale.
    
    Now consider an E# ionian scale. By the above paragraph, we should spell it E#, Fx, Gx, A#, B#, Cx, Dx. It's exactly the same pitches and keys on the piano as
    an F ionian scale, F G A Bb C D E. But if we're viewing it as E#, the proper diatonic spelling is the one we just gave. It would be a mistake to "dereference"
    Gx to A, because A is a 4 in the key of E#.
        
    Anyway, the full initialization of the ionian scale, with the intervals, continuation offset, and degree list is:
        
        c_ionian = scale(['p1+', 'p2+', 'p2+', 'd2+', 'p2+', 'p2+', 'p2+'], 'd2+', [1, 2, 3, 4, 5, 6, 7, 8])
    
    """
    
    
    def __init__(self, list_of_interval_strings, continuation_offset, degree_list):
        """
        The list_of_interval_strings is a list of intervals that we initialize using shorthand notation--
        so instead of initializing with list_of_interval_strings as [interval('p1+'), interval('p2+'), interval('p2+')],
        we can initialize using list_of_interval_strings = ['p1+', 'p2+', 'p3+']. The list must either
        start with 'p1+' (rooted) or not contain 'p1+' (rootless)
        
        Similarly, continuation_offset is an interval string. This parameter tells us how to add scales together,
        which enables hyperdiatonic systems and other things.
        
        The degree list is just a list of numbers.
        """
        
        
        self._degree_list = degree_list
        
        # Preserve the string version of all these for later
        self._str_list_of_interval_strings = list_of_interval_strings
        self._str_continuation_offset = continuation_offset
        
        converted_interval_strings = []
    
        for interval_string in list_of_interval_strings:
            converted_interval_strings.append(interval(interval_string))
            
        self._scale_steps = converted_interval_strings
        
        # make sure offset is an interval string
        self._continuation_offset = interval(continuation_offset)
        
        # mark rooted or rootless
        if 'p1+' in list_of_interval_strings:
            self._rootness = 'rooted'
        else:
            self._rootness = 'rootless'
                     
    
    def __str__(self):
        """
        String representation
        """
        return '[' + ', '.join(self._str_list_of_interval_strings) + '], ' + self._str_continuation_offset + ', ' + str(self._degree_list)


    def __repr__(self):
        """
        We have to do a bit of work to return the appropriate string
        """
        return 'scale([' + ', '.join(self._str_list_of_interval_strings) + '], ' + self._str_continuation_offset + ', ' + str(self._degree_list) + ')'
           
    
    def __getitem__(self, index):
        return self._scale_steps[index]
    
    
    def get_mode(self, mode_number):
        """
        Return the given mode of the given scale, meaning cyclically permute the list of
        interval strings and continuation offset and degree list right by one place. We do this 
        in a very general way to handle non-monotonic scales and non-rooted scales
        """
        
        # mode_number has to be a positive integer
        if mode_number <= 0:
            raise ValueError('mode_number must be a positive integer')
        
        # Get a list of the interval strings because it's easier to work with
        full_interval_list = self._str_list_of_interval_strings + [self._str_continuation_offset]
        
        # The first interval gives the rootedness of the scale, and we define all modes of a given scale to have
        # the same rootedness as that scale. To compute each mode, we simply do a cyclic permutation of the
        # remaining intervals mode_number places to the left
        rootedness = full_interval_list[0]
        intervals_to_permute = full_interval_list[1:]
        
        # First we handle the interval list
        # We usually talk about "the first through seventh" modes of an ionian scale, so "mode 1" of a scale here
        # is just the scale itself (in other words, we don't zero-index the way Python normally would). 
        permuted_intervals = intervals_to_permute[mode_number - 1:] + intervals_to_permute[:mode_number - 1]
        new_list_of_interval_strings = [rootedness] + permuted_intervals[:-1]
        new_continuation_offset = permuted_intervals[-1]
        
        # Now we handle the degree list in a similar way. We'll write a function to do one permutation and then
        # run that function mode_number of times. We record some notes about the degree list. The first number
        # is the same by definition across all modes, since all modes of a given scale have the same rootedness
        # as that scale. The last number of the degree list is the number of the continuation offset, which will be the
        # same for all modes, since the distance between it and the root is the same (we add the same intervals, but in 
        # a different cyclic permutation). First step is chop off the first number of the degree list to get a new list. Then we
        # decrement all numbers in the new list by (the second number - the first number) of the list. Then we add the
        # last degree back on. The new first degree then is the same as the old first degree by construction.
        def permute_degrees_once(degree_list):            
            last_degree = degree_list[-1]
            degree_list_to_decrement = degree_list[1:]
            decrement = degree_list[1] - degree_list[0]
            decremented_degree_list = [degree - decrement for degree in degree_list_to_decrement]
            return decremented_degree_list + [last_degree]
        
        # Call this function mode_number - 1 times to get the final degree list
        # (for the first mode, we do nothing, so degree_list doesn't change)
        new_degree_list = self._degree_list
        for i in range(mode_number - 1):
            new_degree_list = permute_degrees_once(new_degree_list)

        # Return a scale with all of the new parameters we calculated
        return scale(new_list_of_interval_strings, new_continuation_offset, new_degree_list)
    
    
    def __len__(self):
        """
        The length of a scale is what we need to loop over when doing stuff,
        so we'll define it as the length of the interval string list.
        In other words, the length is how many notes in the scale, not the cumulative interval the scale traverses.
        So a C ionian scale has length 7, because it is C D E F G A B.
        """

        return len(self._str_list_of_interval_strings)
    
    
    def scale_span(self):
        """
        Gives the interval span between the first and last notes of the scale. For monotonic scales, this is just the 
        distance between the first and last note, regardless of whether there is any non-monotonicity. We compute it 
        using the scale's constituent intervals. The first interval gives the rootedness of the scale, so we ignore it.
        We then sum up the second through last intervals to get the span.
        We don't include the continuation offset, so the span of a C ionian scale is a pure seventh
        For non-rooted scales, we don't include the root in the computation, so the span of D E G A B 
        with a C root is just D to B, a major sixth.
        """
        
        # initialize an identity span
        span = [interval('p1+')]
        
        # iterate over the scale intervals ignoring the root and the continuation offset
        for step in self._scale_steps[1:]:
            span = [i + step for i in span][0]
        
        return span
    
        
    def scale_cum_span(self):
        """
        Gives the total interval distance spanned by the scale. For monotonically increasing scales,
        this is equal to scale_span. This is the same logic as scale_span, but with the absolute
        value of the interval size.
        """
        
        # initialize an identity span
        span = [interval('p1+')]
        
        # iterate over the scale intervals ignoring the root and the continuation offset
        for step in self._scale_steps[1:]:
            span = [i + abs(step) for i in span][0]
        
        return span
        
    
    def widest_consec_interval(self):
        """
        Return the widest consecutive interval in the scale.
        """
        
        # initialize an identity interval
        widest = interval('p1+')
        
        # iterate over the scale intervals ignoring the root and the continuation offset
        for step in self._scale_steps[1:]:
            if step > widest:
                widest = step
        
        return widest
    
    
    def __add__(self, other):
        """
        Adding two scales means sticking the intervals of other after the intervals of self via the continuation offset
        We also need to combine the two degree lists. The intervals we get when we do this will govern the enharmonic 
        spellings of the notes when we render the new scale relative to a pitch.
        
        We basically want to be able to combine existing scales together to get new scales.
                
        Take the lydian tetrachord as an example:
        
            lyd_tc = scale(['p1+', 'p2+', 'p2+', 'd2+'], 'p2+', [1, 2, 3, 4, 5])
            ... so like c d e f
        
            lyd_tc + lyd_tc should be scale(['p1+', 'p2+', 'p2+', 'd2+', 'p2+', 'p2+', 'p2+', 'd2+'], 'p2+', [1, 2, 3, 4, 5, 6, 7, 8, 9])
            ... so like c d e f g a b c
        
        Compare this to ionian_scale = scale(['p1+', 'p2+', 'p2+', 'd2+', 'p2+', 'p2+', 'p2+'], 'd2+', [1, 2, 3, 4, 5, 6, 7]),
        which is not the same thing. We can iterate lydian tetrachords to get Jacob Collier's super ultra hyper mega meta lydian
        scale with a huge period, but we iterate the ionian scale and it has a period of seven--so unlike in casual conversation, 
        here we have
        
            lyd_tc + lyd_tc != ionian_scale
        
        because the underlying structure and representation are different.
        
        So the procedure for adding scale_1 + scale_2 is
        
        -start with scale_1's interval string
        -append scale_1's continuation offset to the list (if scale_2 is rootless, this gives the new "implicit root")
        -then
            -if scale_2 is rooted, delete the 'p1+' from scale_2. 
            -if scale_2 is rootless, don't do anything
        -append scale_2's remaining interval string
        -new continuation offset is scale_2's
        -increment scale_2's degree list by the highest degree in scale_1's degree list and append it to scale_1's degree list
        -initialize a new scale with these parameters
        
        All of this works exactly the same way for non-monotonic scales and scales with more than 7 notes.
        
        To take an example, look at
        
        big_scale = scale(['p1+', 'p2+', 'p2+', 'd2+', 'p2+', 'p2+', 'p2+', 'p2+', 'p2+', 'd3+'], 'p2+', [1, 2, 3, 4, 5, 6, 7, 8, 9, 11])
        ... so like         c,     d,     e,     f,     g,     a,     b,     c#,    d#,    f#
        
        Then big_scale + lyd_tc should give us
        
         big_scale + lyd_tc = scale(['p1+', 'p2+', 'p2+', 'd2+', 'p2+', 'p2+', 'p2+', 'p2+', 'p2+', 'd3+', 'p2+', 'p2+', 'd2+'], 'p2+', [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13])
         ... so like                  c,     d,     e,     f,     g,     a,     b,     c#,    d#,    f#     g#     a#     b
    
        Everything generalizes naturally to rootless scales, non-monotonic scales, and scales that are not an octave long
        
        Subtraction isn't really defined--do we ever want to reduce scales somehow?
        
        """
        
        # start with scale_1's interval string
        # append scale_1's continuation offset to the list (if scale_2 is rootless, this gives the new "implicit root")
        # then
        #    if scale_2 is rooted, delete the 'p1+' from scale_2. 
        #    if scale_2 is rootless, don't do anything
        # append scale_2's remaining interval string
        if self._rootness == 'rooted':
            new_interval_list = self._str_list_of_interval_strings + [self._str_continuation_offset] + other._str_list_of_interval_strings[1:]
        elif self._rootness == 'rootless':
            new_interval_list = self._str_list_of_interval_strings + [self._str_continuation_offset] + other._str_list_of_interval_strings
        
        # new continuation offset is scale_2's
        new_continuation_offset = other._str_continuation_offset
        
        # increment scale_2's degree list by the highest degree in scale_1's degree list and append it to scale_1's degree list
        self_highest_degree = max(self._degree_list)
        scale_2_incremented_degree_list = [x + self_highest_degree for x in other._degree_list]
        new_degree_list = self._degree_list + scale_2_incremented_degree_list
        
        # initialize a new scale with these parameters
        return scale(new_interval_list, new_continuation_offset, new_degree_list)
           
    
    def __mul__(self, integer):
        """
        Define integer multiplication so we can do things like my_scale*4
        """
        
        result = self
        
        for i in range(integer - 1):
            result += self
            
        return result
        
    
    # def invert(self):
        """
        I don't think we need an invert method for scales.
        """
    
    def absolute_scale_repr(self):
        """
        Take relative scale representation. For example:
            
            c_ionian = scale(['p1+', 'p2+', 'p2+', 'd2+', 'p2+', 'p2+', 'p2+'], 'd2+', [1, 2, 3, 4, 5, 6, 7, 8])
            
        Return a list of intervals where each interval gives the relationship of the note to the root, not the previous note:
            
            ionian_scale.absolute_scale_repr() = ['p1+', 'p2+', 'p3+', 'p4+', 'p5+', 'p6+', 'p7+']        
            
        Here's one payoff for everything we've built so far: the scale's degree list tells which version of the
        multi-valued interval addition that we need to pick!
        """
       
        # Start with the first interval, because this one will stay the same
        absolute_scale = [self._scale_steps[0]]
        
        # Loop through the remaining intervals and add them to the previous interval.
        # Dereference multivariate values against the degree list!
        for i in range(len(self._scale_steps[1:])):
            print(self._scale_steps[i+1])
            print(absolute_scale[i])
            possib_multiv_interval = self._scale_steps[i+1] + absolute_scale[i]
            print(possib_multiv_interval)
            print(self._degree_list[i+1])
            print("\n")
            deref_possib_multiv_interval = dereference_diasteps_output(possib_multiv_interval, self._degree_list[i+1])
            absolute_scale.append(deref_possib_multiv_interval)
            
        print(absolute_scale)

            
 
#%%      

c_ionian = scale(['p1+', 'p2+', 'p2+', 'd2+', 'p2+', 'p2+', 'p2+'], 'd2+', [1, 2, 3, 4, 5, 6, 7, 8])
c_ionian.absolute_scale_repr()  


          
#iss = scale(['p2+', 'p2+', 'd3+', 'p2+', 'p2+'], 'd3+', [2, 3, 5, 6, 7, 9])
#iss.absolute_scale_repr()
#iss._degree_list

#iss = scale(['p2+', 'p2+', 'd3+', 'p2+', 'p2+'], 'd3+', [2, 3, 5, 6, 7, 9])
#iss.absolute_scale_repr()
#iss._degree_list

#%%       
   
    def compute_density(self):
        """
        The density of a scale is the number of unique pitches it contains divided by 12, the number of total
        unique pitches. It doesn't consider the span of the scale.
        
        We use the diatonic_to_num_semitones variable to compute relative numbers of semitones from the root
        """
        
        
        


#%%




class pitch:
    
    """
    For this system, a pitch corresponds to a key on a theoretically infinite piano. For practical
    purposes, most of the stuff we do takes place on the 88 actual piano keys.
    
    In doing this, we lock ourselves into Western 12-tone equal tempered music system, like on a piano. 
    Music that doesn't fit into this system is beyond the scope of this package.

    There are several representations for each pitch. 
    
    We'll use middle C as an example.

    The underlying unique representation (i.e., no enharmonic or other equivalents) for this note is
    40, because it's the 40th key from the left on a piano. This representation doesn't care how the pitch
    is enharmonically spelled.
    
    We use lilypond notation to spell pitches. In this notation, we have
    -is means sharp
    -isis means double sharp
    -es means flat
    -eses means double flat
    -there are no triple or higher accidentals possible in lilypond
    
    Enharmonically, a C could be spelled
    -c
    -bis
    -deses
    
    Since we're talking about middle C, we also need to specify the octave. In lilypond, c, d, e, f, g, a, b correspond
    to the C one octave below middle C, and higher octaves can be specified by c', c'', etc, and 
    lower octaves can be specified as c, c,, c,,, and so forth. This is absolute pitch entry. 
    Lilypond also has relative pitch entry, but we don't use it here.
    
    So middle C could be enharmonically spelled
    -c'
    -bis
    -deses'
    
    But we want to capture general enharmonicism. This is why we initialize a pitch as a pair:
    (diatonic_pitch, chromatic_alteration). The diatonic_pitch is the letter name of the note and 
    the chromatic_alteration is an integer that represents how sharp or flat the pitch is. For example,
    middle C could be
    -(40, 0), corresponding to c'
    -(39, 1), corresponding to bis
    -(42, -2), corresponding to deses
    -(47, -7), corresponding to g hexuple flat 
    -but not (46, -6), because 46 is f#/gb... need to test for all of this, maybe for invalid ones like this, 
    dereference it to the nearest valid one
    
    To figure out the correct spelling, we first differentiate between root pitches and functional pitches. These
    different functions are not inherent to the concept of a pitch, rather, they come up when we're rendering
    scales and other things.
    
    A root pitch gives the tonal center for the current environment. Out of the many possible representations,
    we have to choose exactly one. This allows us to be in the tonal center of Ab or G# to take one example, or
    in the key of C, B#, or Dbb, to take another example. At this point, though, we're not locked into the usual "key" 
    of these, becase our system is much more general than this and allows much more complicated stuff.
    
    Functional pitches are pitches that we view as functioning relative to some scale based off of some root pitch.
    
    We need to flesh this out a bit, but the basic idea is that Eb is functioning as a 4 in a Bb ionian environment.
    Conversely, the 4 in Bb ionian is Eb (not D#) because diatonically we have b, c, d, e (up to accidentals), so
    the 4 in Bb ionian can't be some kind of D.

    Similarly, we have the question of "how do we view C# in an A dorian environment?". To answer this, we consider
    chords built on thirds, like 
    
        A  C  E  G  B  D  F#  A  C#  E  G#  B  D#  F# 
        1  3  5  7  9  11 13  15 17  19 21  23 25  27
        
    So, diatonically, C is the 3, the 10, the 17, the 24, the 31, etc. of A. In A dorian, the 3 is a C natural
    In stacking thirds, the 10 doesn't come up. The next C that comes around is the 17, so it can be sharp.
    

    """
    

            
    # Letter names of diatonic notes in order
    diatonic_sequence = ['a', 'b', 'c', 'd', 'e', 'f', 'g']     
    
    def __init__(self, diatonic_pitch, chromatic_alteration):
        """
        asdf
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
            except:
                pass
        
        
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
   
    




















# encode simplest sharp and flat representations of each pitch
# in terms of cc_pitch_num
base_lilypond_octaves = {
    35: ["b", "x", "aisis", "ces'", "x"],
    34: ["x", "ais", "x", "bes", "ceses"],
    33: ["a", "x", "gisis", "x", "beses"],
    32: ["x", "gis", "x", "aes", "x"],
    31: ["g", "x", "fisis", "x", "aeses"],
    30: ["x", "fis", "eisis", "ges", "x"],
    29: ["f", "eis", "x", "x", "geses"],
    28: ["e", "x", "disis", "fes", "x"],
    27: ["x", "dis", "x", "ees", "feses"],
    26: ["d", "x", "cisis", "x", "eeses"],
    25: ["x", "cis", "bisis", "des", "x"],
    24: ["c", "bis,", "x", "x", "deses"]}

def get_attrs(pitch_num):
    """
    Get attributes of a c-centered pitch number
    All pitches will be c-centered for this exercise
    """
       
    # get an a-centered pitch number just in case
    a_centered_pitch_num = pitch_num + 4
    
    # do basic computations
    octave_num = math.floor(pitch_num/12) + 1
    pitch_freq = 2**((pitch_num - 45)/12)*440 # in terms of A440
    
    # get pitch color on piano
    if pitch_num % 12 in [0, 2, 4, 5, 7, 9, 11]:
        pitch_color = 'white'
    elif pitch_num % 12 in [1, 3, 6, 8, 10]:
        pitch_color = 'black'
        
    # get note equivalence classes in the octave below middle c
    # (where the lilypond octave modifier is null)
    equiv_pitch_oct_bel_mc = (pitch_num % 12) + 24
    
    # Get the simplest representations for a given pitch
    # Represent it as locations in the base_lilypond_octaves list
    # simplest natural representation is always 1, so we don't need that
    # This is essentially lots of data entry to capture the structure of a 
    # Diatonic octave
    if equiv_pitch_oct_bel_mc == 24:
        simplest_flat_rep_oct_bel_mc = 4
        simplest_sharp_rep_oct_bel_mc = 1
    elif equiv_pitch_oct_bel_mc == 25:
        simplest_flat_rep_oct_bel_mc = 3
        simplest_sharp_rep_oct_bel_mc = 1
    elif equiv_pitch_oct_bel_mc == 26:
        simplest_flat_rep_oct_bel_mc = 4
        simplest_sharp_rep_oct_bel_mc = 2
    elif equiv_pitch_oct_bel_mc == 27:
        simplest_flat_rep_oct_bel_mc = 3
        simplest_sharp_rep_oct_bel_mc = 1
    elif equiv_pitch_oct_bel_mc == 28:
        simplest_flat_rep_oct_bel_mc = 3
        simplest_sharp_rep_oct_bel_mc = 2
    elif equiv_pitch_oct_bel_mc == 29:
        simplest_flat_rep_oct_bel_mc = 4
        simplest_sharp_rep_oct_bel_mc = 2
    elif equiv_pitch_oct_bel_mc == 30:
        simplest_flat_rep_oct_bel_mc = 3
        simplest_sharp_rep_oct_bel_mc = 1
    elif equiv_pitch_oct_bel_mc == 31:
        simplest_flat_rep_oct_bel_mc = 4
        simplest_sharp_rep_oct_bel_mc = 2
    elif equiv_pitch_oct_bel_mc == 32:
        simplest_flat_rep_oct_bel_mc = 3
        simplest_sharp_rep_oct_bel_mc = 1
    elif equiv_pitch_oct_bel_mc == 33:
        simplest_flat_rep_oct_bel_mc = 4
        simplest_sharp_rep_oct_bel_mc = 2
    elif equiv_pitch_oct_bel_mc == 34:
        simplest_flat_rep_oct_bel_mc = 3
        simplest_sharp_rep_oct_bel_mc = 1
    elif equiv_pitch_oct_bel_mc == 35:
        simplest_flat_rep_oct_bel_mc = 3
        simplest_sharp_rep_oct_bel_mc = 2
    
    # get lilypond octave modifier
    if octave_num == 3:
        lilypond_octive_modifier_type = 'none'
        lilypond_octive_modifier_quantity = 0
    elif octave_num >= 4:
        lilypond_octive_modifier_type = "'"
        lilypond_octive_modifier_quantity = octave_num - 3
    elif octave_num <=2:
        lilypond_octive_modifier_type = ","
        lilypond_octive_modifier_quantity = -1*octave_num + 3
    
    lilypond_octave_modifier = lilypond_octive_modifier_type*lilypond_octive_modifier_quantity
    
    # Put it all together to get a list of possible lilypond spellings
    # Xs represent nulls, so they don't get modified
    lilypond_spellings = []    
    for item in base_lilypond_octaves[equiv_pitch_oct_bel_mc]:
        if item == "x":
            lilypond_spellings.append(item)
        elif item != "x":
            lilypond_spellings.append(item + lilypond_octave_modifier)
        
    # Test
    return lilypond_spellings

    
    # dereference "," (octave lower) and "'" (octave higher) when they're together (i.e., '', is equal to ')
    while lilypond_spellings.find("',") > 0:
        location = lilypond_spellings.find("',") 
        lilypond_spellings = lilypond_spellings[0:location] + lilypond_spellings[location + 2:]
    
    while lilypond_spellings.find(",'") > 0:
        location = lilypond_spellings.find(",'") 
        lilypond_spellings = lilypond_spellings[0:location] + lilypond_spellings[location + 2:]

    return lilypond_spellings
    

get_attrs(50)
# function to derefrence ',',' for a single pitch, apply to all pitches
# Method to get the hexuple-flat version of the pitch





class harmonica_hole:
    """
    Implements a harmonica hole. Harmonicas have a given key, and holes relative to that key. An individual
    harmonica hole has a blow pitch and a draw pitch that are a certain interval relative to each other, and that's
    all we need to compute its individual properties. Then we can implement a whole harmonica by arranging
    these holes together, along with the relationship to the individual harmonica pitch.
    
    But we don't want to get in to the specifics of the enharmonics at this point--all we need is the number
    of semitones bewteen the blow pitch and draw pitch (with sign) to do the computation.
    
    Richter tuned harmonica example:
        hole 01: harmonica_hole(2) (C up to D, for example)
        hole 02: harmonica_hole(3)
        hole 03: harmonica_hole(4)
        hole 04: harmonica_hole(2)
        hole 05: harmonica_hole(2)
        hole 06: harmonica_hole(2)
        hole 07: harmonica_hole(-1)
        hole 08: harmonica_hole(-2)
        hole 09: harmonica_hole(-2)
        hole 10: harmonica_hole(-3)
    
    So this class just captures the unique playing technique of each hole. We render the exact pitches
    later when we put these together to construct harmonicas.
    
    """
    
    def __init__(self, num_semitones):
        """
        Pitch numbers for the blow and draw of this hole. Compute note possibilities
        """

        # A hole is defined by its basic blow note and draw note
        # Since we're working relatively here, define the basic blow note is 0 semitones, and
        # the basic draw note is how many semi-tones away
        self._basic_blow_note = 0 
        self._basic_draw_note = num_semitones        
        
        # Implement basic blow physics
        # Whether the blow is lower or higher than the draw
        # For example, holes 1-7 of a Richter-tuned diatonic harmonica are forward, 8-10 are backward
        # We limit ourselves to standard overblow technique and exclude theoretical possibilities
        # like quarter-tones and severly bent-up overblows. We'll add bends to this list later in 
        # the initialization process.
        self._all_practical_pitches = [self._basic_blow_note] + [self._basic_draw_note]
        
        if self._basic_draw_note > 0:
            self._hole_direction = 'forward'
            self._draw_bends = [pitch for pitch in range(self._basic_blow_note + 1, self._basic_draw_note)]
            self._draw_gliss_range = [self._basic_blow_note + 1, self._basic_draw_note]
            self._overdraw_bend = []
            self._blow_bends = []
            self._blow_gliss_range = []
            self._overblow_bend = num_semitones + 1
            self._all_practical_pitches += self._draw_bends + [self._overblow_bend]
            
        # I'm not actually sure that overbends are null here
        elif self._basic_draw_note == 0:
            self._hole_direction = 'neutral'
            self._draw_bends = []
            self._draw_gliss_range = []
            self._overdraw_bend = []
            self._blow_bends = []
            self._blow_gliss_range = []
            self._overblow_bend = []
            
        elif self._basic_draw_note < 0:
            self._hole_direction = 'backward'
            self._draw_bends = []
            self._draw_gliss_range = []
            self._overdraw_bend = num_semitones + 1
            self._blow_bends = [pitch for pitch in range(self._basic_draw_note + 1, self._basic_blow_note)]
            self._blow_gliss_range = [self._basic_draw_note + 1, self._basic_blow_note]
            self._overblow_bend = []
            self._all_practical_pitches += self._blow_bends + [self._overdraw_bend]

        print(self._all_practical_pitches)
         
        self._all_practical_pitches.sort()                                        
      
        # Placeholder for theoretical pitches, which could include severly bent-up overbends and glisses
        # Maybe we'll do quartertones, and near-quartertones later
        self._all_theoretical_pitches = []
        
        # All possible pitches, at least according to our model above
        self._all_possible_pitches = self._all_practical_pitches + self._all_theoretical_pitches
        
        



class harmonica:
    """
    Oooooh, this has to be in terms of intervals
    How hard is a given tune on a given harmonica?
    For a given pitch, how easily can it be played (formation, intonation, low overblows are hard, etc.)
    For any given interval, how easy is it? (breath direction, changing between blowing forms)
    The 5 of the 1 is the 3 of the 2 thing
    What's the pitch range, number of holes and ratio of the two?
    How chromaticly/diatonically oriented is this for arbitrary music? (compare test 12-tone music to diatonic music)
    How "bluesy" a harmonica is in a given key?
    Is there some quantitative reason that we can derive why Howard Levy loves Richter tuning?
    A hypermegametalydian harmonica?
    
    The tuning input variable is a dictionary with 
    hole number: [blow note relative interval, hole structure]
    
    We assume that the holes are numbered from 1 on the left to N on the right (physically)
    In most tunings, the hole 1 blow note corresponds to the "key" of the harmonica
    Here, for more generality, we merely assume that exactly one of the holes (not necessarily hole 1) 
    has an interval of 'p1+', and that's the "key" of the harmonica (and root_pitch gets assigned there)
    
    """
    
    def __init__(self, tuning, root_pitch):
        
        # Check assumptions: holes numbered from -M to N, etc.
        
        # Initialize tuning        
        self._tuning = tuning
        
        # Loop through keys and find main hole
        # Loop up and back from that hole assigning absolute pitches
        # Need to implement pitch class first
        
        
        # Add additional absolute pitch attributes to 



richter_tuning = {
1: ['p1+', harmonica_hole(2)],
2: ['p3+', harmonica_hole(3)],
3: ['d3+', harmonica_hole(4)],
4: ['p4+', harmonica_hole(2)],
5: ['p3+', harmonica_hole(2)],
6: ['d3+', harmonica_hole(2)],
7: ['p4+', harmonica_hole(-1)],
8: ['p3+', harmonica_hole(-2)],
9: ['d3+', harmonica_hole(-2)],
10: ['p4+', harmonica_hole(-3)]}

list(richter_tuning.keys())

richter_tuned_harmonica = harmonica(richter_tuning, "c,")


# So like (G B) (C E) (E G) (G C) to get a perfect fourth below your single melody octave
shephards_flute_tuning = {
1: ['p4-', harmonica_hole(4)],
2: ['p1+', harmonica_hole(4)],
3: ['p3+', harmonica_hole(3)],
4: ['d3+', harmonica_hole(4)]}































