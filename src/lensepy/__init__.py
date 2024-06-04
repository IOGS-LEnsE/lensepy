__all__ = [
    "images",      # refers to the 'images' file
]

print('SupOptique Package')


# Translation
# -----------

def load_dictionary(language_path: str) -> None:
    """
    Load a dictionary from a CSV file based on the specified language.

    Parameters
    ----------
    language : str
        The language path to specify which CSV file to load.

    Returns
    -------
    None

    Notes
    -----
    This function reads a CSV file that contains key-value pairs separated by semicolons (';')
    and stores them in a global dictionary variable. The CSV file may contain comments
    prefixed by '//', which will be ignored.

    The file should have the following format:
        // comment
        // comment
        key_1 ; language_word_1
        key_2 ; language_word_2

    The function will strip any leading or trailing whitespace from the keys and values.

    See Also
    --------
    numpy.genfromtxt : Load data from a text file, with missing values handled as specified.
    """
    global dictionary
    dictionary = {}

    # Read the CSV file, ignoring lines starting with '//'
    data = np.genfromtxt(
        language_path, delimiter=';', dtype=str, comments='#', encoding='UTF-8')

    # Populate the dictionary with key-value pairs from the CSV file
    for key, value in data:
        dictionary[key.strip()] = value.strip()

def translate(key: str) -> str:
    """
    Translate a given key to its corresponding value.

    Parameters
    ----------
    key : str
        The key to translate.

    Returns
    -------
    str
        The translated value corresponding to the key. If the key does not exist, it returns the key itself.

    """    
    if ('dictionary' in globals()) and (key in dictionary):
        return dictionary[key]
    else:
        return key
        
import os
import csv

def trl(index_value: str) -> str:
    """
    Return the translation of a parameter.
    
    This function is based on a global variable called dico.
    If this variable does not exist, the parameter is directly returned.

    :param index_value: Index of the dico dictionnary (containing translations in a specific language).
    :type index_value: str
    :return: The translation of the parameter (or the index_value if dico is not a global variable)
    :rtype: str
    """
    if 'dico' in globals():
        if index_value in dico:
            return dico[index_value]
        else:
            return index_value
    else:
        return index_value
  
def read_trl(filename: str) -> dict:
    """
    Return a dictionnary of translation.
    
    This function reads a CSV file containing 2 columns :  
    - 1 column for the key index
    - 1 column for the translation.
    
    Data must be stored in a dictionnary called 'dico' to be used with trl function.

    :param filename: Filename (and path) to the CSV file containing the translations
    :type index_value: str
    :return: Dictionnary containing the translation of the parameter
    :rtype: dict
    """
    # Test if filename exists
    result_dict = {}
    if os.path.exists(filename):
        with open(filename, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header row if there is one
            result_dict = {rows[0]: rows[1] for rows in reader}
    else:
        print('File error')
    return result_dict
        
