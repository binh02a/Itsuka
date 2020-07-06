from collections import Counter

import spacy
import textacy
from spacy import displacy

nlp = spacy.load("en_core_web_sm")

merge_nps = nlp.create_pipe("merge_noun_chunks")
nlp.add_pipe(merge_nps)

merge_ents = nlp.create_pipe("merge_entities")
nlp.add_pipe(merge_ents)

# matcher = PhraseMatcher(nlp.vocab)
# matcher.add("OBAMA", None, nlp("Barack Obama"))
# matcher.add("HEALTH", None, nlp("health care reform"), nlp("healthcare reforms"))
# doc = nlp("Barack Obama urges Congress to find courage to defend his healthcare reforms")
# matches = matcher(doc)
# for match in matches:
#   print(nlp.vocab.strings[match[0]])

# https://spacy.io/usage/rule-based-matching

# noun_pharses=set()
# for nc in doc.noun_chunks:
#    for np in [nc, doc[nc.root.left_edge.i:nc.root.right_edge.i+1]]:
#       noun_pharses.add(np)

about_talk_text = ('The talk will introduce reader about Use'
                   ' cases of Natural Language Processing in'
                   ' Fintech')
pattern = r'(<VERB>?<ADV>*<VERB>+)'
about_talk_doc = textacy.make_spacy_doc(about_talk_text,
                                        lang='en_core_web_sm')
verb_phrases = textacy.extract.pos_regex_matches(about_talk_doc, pattern)

# Print all Verb Phrase
#for chunk in verb_phrases:
#    print(chunk.text)


# Extract Noun Phrase to explain what nouns are involved
for chunk in about_talk_doc.noun_chunks:
    print (chunk)
