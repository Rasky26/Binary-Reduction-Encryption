# Binary-Reduction-Encryption

This encryption function should ONLY be used for entertainment and education. If you need to encrypt information, please use standard heavily utilized methods that have been thoroughly vetted by professionals and institutions.

Main functions:
-> encode(string, password)
-> decode(string, password)

 Here are the main points to this encryption method:

1.) The core process revolves around using the binary values for characters to encrypt. I built this to only use UTF-8 (and only kept it to the first 128 characters for testing), but it could be expanded to encompass more formats.
1.1) Global variables:
1.1.1) STRING_LENGTH -> the number of characters to grab to encrypt with each loop
1.1.2) NULL_STRING -> I was having issues dealing with the null character, so I use this value to keep issues/errors from arising

2.) Call the encode() function. This function takes a string and a password
2.1) If the password length is less than STRING_LENGTH, pad out the password with UTF-8 characters to reach STRING_LENGTH.
2.1.1) Passwords longer than STRING_LENGTH are not modified

3.) Creating the hash table
3.1) Create an array of the first 128 UTF-8 characters using [chr(x) for x in range(128)]
3.2) Shuffle the hash table using the supplied password
3.2.1) For each character in the password, shift the hash table ahead by the ordinal value for the current password character
3.2.2) After each shift, loop through the entire hash array noting the current index and the current character
3.2.3) Begin another loop stepping through the characters of the password
3.2.4) Here is how that loop functions:
3.2.4.1) Take the current index and calculate and store a swap index by adding ordinal of the character from 3.2.3 and adding it to the index
3.2.4.1.1) If the swap index is greater than the length of the array, subtract off the length of the hash array to reduce it back into a valid range
3.2.4.2) Swap those characters
3.2.4.3) Set the index = swap index, then repeat step 3.2.4.1 for the entirety of the password
3.2.4.4) Once through the password, move back to 3.2.2

      The process works thusly (very minimal example, using numbers, not characters):
      
          example_array = [0, 1, 2, 3, 4, 5, 6, 7]
          password = [2, 7] (shown as array for clarity)
          
          3.2.1      -> [2, 3, 4, 5, 6, 7, 0, 1] -> shifted
          3.2.2      -> index = 0, swap_index = 0 + 2 = 2
          3.2.4.3    -> [4, 3, 2, 5, 6, 7, 0, 1] -> swapped
            <loop steps to next character in password>
          3.2.2      -> index = 2, swap_index = 2 + 7 = 9 -> revalued to: 9 - 8 = 1 (8 is length of the array)
          3.2.4.3    -> [4, 2, 3, 5, 6, 7, 0, 1] -> swapped
            <now repeat the process at 3.2.1 starting with second index in the above array>
            <once through the whole array, go to 3.2.1, shift the array by the next value of the password, and repeat this process>
          
      The purpose is to make sure the hash table is consistently shifted, and that every character is shifted in predictable ways based upon the password values

4.) Take that newly created hash array and create a secondary hash array (called hash_array_next) using the above steps.

5.) The shuffled hash array will now serve as the password when doing the binary reduction.

6.) Take the first STRING_LENGTH value of characters from the hash array (if there are not enough in the array, move to the hash_array_next array) and add the first STRING_LENGTH amount of characters from the string to the end
6.1) i.e.: 423567string

7.) Convert each character to its binary representation and store the results as a long binary string

8.) Reduce the binary; if characters match return zero (0), otherwise return one (1)
8.1> Keep reducing until the binary string is equal to STRING_LENGTH * binary_length (which is 8 in this case)

          0 1 0 1 1 1 0 1 <- example of password (length 4) + string (length 4)
           1 1 1 0 0 1 1
            0 0 1 0 1 0
             0 1 1 1 1
              1 0 0 0     <- reduces to this
              
9.) Convert that newly reduced binary back to character values
              
