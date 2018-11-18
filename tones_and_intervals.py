






"""
I like complex, highly structured melodies and harmonies. I also like everything to be
spelled enharmonically correctly. 

So I made this package to implement a very general 
and flexible jazz scale theory that can be used to programmatically generate many different
pan-diatonic musical structures derived from things like
-Basic scales
-Jacob Collier hyper mega meta ultra lydian scale
-Arbitrary chord extensions like #15 or b39
-Dave Liebman's whole chromatic theory, including synthetic scales
-Mick Goodrick's system of voice-leading
-Slonimsky's scales
-Tonino Miano's whole system
-Hindustani and Carnatic ragas (what of them fits in our Western system)

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
-Modes of limited transposition on a grander scale?
-Diatonic voice leading like Mick Goodrick
-Generate diatonic exercise books
-Do all of this within the compass of a particular voice or instrument

We incorporate rhythmic patterns such as
-Different time signatures
-Eric Demaine's rhythmic necklaces
-Arbitrary accent patterns
-Many different polyrhythms

We'll be able to do cute tricks like
-Crazy computations in triple flats
-Howard Levy "the 2 of the 5 is the 3 of the 2"
-Something dan tepfer
    -visualize complicated chromatic structures while they play?
    -translate pictoral or other input into structured lines, relative to some scale? (like nok)
-Take numeric input (like from transcendental numbers) and hear it

We strive for high generality here, but note that enharmonic naming conventions are relative
to the ionian scale (white keys on the piano), so we can't treat all 12 pitches equally
for the purposes of notation (though musically we can)

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
-a rendered scale is just a starting note + a scale, then extend that over the whole piano in both direciotns 
"""



import re
import math

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











def semitones_to_diasteps(num_semitones):
    """
    Take an integer number of semitones and return a list of all possible diatonic intervals
    corresponding to that number. If num_semitones < 0, return a descending interval.
    
    This function is not actually a method that operates on intervals, though it returns intervals,
    so we define it here in open code, not in the interval class
    
    For multi-valued outputs of this function, we leave it to downstream processes to choose the correct version.
    
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
    octave_offset = raw_num_semitones // 12
    
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
        Interval subraction is just the opposite of interval addition.
        
        Again, we return a list of all possible results, to be disambiguated later.
        """
        return self + other.reverse_direction()
    
    
    def invert(self, wrt=interval('p8+')):
        """             
        Invert an interval with respect to (wrt) an octave up, or some other
        (positive or negative) distance that we specify.
        """
        return __sub__(wrt, self)
    



