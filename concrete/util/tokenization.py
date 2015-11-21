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
            logging.warn('Tokenization.kind is None but is required in Concrete; using tokenList')

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
        raise ValueError('Unrecognized TokenizationKind %d' % tokenization.kind)

    return None


def get_lemmas(tokenization):
    '''
    Return list of lemmas (as TaggedTokens), if there is a unique
    choice.

    Raise exception if there is no lemma tagging or more than one
    lemma tagging.
    '''

    lemma_tts = [
        tt
        for tt in tokenization.tokenTaggingList
        if tt.taggingType == u'LEMMA'
    ]
    if len(lemma_tts) == 0:
        raise Exception('No lemma tagging.')
    elif len(lemma_tts) == 1:
        return lemma_tts[0].taggedTokenList
    else:
        raise Exception('More than one lemma tagging.')


def get_pos(tokenization):
    '''
    Return list of POS tags (as TaggedTokens), if there is a unique
    choice.

    Raise exception if there is no POS tagging or more than one
    POS tagging.
    '''

    pos_tts = [
        tt
        for tt in tokenization.tokenTaggingList
        if tt.taggingType == u'POS'
    ]
    if len(pos_tts) == 0:
        raise Exception('No POS tagging.')
    elif len(pos_tts) == 1:
        return pos_tts[0].taggedTokenList
    else:
        raise Exception('More than one POS tagging.')


plus = lambda x, y: x + y

flatten = lambda a: reduce(plus, a, [])

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
            if (sect_pred is not None)
            else comm.sectionList
    ))
