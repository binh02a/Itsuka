import spacy
import textacy
from nltk.corpus import wordnet as wn

input_text = "In 2016 The US attracts migrants and refugees who are particularly at risk of vulnerability to human " \
             "trafficking. Trafficking victims often responding to fraudulent offers of employment in the US migrate " \
             "willingly and are subsequently subjected to conditions of involuntary servitude in industries such as " \
             "forced labour and commercial sexual exploitation.Suamhirs was trafficked from Honduras to the United " \
             "States by his Godmother by train in 2016, who threatened to kill his family if he did not do what she " \
             "told him. Suamhirs " \
             "was finally rescued when a neighbour reported the large number of people coming and going from the " \
             "house to the police. In this narrative Suamhirs talks of facing his trafficker in the court and the " \
             "continuous nature of rehabilitation. Human trafficking is a crime that takes away souls, that takes " \
             "away memories. My trafficker was someone who knew my family. I was given specific instructions: You're " \
             "going to do what I ask you to do. If you not"

input_text1 = "2014 (Narrative date) There are an estimated 518,000 people living in modern slavery in Egypt, 465," \
              "000 in Sudan and an estimated 451,000 in Eritrea (GSI 2018). Since 2006 tens of thousands of Eritreans " \
              "fleeing widespread human rights abuses and destitution have ended up in Egypt's Sinai Peninsula. Until " \
              "2010, they passed through Sinai voluntarily and generally without any problems and crossed in to " \
              "Israel. However, since then, Sudanese traffickers have kidnapped Eritreans in eastern Sudan and sold " \
              "them to Egyptian traffickers in Sinai who have subjected at least hundreds to violence in order to " \
              "extort large sums of money from their relatives.Petros*, a 43-year-old Eritrean man was travelling " \
              "with his wife and four children when they crossed to Sudan in May 2011. There, Sudanese traffickers " \
              "kidnapped and held them for 65 days before moving them to Sinai. There, he said traffickers held them " \
              "for 25 days and tortured him and other Eritreans. After Petros paid the kidnappers $14," \
              "000 they released him. At around 8 p.m., two of the Bedouin who held us took 15 of us\xe2\x80\x94nine " \
              "Sudanese and six Eritreans\xe2\x80\x94to the [Israeli] border in two cars where we met two Egyptian " \
              "soldiers. We all sat together for about half an hour and the soldiers took us to the Israeli fence and " \
              "showed us where to cross.*name given\xc2\xa0Narrative provided by Human Rights Watch in their report " \
              "\xe2\x80\x9cI Wanted to Lie Down and Die\xe2\x80\x9d: Trafficking and Torture of Eritreans in Sudan " \
              "and Egypt\xc2\xa0 Country Sudan (trafficked from), Egypt (slavery location), Sudan (slavery location) " \
              "Theme Trafficking Type Narrative."

nlp = spacy.load('en_core_web_md')
doc = nlp(input_text)
threshold = 0.7

incident_fields = [
    'start_date',
    'end_date',
    'number_of_victim',
    'nationality',
    'gender',
    'age',
    'organisations',
    'routes',
    'geography',
    'transport methods',
    'type, sub-type',
    'recruitment methods',
    'trafficker operation location'
]

incident_data = {}
for field in incident_fields:
    incident_data[field] = 'unknown'


def log_array(mess, array):
    print('\n>>>', mess)
    for item in array:
        print('\t', item)


# 1. Get noun chunk, verb chunk without stopwords
noun_tokens = [chunk.root for chunk in doc.noun_chunks
               if chunk.root.has_vector and not chunk.root.is_stop]
verb_tokens = [chunk.root for chunk in textacy.extract.matches(doc, "POS:VERB:? POS:ADV:* POS:VERB:+")
               if chunk.root.has_vector and not chunk.root.is_stop]
doc_tokens = noun_tokens + verb_tokens


# 2. Get field's domain included verb and noun keywords using wordnet
def get_domain(field):
    lemma_names = [field]
    synsets = wn.synsets(field)
    for synset in synsets:
        lemma_names.extend(synset.lemma_names())
        for hyponym in synset.hyponyms():
            lemma_names.extend(hyponym.lemma_names())

    domain_tok = []
    for lemma in lemma_names:
        lemma = lemma.replace('_', ' ')
        lemma_span = nlp(lemma)[:]
        if lemma_span.root.pos_ == 'NOUN':
            domain_tok.extend(list(lemma_span.root.children) or [lemma_span.root])
        else:
            domain_tok.append(lemma_span.root)

    return domain_tok


field_domain = get_domain('victim') + get_domain('trafficked')


# 3. Get similarity of those chunks with domain
def get_similar_token(field):
    similar_toks = []
    for token in doc_tokens:
        max_distance = max([domain_token.similarity(token) for domain_token in field_domain] or [0])
        if max_distance > threshold and token.tag_ == field.tag_:
            similar_toks.append(token)
    return similar_toks


similar_tokens = get_similar_token(nlp('victim')[0]) + get_similar_token(nlp('trafficked')[0])

# 4. Get similar sentences
log_array("Similar keywords:", similar_tokens)
victim_sentences = []
for token in similar_tokens:
    if token.sent not in victim_sentences: victim_sentences.append(token.sent)

log_array("Similar sentences:", victim_sentences)

# 5. Extract data from similar sentences
subjects = []
extractable_sents = []
person_labels = ['PERSON', 'ORG']
for sent in victim_sentences:
    for ent in sent.ents:
        label = ent.label_
        if label in person_labels:
            subjects.append(ent)
            if ent.sent not in extractable_sents:
                extractable_sents.append(ent.sent)

log_array('Extractable sentences', extractable_sents)

# get nations
nationality_labels = ['GPE', 'LOC']
date_labels = ['TIME', 'DATE']
locations = []
dates = []
for sent in extractable_sents:
    sent_locs = [ent for ent in sent.ents if ent.label_ in nationality_labels]
    locations.extend(sent_locs)
    date = [ent for ent in sent.ents if ent.label_ in date_labels]
    dates.extend(date)
locations = [location for location in locations if location not in subjects]


tokens = [location.root for location in locations]
for i, token in enumerate(tokens):
    root = [an for an in token.ancestors if an.pos_ == 'VERB' and an == token.sent.root]
    nationality_prep = ['from', 'between', 'at', 'in', 'on', 'of']
    head = token.head
    if root and (head.dep_ == 'prep'):
        if head.text in nationality_prep:
            incident_data['nationality'] = locations[i].text
        else:
            incident_data['geography'] = locations[i].text
print(incident_data['nationality'], '-', incident_data['geography'])