class scale:
    """
    A scale is an ordered list of (ascending or descending) intervals, a continuation offset, and a degree list
    
    The list of intervals starts out with the root, 'p1+' for rooted scales. Subsequent intervals tell how far to
    go to get to the next note.   
    
    But scales can be rootless and not have a 'p1+' in their interval list. For example, we might imagine playing 
    [d, e, g, a, b] with respect to a C root. Here, the first interval gives the distance from the implicit root.
    
    A scale either begins with the root 'p1+' in the degree list or is rootless--the 'p1+' can't appear anywhere else
    
    Later we will "render" scales with a given pitch as the root as a list of the corresponding absolute pitches built off of that root.
    
    Intervals in a scale can be ascending or descending, so a scale need not be monotonically increasing.
    
    After the list of intervals there's something called a continuation offset, 
    which tells us how to add scales together. For example, the interval
    c d e f g a b. If we want to continue to the next octave... continuation offset
    But wholestepp...   which allows us to capture scales that are periodic with period greater than 7
    
    There's also the degree list which tells us what diatonic function each pitch in the scale has with respect to the root
    
    So we could have ionian_scale = scale(['p1+', 'p2+', 'p2+', 'd2+', 'p2+', 'p2+', 'p2+'], 'd2+')
    It doesn't matter if we say 'd2+' or 'a1+'... when we go to render the scale, the interval arithmetic will return a list 
    of all possible notes, and then we will use the degree list cross referenced to [a, b, c, d, e, f, g] to determine
    the appropriate enharmonic spelling of the pitch. So in a Bb scale, Eb is the 4 because we have b, c, d, e... it's 
    not D#, because D# is a 3 in the key of Bb
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
        interval strings and continuation offset and degree list right by one place
        
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
        In other words, the length is how many notes in the scale, not the cumulative interval the scale traverses.
        The interavl string includes the continuation offset, so we add one at the end
        Recall that for our purposes, a scale can be any length, including > 7 pitches
        """
        return len(self._str_list_of_interval_strings) + 1
    
    
    def scale_span(self):
        """
        Gives the cumulative interval the scale traverses.
        We get it by adding all of the intervals together.
        """
        
        
    def widest_interval(self):
        """
        Return the widest interval in the scale.
        ??? We obviously need to do this on the absolute representation.
        If scales were forced to be monotonically increasing, we could just
        use the last interval, but here the widest interval need not be the last
        """
        
        scale_length = 0
        for interval in self._scale_steps:
            if len(interval) > scale_length:
                scale_length= len(interval)
                
        return scale_length
    
    
    def __add__(self, other):
        """
        Adding two scales means sticking the intervals of other after the intervals of self via the continuation offset
        We also need to combine the two degree lists. The intervals we get when we do this will govern the enharmonic 
        spellings of the notes when we render the new scale relative to a pitch.
        
        We basically want to be able to combine existing scales together to get new scales.
                
        Take the lydian tetrachord as an example:
        
        lyd_tc = scale(['p1+', 'p2+', 'p2+', 'd2+'], 'p2+', [1, 2, 3, 4])
        ... so like c d e f
        
        lyd_tc + lyd_tc should be scale(['p1+', 'p2+', 'p2+', 'd2+', 'p2+', 'p2+', 'p2+', 'd2+'], 'p2+', [1, 2, 3, 4, 5, 6, 7, 8])
        ... so like c d e f g a b c
        
        Compare this to ionian_scale = scale(['p1+', 'p2+', 'p2+', 'd2+', 'p2+', 'p2+', 'p2+'], 'd2+', [1, 2, 3, 4, 5, 6, 7]),
        which is not the same thing. We can iterate lydian tetrachords to get Jacob Collier's super ultra hyper mega meta lydian
        scale with a huge period, but we iterate the ionian scale and it has a period of seven--so unlike in casual conversation, 
        here we have
        
        lyd_tc + lyd_tc != ionian_scale
        
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
        
    
    def invert(self):
        """
        This is not "take a scale c, d, e, f, g and turn it into f, g, a, bb, c", for example--
        these two scales have the same abstract representation.
        
        Instead, it's respelling the intervals so that the most positive interval is at the right. For example,
        for a lydian scale, ['p1+', 'p2+', 'p2+', 'd2+'] becomes ['p2-', 'p2-', 'd2-'], without the 'p1'
        ... or something to help us extend scales all along the piano
        
                
        """
        return
    
    
    def absolute_scale_repr(scale):
        """
        Take relative scale representation:
            
            ionian_scale = scale(['p1+', 'p2+', 'p2+', 'd2+', 'p2+', 'p2+', 'p2+'], 'd2+', diatonic_sc_degs)
            
        and return the interval list in absolute representation, where each interval is with respect to the root,
        and not the neighbor to the left
            
            ['p1+', 'p2+', 'p3+', 'p4+', 'p5+', 'p6+', 'p7+']
        
        """
    
        # Start out with a unison
        current_interval = interval('p1+')
        
        # Initialize an absolute scale to return
        absolute_scale_to_return = [current_interval]
        
        # Chop off the 1 from the degree list
        chopped_degree_list = scale._degree_list[1:]
        
        # Loop over degree_list, do the interval addition, and pick the appropriate name for the new interval
        for step in range(len(scale._scale_steps)):
    
            list_of_addition_results = absolute_scale_to_return[-1] + scale._scale_steps[step]
            
            # Iterate over the possible results of the addition
            # Pick the interval from the list that has the next degree in the degree list
            found_indicator = 0
            for element in list_of_addition_results:
                
                if element._interval_number == chopped_degree_list[step]:
                    found_indicator = 1
                    element_to_append = element
                
            # If we found a match, pick it. If not, what we're trying to do is impossible, so raise an error.
            if found_indicator == 1:
                absolute_scale_to_return += [element_to_append]
            elif found_indicator == 0:
                    # If we haven't found a match, it's an error
                    print(absolute_scale_to_return)
                    raise ValueError('No interval exists that represents the next scale degree.')
    
        return absolute_scale_to_return 

    
    def compute_interest(self):
        """
        A measure of how interesting the scale is--what proportion of the twelve tones
        does it include in its entirety?
        """
        
        # WLOG put it into C representation
        # Compute number of pitches out of 12
               
"""
Methods to add:
    -modes
    
