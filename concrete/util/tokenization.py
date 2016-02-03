import logging

from concrete.structure.ttypes import TokenizationKind


def get_tokens(tokenization, suppress_warnings=False):
    '''
    Return list of Tokens from lattice.cachedBestPath, if Tokenization
    kind is TOKEN_LATTICE; else, return list of Tokens from tokenList.

    Warn and return list of Tokens from tokenList if kind is not set.
    Return None if kind is set but the respective data fields are not.
    '''

    if tokenization.kind is None:
        if not suppress_warnings:
            logging.warn('Tokenization.kind is None but is required in '
                         'Concrete; using tokenList')

        token_list = tokenization.tokenList
        if token_list.tokenList is not None:
            return token_list.tokenList

    elif tokenization.kind == TokenizationKind.TOKEN_LATTICE:
        token_lattice = tokenization.lattice
        if token_lattice.cachedBestPath is not None:
            lattice_path = token_lattice.cachedBestPath
            if lattice_path.tokenList is not None:
                return lattice_path.tokenList

    elif tokenization.kind == TokenizationKind.TOKEN_LIST:
        token_list = tokenization.tokenList
        if token_list.tokenList is not None:
            return token_list.tokenList

    else:
        raise ValueError('Unrecognized TokenizationKind %s'
                         % tokenization.kind)

    return None


def get_tagged_tokens(tokenization, tagging_type):
    '''
    Return list of TaggedTokens of taggingType equal to tagging_type,
    if there is a unique choice.

    Raise exception if there is no matching tagging or more than one
    matching tagging.
    '''
    tts = [
        tt
        for tt in tokenization.tokenTaggingList
        if tt.taggingType == tagging_type
    ]
    if len(tts) == 0:
        raise Exception('No %s tagging.' % tagging_type)
    elif len(tts) == 1:
        return tts[0].taggedTokenList
    else:
        raise Exception('More than one %s tagging.' % tagging_type)


def get_lemmas(t):
    return get_tagged_tokens(t, 'LEMMA')


def get_pos(t):
    return get_tagged_tokens(t, 'POS')


def plus(x, y):
    return x + y


def flatten(a):
    return reduce(plus, a, [])


def get_comm_tokens(comm, sect_pred=None, suppress_warnings=False):
    '''
    Return list of Tokens in communication, delegating to get_tokens
    for each sentence.
    '''
    return flatten(map(
        lambda sect: flatten(map(
            lambda sent: get_tokens(sent.tokenization, suppress_warnings),
            sect.sentenceList
        )),
        filter(sect_pred, comm.sectionList)
        if (sect_pred is not None) else comm.sectionList
    ))
