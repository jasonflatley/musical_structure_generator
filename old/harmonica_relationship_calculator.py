



"""
Intro

Assumptions:
-Ignore enharmonic technicalities for now and just use common pitch names
-View the circle of fifths mod 12 (ie, don't keep track of where we are)
"""




# Dictionary that maps English pitch names to the distance in half steps from the nearest lower C
# Used to compute half step distances between arbitrary English pitch names, such as would 
# appear in scales.
# It also serves as a unique way to identify each pitch (even though pitches can have two names)
note_distance = {'C': 0,
                 'C#': 1,
                 'Db': 1,
                 'D': 2,
                 'D#': 3,
                 'Eb': 3,
                 'E': 4,
                 'F': 5,
                 'F#': 6,
                 'Gb': 6,
                 'G': 7,
                 'G#': 8,
                 'Ab': 8,
                 'A': 9,
                 'A#': 10,
                 'Bb': 10,
                 'B': 11,
                 'Cb': 11}




# Map our distance numbers from above to pitch names
# It's a 2-to-1 mapping depending on whether you're going up or down
# We work mod 12 to deal with huge intervals
find_pitch_up = {0: 'C',
                 1: 'C#',
                 2: 'D',
                 3: 'D#',
                 4: 'E',
                 5: 'F',
                 6: 'F#',
                 7: 'G',
                 8: 'G#',
                 9: 'A',
                 10: 'A#',
                 11: 'B'}

find_pitch_down =   {0: 'C',
                     1: 'Db',
                     2: 'D',
                     3: 'Eb',
                     4: 'E',
                     5: 'F',
                     6: 'Gb',
                     7: 'G',
                     8: 'Ab',
                     9: 'A',
                     10: 'Bb',
                     11: 'B'}




# Define a scale data structure as an ordered list of pitch names, where each subsequent pitch name is understood
# to be higher than the previous pitch name, even if the distance is big
test_scale = ['C', 'D', 'E', 'F', 'G#', 'A', 'B', 'C#', 'D#', 'G', 'A', 'B', 'C', 'D', 'E', 'F#']




def move_pitch_by_interval(pitch, interval):
    
    """
    Takes 'C' and 4 (for major third up) and returns 'E'
    Internally, we do C -> 0 + 4 = 4 -> E
    Distinguish between up and down by sign of interval argument
    Work mod 12 for large intervals
    """
    
    if interval >= 0:
        return find_pitch_up[(note_distance[pitch] + interval)%12]
    elif interval < 0:
        return find_pitch_down[(note_distance[pitch] + interval)%12]
    
# Test
move_pitch_by_interval('C', 4)
move_pitch_by_interval('C', 6)
move_pitch_by_interval('C', 18)
move_pitch_by_interval('Bb', 6)
move_pitch_by_interval('Bb', -6)
move_pitch_by_interval('Bb', -1)
move_pitch_by_interval('Bb', -13)




def check_scale_for_all_pitches(scale):
    
    """
    Returns True if the given scale contains each of the 12 pitches (regardless of how they're named), otherwise False
    Since each pitch can have multiple names, create a checklist of tuples (pitch, False) and 
    set each one to True when we find that pitch
    """
    
    # Initialize checklist of 12 False values, each one corresponding to
    # a note in note_distance
    pitch_checklist = [False]*12
    
    # Fill out the checklist
    # Once we've found all of the pitches, we're done
    for note in scale:
        pitch_checklist[note_distance[note]] = True
        if sum(pitch_checklist) == 12:
            return True
        
    # At this point, the entries of pitch_checklist that are still False are the missing pitches
    return False

# Test
test_scale_1 = ['C', 'D', 'E', 'F', 'G#', 'A', 'B', 'C#', 'D#', 'G', 'A', 'B', 'C', 'D', 'E', 'F#']
test_scale_2 = ['C', 'D', 'E', 'F', 'G#', 'A', 'B', 'C#', 'D#', 'G', 'A', 'Bb', 'C', 'D', 'E', 'F#']
test_scale_3 = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B']
test_scale_4 = ['C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B']
check_scale_for_all_pitches(['C', 'D', 'E', 'F', 'G'])
check_scale_for_all_pitches(test_scale_1)
check_scale_for_all_pitches(test_scale_2)
check_scale_for_all_pitches(test_scale_3)
check_scale_for_all_pitches(test_scale_4)





