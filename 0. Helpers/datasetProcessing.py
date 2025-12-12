from datasets import concatenate_datasets

# Methods for turning BI tagging into json
punctuation_after = [",", ".", "!", "?", ";", ":", ")", "'s"]
punctuation_before = ["("]
all_punctuation = punctuation_after + punctuation_before

def tokens_to_sentence(tokens):
    sentence = ""
    for i, token in enumerate(tokens):
        if token in punctuation_after:
            sentence += token # skip the space
        elif i != 0 and tokens[i-1] in punctuation_before:
            sentence += token # skip the space
        else:
            sentence += " " + token
    return sentence.strip()

def sentence_to_tokens(sentence):
    tokens = []
    i = 0
    while i < len(sentence):
        char = sentence[i]

        if char == " ":
            i += 1
        elif char in all_punctuation:
            # Check for "'s" case
            if char == "'" and i + 1 < len(sentence) and sentence[i+1] == 's':
                tokens.append("'s")
                i += 2
            else:
                tokens.append(char)
                i += 1
        else:
            # Accumulate a word token
            start = i
            while i < len(sentence) and sentence[i] not in all_punctuation and sentence[i] != " ":
                i += 1
            tokens.append(sentence[start:i])
    return tokens

# Entity class
class Entity:
    tokens = []
    span = ""
    entity = ""

    def __init__(self, first_token, entity):
        self.tokens = [first_token]
        self.entity = entity

    def __eq__(self, other):
        if isinstance(other, Entity):
            return self.span.lower() == other.span.lower() and self.entity.lower() == other.entity.lower()
        return False

    def __hash__(self):
        return hash((self.span, self.entity))
    
    def final_processing(self, entity_names_parsed):
        self.span = tokens_to_sentence(self.tokens)
        self.entity = entity_names_parsed[self.entity]

    def __str__(self):
        return f'{{\n   span: "{self.span}",\n   entity: "{self.entity}"\n}}'
    
    def from_dict(dict):
        entity = Entity(first_token = "", entity = dict["entity"]) 
        entity.span = dict["span"]
        return entity

    def to_dict(self):
        return {"span": self.span, "entity": self.entity}
    
# Load the dataset
def tokens_to_entities(tokens, ner_tags, entity_names_parsed, start_of_entity_indices, entity_index_to_name):
    entities = []
    current_entity = None

    for i in range(len(tokens)):

        # get current entity type
        entity_index = ner_tags[i]
        entity_type = entity_index_to_name[entity_index]

        # check to save previous entity
        if (entity_index in start_of_entity_indices or entity_index == 0) and current_entity is not None:
            current_entity.final_processing(entity_names_parsed)
            entities.append(current_entity)
            current_entity = None

        # check to start new entity
        if entity_index in start_of_entity_indices:
            current_entity = Entity(tokens[i], entity_type)

        # add token to current entity
        elif entity_index != 0 and current_entity is not None:
            # validate same entity as current entity
            if entity_type != current_entity.entity:
                print(f"Error: {entity_type} != {current_entity.entity}")
            else:
                current_entity.tokens.append(tokens[i])

    # check to save last entity
    if current_entity is not None:
        current_entity.final_processing(entity_names_parsed)
        entities.append(current_entity)

    # remove duplicates (preserving order)
    seen = set() 
    unique_entities = []

    for entity in entities:
        if entity not in seen:
            unique_entities.append(entity)
            seen.add(entity)

    return unique_entities

# Methods to concatenate datasets
def join_datasets(datasets, percentage):
    subsets = []

    for dataset in datasets:

        goal = int(len(dataset) * percentage) # without no-entity examples
        count_with_entities = 0 
        cutoff_index = 0

        while count_with_entities <= goal and cutoff_index < len(dataset):  # prevent index overflow

            example = dataset[cutoff_index]

            # only count towards goal if there are entites (not counting "O" tags)
            if 'ner_tags' in example and 'tokens' in example:
                unique_tags = set(example['ner_tags'])
                if len(example['tokens']) > 0 and len(unique_tags) > 1:
                    count_with_entities += 1
            
            cutoff_index += 1

        # select ALL examples until the goal is reached
        subsets.append(dataset.select(range(cutoff_index)))

    return concatenate_datasets(subsets)


# Fix encoding issues
def fix_encoding(text):
    try:
        # Decode the text from ISO-8859-1 (or similar encodings) and re-encode it to UTF-8
        return text.encode('iso-8859-1').decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        return text

# Recursively fix encoding in the JSON data (handles both strings and nested structures)
def recursive_fix(obj):
    if isinstance(obj, dict):
        return {key: recursive_fix(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [recursive_fix(item) for item in obj]
    elif isinstance(obj, str):
        return fix_encoding(obj)
    else:
        return obj