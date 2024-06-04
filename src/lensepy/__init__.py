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
