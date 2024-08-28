# pip install thefuzz

# Check the similarity score
from thefuzz import fuzz

full_name = ["Kurtis K D Pykes","ciao"]
full_name_reordered = ["Kurtis Pykes K D"]
name = "Kurtis Pykes"

# Order does not matter for token sort ratio
print(f"Token sort ratio similarity score: {fuzz.token_sort_ratio(full_name_reordered, full_name)}")

# Order matters for partial ratio
print(f"Partial ratio similarity score: {fuzz.partial_ratio(full_name, full_name_reordered)}")

# Order will not effect simple ratio if strings do not match
print(f"Simple ratio similarity score: {fuzz.ratio(name, full_name)}")

"""
Token sort ratio similarity score: 100
Partial ratio similarity score: 75
Simple ratio similarity score: 86
"""

# Process 

# The process module enables users to extract text from a collection using fuzzy string matching. 
# Calling the extract() method on the process module returns the strings with a similarity score in a vector.
# For example: 
from thefuzz import process

collection = ["come stai", "io sono", "spegni la luce"]
print(process.extract("mi accendi la luce", collection, scorer=fuzz.ratio))


