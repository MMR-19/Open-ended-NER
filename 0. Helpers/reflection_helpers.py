import unicodedata

def char_is_punctuation(ch):
    return unicodedata.category(ch).startswith("P")

def word_only_punctuation(text):
    return len(text) > 0 and all(char_is_punctuation(ch) for ch in text)

def get_token_context_include(tokens, center_idx, context_length = 2):

    left_tokens = []
    left_relevant_tokens = 0
    go_left_idx = center_idx

    while go_left_idx > 0 and left_relevant_tokens < context_length:
        potential_token = tokens[go_left_idx - 1]
        left_tokens.append(potential_token)
        go_left_idx -= 1

        # only count if token is relevant (ignore punctuation)
        if not word_only_punctuation(potential_token):
            left_relevant_tokens += 1

    # invert left_tokens
    if left_tokens:
        left_tokens.reverse()

    right_tokens = []
    right_relevant_tokens = 0
    go_right_idx = center_idx

    while go_right_idx < len(tokens) - 1 and right_relevant_tokens < context_length:
        potential_token = tokens[go_right_idx + 1]
        right_tokens.append(potential_token)
        go_right_idx += 1

        # only count if token is relevant (ignore punctuation)
        if not word_only_punctuation(potential_token):
            right_relevant_tokens += 1

    return left_tokens + [tokens[center_idx]] + right_tokens

def get_token_context_exclude(tokens, center_idx, context_length = 2):

    left_tokens = []
    go_left_idx = center_idx

    while go_left_idx > 0 and len(left_tokens) < context_length:
        potential_token = tokens[go_left_idx - 1]
        go_left_idx -= 1

        # only count if token is relevant (ignore punctuation)
        if not word_only_punctuation(potential_token):
            left_tokens.append(potential_token)

    # invert left_tokens
    if left_tokens:
        left_tokens.reverse()

    right_tokens = []
    go_right_idx = center_idx

    while go_right_idx < len(tokens) - 1 and len(right_tokens) < context_length:
        potential_token = tokens[go_right_idx + 1]
        go_right_idx += 1

        # only count if token is relevant (ignore punctuation)
        if not word_only_punctuation(potential_token):
            right_tokens.append(potential_token)

    return left_tokens + right_tokens


def find_sub_list(sl,l):
    # results=[]
    # sll=len(sl)
    # for ind in (i for i,e in enumerate(l) if e==sl[0]):
    #     if l[ind:ind+sll]==sl:
    #         results.append((ind,ind+sll-1))

    # return results

    sll=len(sl)
    for ind in (i for i,e in enumerate(l) if e==sl[0]):
        if l[ind:ind+sll]==sl:
            return ind, ind+sll-1

def get_entity_context(sentence, entity_span, context_length = 2, include_entity = True):

    # ignore punctuation and fix 's spacing
    sentence = sentence.lower().strip().replace(" 's", "'s")
    entity_span = entity_span.lower().strip().replace(" 's", "'s")

    sentence = [c if not char_is_punctuation(c) else " " for c in sentence]
    entity_span = [c if not char_is_punctuation(c) else " " for c in entity_span]

    sentence = "".join(sentence).replace("  ", " ")
    entity_span = "".join(entity_span).replace("  ", " ")

    tokens = sentence.split()
    entity_tokens = entity_span.split()

    # find entity in tokens
    indices = find_sub_list(entity_tokens, tokens)
    if not indices:
        return None

    # start and end of entity
    start_idx, end_idx = indices

    # compute start and end indices with context
    left_tokens = []
    left_relevant_tokens = 0
    go_left_idx = start_idx

    while go_left_idx > 0 and left_relevant_tokens < context_length:
        potential_token = tokens[go_left_idx - 1]
        left_tokens.append(potential_token)
        go_left_idx -= 1

        # only count if token is relevant (ignore punctuation)
        if not word_only_punctuation(potential_token):
            left_relevant_tokens += 1

    # invert left_tokens
    if left_tokens:
        left_tokens.reverse()

    right_tokens = []
    right_relevant_tokens = 0
    go_right_idx = end_idx

    while go_right_idx < len(tokens) - 1 and right_relevant_tokens < context_length:
        potential_token = tokens[go_right_idx + 1]
        right_tokens.append(potential_token)
        go_right_idx += 1

        # only count if token is relevant (ignore punctuation)
        if not word_only_punctuation(potential_token):
            right_relevant_tokens += 1

    if include_entity:
        return left_tokens + entity_tokens + right_tokens
    else:
        return left_tokens + right_tokens

def get_entity_inner_boundary(entity_span, context_length = 2):

    # ignore punctuation and fix 's spacing
    entity_span = entity_span.strip().replace(" 's", "'s")
    entity_span = [c if not char_is_punctuation(c) else " " for c in entity_span]
    entity_span = "".join(entity_span).replace("  ", " ")

    entity_tokens = entity_span.split()
    
    if len(entity_tokens) <= context_length * 2:
        return entity_tokens
    
    else:
        return entity_tokens[:context_length] + entity_tokens[-context_length:]

