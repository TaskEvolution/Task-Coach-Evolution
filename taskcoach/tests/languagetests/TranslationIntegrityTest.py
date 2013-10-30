# -*- coding: UTF-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2013 Task Coach developers <developers@taskcoach.org>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from taskcoachlib import meta
import string  # pylint: disable=W0402
import re  
import test


class TranslationIntegrityTestsMixin(object):
    ''' Unittests for translations. This class is subclassed below for each
        translated string in each language. '''
    
    conversionSpecificationRE = re.compile('%\(\w+\)[sd]')
    
    @staticmethod
    def countMatches(regex, search_string):
        matches = dict()
        for match in re.findall(regex, search_string):
            matches[match] = matches.get(match, 0) + 1
        return matches
            
    def testMatchingConversionSpecifications(self):
        regex = self.conversionSpecificationRE
        matches_english = self.countMatches(regex, self.englishString)
        matches_translation = self.countMatches(regex, self.translatedString)
        self.assertEqual(matches_english, matches_translation, self.englishString)
            
    def testMatchingNonLiterals(self):
        for symbol in '\t', '|', '%s', '%d', '%.2f':
            self.assertEqual(self.englishString.count(symbol), 
                self.translatedString.count(symbol),
                "Symbol ('%s') doesn't match for '%s' and '%s'" % (symbol,
                    self.englishString, self.translatedString))
            
    def testMatchingAmpersands(self):
        # If the original string contains zero or one ampersands, it may be 
        # an accelerator. In that case, we don't require the translated string
        # to have an accelerator as well, because many translators don't use 
        # it and it doesn't break the application. However, if the original
        # string contains more than one ampersand it's probably HTML. In that
        # case we do require the number of ampersands to match exactly in the 
        # original and translated string.
        translatedString = self.removeUmlauts(self.translatedString)
        nrEnglishAmpersand = self.englishString.count('&')
        nrTranslatedAmpersand = translatedString.count('&')
        if nrEnglishAmpersand <= 1 and not '\n' in self.englishString:
            self.failUnless(nrTranslatedAmpersand in [0, 1], 
                "'%s' has more than one '&'" % self.translatedString)
        else:
            self.assertEqual(nrEnglishAmpersand, nrTranslatedAmpersand,
                "'%s' has more or less '&'s than '%s'" % (self.translatedString,
                self.englishString))

    usedShortcuts = dict()
    # Some keyboard shortcuts are used more than once, list those here:
    maxShortcuts = {'Ctrl-RETURN': 2, 'Shift+Ctrl+T': 3}
    
    def testUniqueShortCut(self):
        if '\t' in self.translatedString:
            shortcut = self.translatedString.split('\t')[1]
            shortcutKey = shortcut, self.language
            timesUsed = self.usedShortcuts.get(shortcutKey, 0)
            timesAllowed = self.maxShortcuts.get(shortcut, 1)
            self.failIf(timesUsed > timesAllowed, "Shortcut ('%s') used more "
                        "than once in language %s." % shortcutKey)
            self.usedShortcuts[shortcutKey] = timesUsed + 1
            
    def testMatchingShortCut(self):
        for shortcutPrefix in ('Ctrl+', 'Ctrl-', 'Shift+', 'Shift-', 
                               'Alt+', 'Alt-', 'Shift+Ctrl+', 'Shift-Ctrl-',
                               'Shift+Alt+', 'Shift-Alt-'):
            self.assertEqual(self.englishString.count('\t' + shortcutPrefix),
                             self.translatedString.count('\t' + shortcutPrefix),
                             "Shortcut prefix ('%s') doesn't match for '%s' "
                             "and '%s'" % (shortcutPrefix, self.englishString, 
                                           self.translatedString))
            
    def testShortCutIsAscii(self):
        ''' Test that the translated short cut key is using ASCII only. '''
        if '\t' in self.translatedString:
            shortcut = set(self.translatedString.split('\t')[1])
            self.failUnless(shortcut & set(string.ascii_letters + string.digits))
            
    @staticmethod
    def ellipsisCount(text):
        return text.count('...') + text.count('…')
    
    def testMatchingEllipses(self):
        self.assertEqual(self.ellipsisCount(self.englishString),
                         self.ellipsisCount(self.translatedString),
                         "Ellipses ('...') don't match for '%s' and '%s'" % \
                         (self.englishString, self.translatedString))

    umlautRE = re.compile(r'&[A-Za-z]uml;')
    
    @classmethod
    def removeUmlauts(cls, text):
        return re.sub(cls.umlautRE, '', text)      
    

def installAllTestCaseClasses():
    for language in getLanguages():
        installTestCaseClasses(language)


def getLanguages():
    return [language for language in meta.data.languages.values() \
            if language is not None]


def installTestCaseClasses(language):
    translation = __import__('taskcoachlib.i18n.%s' % language, 
                             fromlist=['dict'])
    for englishString, translatedString in translation.dict.iteritems():        
        installTranslationTestCaseClass(language, englishString, 
                                              translatedString)


def installTranslationTestCaseClass(language, englishString, 
                                          translatedString):
    testCaseClassName = translationTestCaseClassName(language, englishString)
    testCaseClass = translationTestCaseClass(testCaseClassName, 
        language, englishString, translatedString)
    globals()[testCaseClassName] = testCaseClass


def translationTestCaseClassName(language, englishString, 
                                 prefix='TranslationIntegrityTest'):
    ''' Generate a class name for the test case class based on the language
        and the English string. '''
    # Make sure we only use characters allowed in Python identifiers:
    englishString = englishString.replace(' ', '_')
    allowableCharacters = string.ascii_letters + string.digits + '_'
    englishString = ''.join([char for char in englishString \
                             if char in allowableCharacters])
    className = '%s_%s_%s' % (prefix, language, englishString)
    count = 0
    while className in globals():  # Make sure className is unique
        count += 1
        className = '%s_%s_%s_%d' % (prefix, language, englishString, count)
    return className


def translationTestCaseClass(className, language, englishString, translatedString):
    class_ = type(className, (TranslationIntegrityTestsMixin, test.TestCase), 
                  {})
    class_.language = language
    class_.englishString = englishString
    class_.translatedString = translatedString
    return class_


# Create all test cases and install them in the global name space:
installAllTestCaseClasses() 
