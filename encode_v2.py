# GLOBAL VARIABLES
STRING_LENGTH = 32
NULL_STRING = "\\x00"


def set_base_hash_array():
    """
    Creates a consistent array of all UTF-8 characters between
    chr(0) and chr(127).
    """
    # Create base array for hashing
    base_hash_array = [chr(x) for x in range(128)]
    # Replace the null value with the global variable null
    # This will reduce errors from arising.
    base_hash_array[0] = NULL_STRING
    return base_hash_array


def set_hash_array(hash_array, password):
    """
    Shifts the array based on each ord(p_word) value.
    Then it loops through the whole hash array, noting each
    character's index and value.
    Finally, it swaps the value at the current index with the
    index calculated by ord(p) + index. It will keep swapping an
    individual letter for the whole length of the password before
    moving to the next letter.
    This fully mixes the array in a way that can be consistently
    recalculated over and over.
    """
    # LONG STORY SHORT:
    # -password is 20 long
    # -find the int value for the first character of that password, call it 'char'
    # -rotate has array so the hash[char] is moved to hash[0]
    # -loop through all characters in the hash array (starting with first value)
    # -while on that value, loop through the characters in the password
    # -for each letter of the password, find the character's int value
    # -swap the first letter with the character at the int value
    # -then, find the int value for the next letter of the password
    # -from where the last swap ended, set the other index after that based on the new int value
    # -swap those
    # -THEREFORE, each character gets swapped equal to STRING_LENGTH times
    # -repeat all this
    # - i.e. if len(password) = 17, this will loop 17 * 128 * 17 times, equaling 36,992 total loops

    # Get consistent array for padding
    padding = set_base_hash_array()
    # Pad out short passwords to match the STRING_LENGTH
    if len(password) < 17:
        password_padded = password + padding[len(password) : STRING_LENGTH]
    # Otherwise, if passwords match or exceed STRING_LENGTH continue
    else:
        password_padded = password

    # Step through the password.
    for p_word in password_padded:
        # Shift the array based on the character value
        # for each password character
        hash_array = hash_array[ord(p_word) :] + hash_array[: ord(p_word)]
        # Step through the entire hash array, getting index, and character
        for index, hash_chr in enumerate(hash_array):
            # Then step through the password
            for p in password_padded:
                # Temporarily holds the current value for later moving
                char_holder = hash_chr
                # Find the corresponding index to swap with
                swap_index = index + ord(p)
                # If the value is larger than the total array, subtract
                # the length to keep within bounds.
                if swap_index > len(hash_array) - 1:
                    swap_index -= len(hash_array) - 1

                # Swap the initial hash array location with swap_index value
                hash_array[index] = hash_array[swap_index]
                # Swap the stored char_holder value into the other array postition
                hash_array[swap_index] = char_holder
                # Set the index to the swapped index to help with mixing
                # for the rest of the password loop
                index = swap_index

    return hash_array


def get_binary(string):
    """
    Returns the binary representation of the input letter(s). Keeps consistent length.
    """
    # Use special logic for NULL_STRING to avoid errors
    if string == NULL_STRING:
        return "00000000"
    # Otherwise, gives the binary representation of UTF-8 characters
    return "".join("{:08b}".format(d) for d in bytearray(string, "utf-8"))


def char_compare(char1, char2):
    """
    If adjacent binary characters match, return 0, else 1
    """
    if char1 is char2:
        return "0"  # Matches are '0'
    return "1"  # Differences are '1'


def binary_reduction(binary):
    """
    Steps through binary string using char_compare logic.
    Reduces the length by 1 each time.
    """

    new_binary = ""
    # Compare the bit values (technically strings) that are
    # next to each other
    for x in range(len(binary) - 1):
        new_binary += char_compare(binary[x], binary[x + 1])

    return new_binary