For lines
    -tensor product--add diatonic or chromatic enclosures, expand all notes (no--this is for lines only)
    -new data structure: expanded scale where we scale it all around the piano

Mode notes

[1, 2, 3, 4, 5, 6, 7]
then
[2, 3, 4, 5, 6, 7, 1]
then
[1, 2, 3, 4, 5, 6, 7]


pentatonic
[1, 2, 3, 5, 6]
permute list once
[2, 3, 5, 6, 1]
then rachet down by first degree minus one--take away (2-1) = 1
[1, 2, 4, 5, 7]


again
[3, 5, 6, 1, 2]
then take away 3 - 1. 
[1, 3, 4, 6, 7]
In general, take away ((first degree of permuted list) - (first degree of original list))

so
(1)[2, 3, 5, 6, 7] (implicit root is the 1--we permute this just like we permute scales with the 1--move the roles right by one)
(so for C implicit root, d, e, g, a, b, one permutation gives us D implicit root, e, g, a, b, d

permute once, goes to (if a lower number goes back around, add 7 to it)
(2)[3, 5, 6, 7, 8]
take away (2 - 1) = 1
(1)[2, 4, 5, 6, 7]

permute list twice goes to
(3)[5, 6, 7, 8, 9] take away (3 - 1) = 2
(1)[3, 4, 5, 6, 7]


what if it's nonmonotonic, like [1, 2, 5, 3, 4, 6] = c, d, g, e, f, a [...C, D, ...]
permute once
[2, 5, 3, 4, 6, 1] -> [d, g, e, f, a, c] -> 
[1, 4, 2, 3, 5, 7]

what if it's hyperdiatonic nonconsecutive like 
[1, 2, 3, 4, #5, b7, (then in db)] -> c, d, e, f, g#, bb, | , db, eb, f, gb, a, cb

A hyperscale is just a list of scales? convert to a single scale?
scale(['p2+', 'p2+', 'd2+', 'p2+', 'p2+', 'p2+'], 'd2+') + scale(['p2+', 'p2+', 'd2+', 'p2+', 'p2+', 'p2+'], 'd2+')
different representations that tell the root for each unit?
for now, we'll say that you can't take a mode of a hyperscale in piece-wise format--you have to first convert it to a full set of intervals


 
to get the a of the b or the [equivalent] c of the d, just take a harmonica in the 
key of the e and overblow the f

"""





























##### Test Area

# Church Modes
diatonic_sc_degs = [1, 2, 3, 4, 5, 6, 7]
ionian_scale = scale(['p1+', 'p2+', 'p2+', 'd2+', 'p2+', 'p2+', 'p2+'], 'd2+', diatonic_sc_degs)
dorian_scale = ionian_scale.get_mode(2)
phrygian_scale = ionian_scale.get_mode(3)
lydian_scale = ionian_scale.get_mode(4)
mixolydian_scale = ionian_scale.get_mode(5)
aeolian_scale = ionian_scale.get_mode(6)
locrian_scale = ionian_scale.get_mode(7)


# Tetrachords
tetrachord_sc_degs = [1, 2, 3, 4]
lyd_tc = scale(['p1+', 'p2+', 'p2+', 'd2+'], 'p2+', tetrachord_sc_degs)

# Pentatonic
maj_pentatonic_sc_degs = [1, 2, 3, 5, 6]
major_pentatonic_scale = scale(['p2+', 'p2+', 'd3+', 'p2+'], 'd3+', [1, 2, 3, 5, 6])

# Whole Tone
whole_tone_sc_degs = [1, 2, 3, 4, 5, 6]
whole_tone_sc = scale(['p1+', 'p2+', 'p2+', 'p2+', 'p2+', 'p2+'], 'p2+', whole_tone_sc_degs)

# Melodic Minor
melodic_minor_scale = scale(['p2+', 'd2+', 'p2+', 'p2+', 'p2+', 'p2+'], 'd2+', [1, 2, 3, 4, 5, 6, 7])

# Chromatic (test for mode equality?)
# Diminished








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
    
    # get the simplest representations for a given pitch
    # represent it as locations in the base_lilypond_octaves list
    # simplest natural representation is always 1, so we don't need that
    if equiv_pitch_oct_bel_mc = 24:
        simplest_flat_rep_oct_bel_mc = 4
        simplest_sharp_rep_oct_bel_mc = 1
    elif equiv_pitch_oct_bel_mc = 25:
        simplest_flat_rep_oct_bel_mc = 3
        simplest_sharp_rep_oct_bel_mc = 1
    elif equiv_pitch_oct_bel_mc = 26:
        simplest_flat_rep_oct_bel_mc = 4
        simplest_sharp_rep_oct_bel_mc = 2
    elif equiv_pitch_oct_bel_mc = 27:
        simplest_flat_rep_oct_bel_mc = 3
        simplest_sharp_rep_oct_bel_mc = 1
    elif equiv_pitch_oct_bel_mc = 28:
        simplest_flat_rep_oct_bel_mc = 3
        simplest_sharp_rep_oct_bel_mc = 2
    elif equiv_pitch_oct_bel_mc = 29:
        simplest_flat_rep_oct_bel_mc = 4
        simplest_sharp_rep_oct_bel_mc = 2
    elif equiv_pitch_oct_bel_mc = 30:
        simplest_flat_rep_oct_bel_mc = 3
        simplest_sharp_rep_oct_bel_mc = 1
    elif equiv_pitch_oct_bel_mc = 31:
        simplest_flat_rep_oct_bel_mc = 4
        simplest_sharp_rep_oct_bel_mc = 2
    elif equiv_pitch_oct_bel_mc = 32:
        simplest_flat_rep_oct_bel_mc = 3
        simplest_sharp_rep_oct_bel_mc = 1
    elif equiv_pitch_oct_bel_mc = 33:
        simplest_flat_rep_oct_bel_mc = 4
        simplest_sharp_rep_oct_bel_mc = 2
    elif equiv_pitch_oct_bel_mc = 34:
        simplest_flat_rep_oct_bel_mc = 3
        simplest_sharp_rep_oct_bel_mc = 1
    elif equiv_pitch_oct_bel_mc = 35:
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
    
    # put it all together to get a list of possible lilypond spellings
    lilypond_spellings = []    
    for item in base_lilypond_octaves[equiv_pitch_oct_bel_mc]:
        lilypond_spellings.append(item + lilypond_octave_modifier)
    
    # dereference "," (octave lower) and "'" (octave higher) when they're together
    while lilypond_spellings.find("',") > 0:
        location = lilypond_spellings.find("',") 
        lilypond_spellingst = lilypond_spellings[0:location] + lilypond_spellings[location + 2:]
    
    while lilypond_spellings.find(",'") > 0:
        location = lilypond_spellings.find(",'") 
        lilypond_spellings = lilypond_spellings[0:location] + lilypond_spellings[location + 2:]

    return lilypond_spellings
    

get_attrs(50)











