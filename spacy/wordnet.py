import spacy

import explacy

# Load an spacy model (supported models are "es" and "en")
nlp = spacy.load("en_core_web_sm")

explacy.print_parse_info(nlp, 'A couple was assaulted by a criminal falsely portraying himself as their rideshare driver, forced to withdraw money from an ATM, then held overnight before managing to alert a neighbor to their whereabouts.')