def get_string(binary):
    """
    Takes in a binary string and loops through it 8-bits at a time, converting
    each step back to its character representation.
    """
    new_string = ""

    # Sets range as length of binary string and returns an int
    for x in range((len(binary) // 8)):
        # Grabs 8 characters at a time, converts back to an integer
        n = int(binary[(x * 8) : ((x * 8) + 8)], 2)
        # Special logic to handle null values
        if n == 0:
            new_string += "\\x00"
        # Otherwise, change those bits back to a character
        else:
            new_string += n.to_bytes((n.bit_length() + 7) // 8, "big").decode()

    return new_string


def set_encode(string, password):
    """
    Handles the various function calls to encode
    """
    binary_array = []
    # Combine the password and string arrays into one, then loop it
    for character in password + string:
        binary_array.append(get_binary(character))

    # Create one long binary from those values
    binary = "".join(binary_array)

    # This loops through the binary string, reducing it by
    # one (in length) with each pass
    # Stops once the binary length returns back to the
    # pre-defined STRING_LENGTH
    while len(binary) > (8 * STRING_LENGTH):
        binary = binary_reduction(binary)

    # Turn those binary values back into a string
    return get_string(binary)


def set_string(string, hash):
    """
    Adds 3 NULL_STRINGS to the end, to signal what characters
    can be removed once decoded.
    Cuts it shorter if necessary to preserve STRING_LENGTH.
    """
    # Pad out string with 3 nulls
    string = string + ([NULL_STRING] * 3)

    # If the string now longer than STRING_LENGTH, cut it shorter
    if len(string) > STRING_LENGTH:
        string = string[:STRING_LENGTH]

    # If the string is still too short, pad out with the hash
    if len(string) < STRING_LENGTH:
        string = string + hash[len(string) : STRING_LENGTH]

    return string


def encode(string, password):
    """
    Main function to encode text.

    Requires a string and a password.

    No length requirements.
    """

    print("Calling encode...")

    password = [p for p in password]  # Set the password as an array
    encrypted_string = ""  # To hold encrypted text.
    string_array = []  # To store the string as an array
    skipped_loop = 0  # For handling the \\x00 character

    # Scrambled hash array to use
    hash_array = set_hash_array(set_base_hash_array(), password)
    # Next array to use once the first is empty
    hash_array_next = set_hash_array(hash_array, password)

    for index, step in enumerate(string):
        # If a NULL_STRING is found, skip over the individual characters
        # until the next valid character is reached
        if skipped_loop > 0:
            skipped_loop -= 1
            continue

        if step == chr(92):  # The \ character
            # Check if the \ symbol is part of the NULL_STRING
            if string[index : (index + 4)] == NULL_STRING:
                string_array.append(NULL_STRING)
                # Sets number of loops to skip based on NULL_STRING length
                skipped_loop = len(NULL_STRING) - 1
            else:
                string_array.append(step)  # Only the \ character was found

        else:
            # Otherwise, just append the found character
            string_array.append(step)

        # Once the string array is filled, move into the encoding phase
        if len(string_array) == STRING_LENGTH:

            # Checks if hash_array has enough characters to meet STRING_LENGTH
            if len(hash_array) < STRING_LENGTH:
                # If not, find how many character from the hash_array_next to use
                next_array_len = STRING_LENGTH - len(hash_array)
                # Set password_array
                password_array = hash_array + hash_array_next[:next_array_len]
                # Reset hash_array from the next one
                hash_array = hash_array_next
                # Create a new hash_array_next
                hash_array_next = set_hash_array(hash_array, password)
                # Finally, now that hash_array is the old hash_array_next and a
                # few characters were used, remove those values
                hash_array = hash_array[next_array_len:]
            else:
                # Create the password array
                password_array = hash_array[:STRING_LENGTH]
                # Remove those used values from the hash_array
                hash_array = hash_array[STRING_LENGTH:]

            # Do the encrypt functions
            encrypted_string += set_encode(string_array, password_array)
            # Reset string_array to empty for the next pass
            string_array = []

    # This is for catching the last chunk of string that may not meet STRING_LENGTH requirements
    if string_array != []:
        # Calls function to pad out the last array to match STRING_LENGTH
        # Pass hash_array and hash_array_next as one big array to avoice
        # an array being too small
        string_array = set_string(string_array, (hash_array + hash_array_next))

        if len(hash_array) < STRING_LENGTH:
            # If not, find how many character from the hash_array_next to use
            next_array_len = STRING_LENGTH - len(hash_array)
            # Set password_array
            password_array = hash_array + hash_array_next[:next_array_len]
        else:
            # Create the password array padded with the hash_array
            # password_array = password + hash_array[len(password) : STRING_LENGTH]
            password_array = hash_array[:STRING_LENGTH]

        # Build out the encrypted_string
        encrypted_string += set_encode(string_array, password_array)

    return encrypted_string


def get_string_binary(string):
    """
    Takes in an array of characters and converts the values into their binaries.
    Then it returns the string as one long binary.
    """
    string_binary_array = []

    # Create array of binaries from the string
    for character in string:
        string_binary_array.append(get_binary(character))

    # Combine those binaries into one long binary
    string_binary = "".join(string_binary_array)

    return string_binary


def get_password_binaries_array(password):
    """
    Takes in an array of characters and converts the values into their binaries.
    Then it sets the string as one long binary and appends it to an array.
    Using that newly created binary string, reduce it by one each pass and save
    the results into that array.
    Continue until there is only a single digit.
    """
    password_binary_array = []

    # Create array of binaries from the password
    for character in password:
        password_binary_array.append(get_binary(character))

    # Join it together for parsing
    binary = "".join(password_binary_array)

    # Start the array off with the actual padded password binary
    rebuild_binaries = [binary]

    # This loops through the binary string, reducing it by
    # one (in length) with each pass appending string to array
    # Stops once the binary length is 1 (one)
    while len(binary) > 1:
        # Use the function logic to reduce the binary by one based on simple logic
        binary = binary_reduction(binary)
        # Add that new binary to this array for later usage
        rebuild_binaries.append(binary)

    return rebuild_binaries


def rebuild_binary(string_binary, password_binary):
    """
    Takes an binary string (still encoded), and reverses the binary reduction
    by one step up.

    If the string_binary = '0101' and the password_binary = '11':
    It would initially look like:

    1 1         <- password_binary
     0 1 0 1    <- string_binary

    This will therefore produce:

    1 1 0 0 1   <- new string_binary
     0 1 0 1    <- old string_binary

    Because password_binary already has two characters, we can start this rebuild
    by inspecting the second elements of both lists and calculating their next
    values from there.
    """
    # This will be the new string we build out with binary values
    # Because the password_binary already contains valid numbers,
    # set new_string_binary to those valid numbers
    new_string_binary = password_binary
    # Set variable to the last number to start the rebuild with
    last_char = password_binary[-1]

    # Use a range starting at the end of the valid password_binary
    # and ends at the calculated total length
    ## (which is STRING_LENGTH * bit size added to the current password_binary length)
    for x in range(
        (len(password_binary) - 1), (len(password_binary) + (STRING_LENGTH * 8) - 1)
    ):
        # Calculates whether it should return '0' or '1'
        # Store that value for next round iteration
        last_char = char_compare(last_char, string_binary[x])
        # Add that new value to the rebuild string
        new_string_binary += last_char

    return new_string_binary


def set_decrypt(string, password, decrypted_string):
    """
    Using the string and password, begins rebuilding the decrypted string.

    The big step here is the for loop section. This starts with the encrypted
    string and steps it back up in length until it consists of the password
    and original string.

    If the encrypted string = "1100" and the password = "0100":

    Using the password array which would look like:
    0 1 0 0
     1 1 0
      0 1
       1

    And this is all set up like:
    0 1 0 0         <-password
     1 1 0
      0 1
       1            <-reduced password
        1 1 0 0     <-encrypted_string

    It steps backwards to reverse out of the reduction:
    0 1 0 0         <-password
     1 1 0
      0 1
       1 0 1 1 1    <-first step back out
        1 1 0 0     <-encrypted_string

    Until it is fully reversed:
    0 1 0 0 1 0 0 0 <-password + original string binary
     1 1 0 1 1 0 0
      0 1 1 0 1 0
       1 0 1 1 1    <-reduced password
        1 1 0 0     <-encrypted_string

    """
    # Get the binary of the string
    string_binary = get_string_binary(string)

    # Get the binary of the password
    password_binary_tree = get_password_binaries_array(password)

    # This will loop through the range of the found password_binary_tree
    for step in range(len(password_binary_tree)):
        # Sends string_binary to function as well as password_binary_tree sent last to first
        string_binary = rebuild_binary(string_binary, password_binary_tree[(-step) - 1])

    # Convert the found binaries to strings
    new_string = get_string(string_binary)

    # Join the password back together
    password = "".join(password)
    # And then cut it out of the decrypted_string, leaving only the string
    decrypted_string = new_string[len(password) :]

    return decrypted_string


def decode(string, password):
    print("Calling decode...")

    password = [p for p in password]  # Set the password as an array
    decrypted_string = ""  # To hold encrypted text.
    string_array = []  # To store the string as an array
    skipped_loop = 0  # For handling the \\x00 character

    # Scrambled hash array to use
    hash_array = set_hash_array(set_base_hash_array(), password)
    # Next array to use once the first is empty
    hash_array_next = set_hash_array(hash_array, password)

    for index, step in enumerate(string):
        # If a NULL_STRING is found, skip over the individual characters
        # until the next valid character is reached
        if skipped_loop > 0:
            skipped_loop -= 1
            continue

        if step == chr(92):  # The \ character
            # Check if string == NULL_STRING
            if string[index : (index + 4)] == NULL_STRING:
                string_array.append(NULL_STRING)
                # Sets number of loops to skip based on NULL_STRING length
                skipped_loop = len(NULL_STRING) - 1
            else:
                string_array.append(step)  # Only the \ character was found

        else:
            string_array.append(step)

        # Once the string array is filled, move into the encoding phase
        if len(string_array) == STRING_LENGTH:
            # Checks if hash_array has enough characters to meet STRING_LENGTH
            if len(hash_array) < STRING_LENGTH:
                # If not, find how many character from the hash_array_next to use
                next_array_len = STRING_LENGTH - len(hash_array)
                # Set password_array
                # password_array = (
                #     password + hash_array + hash_array_next[:next_array_len]
                # )
                password_array = hash_array + hash_array_next[:next_array_len]
                # Reset hash_array from the next one
                hash_array = hash_array_next
                # Create a new hash_array_next
                hash_array_next = set_hash_array(hash_array, password)
                # Finally, now that hash_array is the old hash_array_next and a
                # few characters were used, remove those values
                hash_array = hash_array[next_array_len:]
            else:
                # Create the password array padded with the hash_array
                # password_array = password + hash_array[len(password) : STRING_LENGTH]
                password_array = hash_array[:STRING_LENGTH]
                # Remove those used values from the hash_array
                hash_array = hash_array[STRING_LENGTH:]

            # Build out decrptyed_string
            decrypted_string += set_decrypt(
                string_array, password_array, decrypted_string
            )
            # Reset string_array to empty
            string_array = []

    # Max buffer needed to account for NULL_STRING LENGTH
    null_string_buffer = (len(NULL_STRING) - 1) * 3

    # If the decrypted_string is long enough, max out buffer size
    # This will get nearly ALL use cases
    if len(decrypted_string) > STRING_LENGTH + null_string_buffer:
        buffer = null_string_buffer
    # Otherwise, calculate how large of a buffer can be used
    elif len(decrypted_string) > STRING_LENGTH:
        buffer = len(decrypted_string) - STRING_LENGTH
    # Fail-safe, set buffer to zero if decrypted_string equals STRING_LENGTH
    else:
        buffer = 0

    # Slice off the final portion to check for ending NULL_STRINGs in
    final_string = decrypted_string[-STRING_LENGTH - buffer :]

    # Check if 3 NULL_STRINGS in a row are present
    if f"{NULL_STRING + NULL_STRING + NULL_STRING}" in final_string:
        # If found, find the index of those NULL_STRINGS in the main decrypted_string
        # Index against the end of decrypted_string
        f = decrypted_string.rindex(
            f"{NULL_STRING + NULL_STRING + NULL_STRING}",
            len(decrypted_string) - STRING_LENGTH - buffer,
            len(decrypted_string),
        )
        # Cut off those NULL_STRINGs and everything after
        decrypted_string = decrypted_string[:f]
    # Check if last 2 spots are NULL STRINGS
    elif f"{NULL_STRING + NULL_STRING}" in final_string[-(len(NULL_STRING) * 2) :]:
        # Cut off the last two nulls
        decrypted_string = decrypted_string[
            : len(decrypted_string) - (len(NULL_STRING) * 2)
        ]
    # Check if last spot is a NULL STRING
    elif f"{NULL_STRING}" in final_string[-(len(NULL_STRING)) :]:
        decrypted_string = decrypted_string[
            : len(decrypted_string) - (len(NULL_STRING))
        ]

    return decrypted_string