def find_missing_scale_pitches(scale):
    
    """
    A variant of check_scale_for_all_pitches where we report which pitches are missing
    """
    
    # Initialize checklist of 12 False values, each one corresponding to
    # a note in note_distance
    pitch_checklist = [False]*12
    
    # Fill out the checklist
    # Once we've found all of the pitches, we're done
    for note in scale:
        pitch_checklist[note_distance[note]] = True
        if sum(pitch_checklist) == 12:
            return "All 12 pitches are represented in this scale."
        
    # At this point, the entries of pitch_checklist that are still False are the missing pitches
    missing_pitches = []
    for pitch in range(0, 12):
        if pitch_checklist[pitch] == False:
            up_pitch = find_pitch_up[pitch]
            down_pitch = find_pitch_down[pitch]
            pitch_name_to_append = up_pitch if up_pitch == down_pitch else up_pitch + '/' + down_pitch
            missing_pitches.append(pitch_name_to_append)
            
    string_to_return = "This scale is missing the following pitches:"
    
    for entry in missing_pitches:
        string_to_return += " " + entry
    
    string_to_return += '.'
    
    return string_to_return
 
# Test
find_missing_scale_pitches(['C', 'D', 'E', 'F', 'G'])
find_missing_scale_pitches(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B'])




def construct_single_tetrachord_scale(starting_pitch, tetrachord):
    
    """
    The idea here is to experiment with extended scales by stacking tetrachords.
    We stack until all 12 pitches are represented, or we iterate a certain number of times
    Would need to put some constraints on numbers in a tetrachord before we can give a
    mathematical stopping condition.
    """
    
    tetrachord_scale = []
    
    # Stack the tetrachords until we reach a stopping condition
    for iteration in range(0, 7):
        if iteration == 0:
            local_starting_pitch = starting_pitch
        else:
            local_starting_pitch = move_pitch_by_interval(tetrachord_scale[-1], tetrachord[3])
            
        next_pitch_2 = move_pitch_by_interval(local_starting_pitch, tetrachord[0])
        next_pitch_3 = move_pitch_by_interval(next_pitch_2, tetrachord[1])
        next_pitch_4 = move_pitch_by_interval(next_pitch_3, tetrachord[2])
        tetrachord_scale.extend([local_starting_pitch, next_pitch_2, next_pitch_3, next_pitch_4])
            
        # If we now have all pitches represented, we're done wit the for loop
        if check_scale_for_all_pitches(tetrachord_scale) == True:
            break
    
    # Print output
    print(tetrachord_scale)
    print('\n')
    print(find_missing_scale_pitches(tetrachord_scale))


test_tetra = [2, 2, 1, 1]
construct_single_tetrachord_scale('C', test_tetra)



# Tetrachord data structure. First three places give the intervals between the four notes
# Fourth place gives the interval between subsequent tetrachords
major_tetrachord = [2, 2, 1, 2]
construct_single_tetrachord_scale('Ab', major_tetrachord)





"""
Pretty-print the tetrachord pitches with 4 on each line
For scales with a non-prime number of pitches, find "conjugacy classes"
"""



















###########################

def compute_num_half_steps_going_upwards(start_pitch, end_pitch, num_times_to_skip):
    
    """
    Function to compute number of half steps walking upwards
    Start at start_pitch, begin counting half steps upwards
    As you are counting, pass end_pitch without stopping num_times_to_skip times
    Then the next time you get to end_pitch, return the number of half steps
    """
    
    # Get start and end half step values
    # Make sure the end value is greater than the start value
    start_value = note_distance[start_pitch]
    end_value = note_distance[end_pitch] if note_distance[end_pitch] - note_distance[start_pitch] >= 0 else note_distance[end_pitch] + 12
                             
    # Return the difference between the values adjusted by the skip distance
    return end_value - start_value + 12*num_times_to_skip
    
# Tests
compute_num_half_steps_going_upwards('Cb', 'D#', 0)
compute_num_half_steps_going_upwards('C', 'Gb', 0)
compute_num_half_steps_going_upwards('G', 'F#', 0)
compute_num_half_steps_going_upwards('C', 'Gb', 1)
compute_num_half_steps_going_upwards('G', 'F#', 1)




def compute_scale_spacing(scale):
    
    """
    Function that takes in a scale and returns a same-length list with the number
    of half steps that each pitch is from the root
    """
    
    octave_num = 0
    scale_spacing = []
    previous_y_distance = 0
    
    for x, y in zip(asdf[0]*len(asdf), asdf):
        if note_distance[y] < previous_y_distance:
            octave_num += 1
        scale_spacing.append(compute_num_half_steps_going_upwards(x, y, octave_num))
        previous_y_distance = note_distance[y]

    return scale_spacing


# should return [0, 2, 4, 5, 8, 9, 11, 13, 15, 19, 21, 23, 24, 26, 28, 30]
test_scale = ['C', 'D', 'E', 'F', 'G#', 'A', 'B', 'C#', 'D#', 'G', 'A', 'B', 'C', 'D', 'E', 'F#']
compute_scale_spacing(test_scale)









###############################
"""


# For a scale starting on pitch X, 'A': B means to get to scale degree 'A', you must move up B half steps from pitch X
lydian_degrees = {}
'1': 0,
'2': 2,
'3': 4,
'4': 5,
'5': 7,
'6': 9,
'7': 11,
'8': 12,
'9': 14,
'10': 
'#11': 
'12': 
'13': 
'14': 
'15': 
'16': 
'17': 
'#18': 
'#19': 
'20': 
'21': 
'#22': 
'#23': 
'24': 
'#25: 
'#26': 
'#27': 
'28': 
    
    
C +2
D +2
E +1
F +2
G +2
A +2
B +1
C



"""
key center of C
assume everything is lydian for now

lydian degrees
C D E F G A B C D E  F#  G  A  B  C#  D  E  F#  G#  A  B  C#  D#  E  F#  G#  A#  B
1 2 3 4 5 6 7 8 9 10 #11 12 13 14 #15 16 17 #18 #19 20 21 #22 #23 24 #25 #26 #27 28

where do each of the 12 pitches appear?
C: 1, 8
C#: #15, #22
D: 2, 9, 16
D#: #23
E: 3, 10, 17
F: 4
F#: #11, #18, #25
G: 5, 12
G#: #19, #26
A: 6, 13, 20
A#: #27
B: 7, 14, 21, 28

so building by thirds gives C E G B    D F#  A  C#  E G#  B D#  F# A#
which is a                  C     maj7 9 #11 13 #15   #19   #23    #27















Phrase 0
The X1 of the X2 is just the X3 of the X4.
[key of C major] the 3 [A] of the 4 [F] is just the 5 [A] of the 2 [D]

Phrase 1
If you're using a harmonica in the key of the X1, then X2-ing X3 will get you the X4 of the X5.
[tune is in C] If you're using a harmonica in the key of the b3 [Eb], then overblowing the 6 [Bb] will get you the 4 [Bb] of the 4 [F]



"""







"""
Function to construct mega meta ultra hyper lydian scale

Here's an example in C:
pitch (going upwards): C D E F G A B C D E  F#  G  A  B  C#  D  E  F#  G#  A  B  C#  D#  E  F#  G#  A#  B
scale degree:          1 2 3 4 5 6 7 8 9 10 #11 12 13 14 #15 16 17 #18 #19 20 21 #22 #23 24 #25 #26 #27 28
number of half steps:  

formula for this scale:
C D E F is 0 2 4 5 (a tetrachord)
then go up 2
G A B C is 0 2 4 5 
then go up 2
D E F# G is 0 2 4 5
then go up 2
A B C# D is 0 2 4 5
then go up 2
E F# G# A is 0 2 4 5
then go up 2
B C# D# E 
F# G# A# B

We have one for C, G, D, A, E, B, F# to get all of the 12 pitches

vary this to generate other scales?
generate lilypond output directly from python?

"""











