'''

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.

'''


from topicargspec import ArgSpecGiven


class ITopicDefnProvider:
    '''
    All topic definition providers must mimic this interface. They must
    override the getDefn(), getTreeDoc() and topicNames() methods. 
    Once a provider has been given to pub.addTopicDefnProvider(), 
    subscribe() and sendMessage() will use it to validate the listener
    and message (respectively).
    '''
    
    ArgSpecGiven = ArgSpecGiven
    
    def getDefn(self, topicNameTuple):
        '''Must return a pair (string, ArgSpecGiven), or (None, None). 
        The first member is a description for topic, and second one 
        contains the listener callback protocol. '''
        msg = 'Must return (string, ArgSpecGiven), or (None, None)'
        raise NotImplementedError(msg)

    def topicNames(self):
        '''Return an iterator over topic names available from this provider.
        Note that the topic names should be in tuple rather than dotted-string
        form so as to be compatible with getDefn().'''
        msg = 'Must return a list of topic names available from this provider'
        raise NotImplementedError(msg)

    def getTreeDoc(self):
        '''Get the document for the tree (root node)'''
        msg = 'Must return documentation string for root topic (tree)'
        raise NotImplementedError(msg)

    def __iter__(self):
        '''Same as self.topicNames(), do NOT override.'''
        return self.topicNames()


