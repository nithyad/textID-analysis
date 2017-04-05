"""Porter Stemming Algorithm
This is the Porter stemming algorithm, ported to Python from the
version coded up in ANSI C by the author. It may be be regarded
as canonical, in that it follows the algorithm presented in

Porter, 1980, An algorithm for suffix stripping, Program, Vol. 14,
no. 3, pp 130-137,

only differing from it at the points maked --DEPARTURE-- below.

See also http://www.tartarus.org/~martin/PorterStemmer

The algorithm as described in the paper could be exactly replicated
by adjusting the points of DEPARTURE, but this is barely necessary,
because (a) the points of DEPARTURE are definitely improvements, and
(b) no encoding of the Porter stemmer I have seen is anything like
as exact as this version, even with the points of DEPARTURE!

Vivake Gupta (v@nano.com)

Release 1: January 2001

Further adjustments by Santiago Bruno (bananabruno@gmail.com)
to allow word input not restricted to one word per line, leading
to:

release 2: July 2008
"""

#Final analsysis and text portion are in the word document in the zip file

#By: Nithya Deepak, Priyanka Agarwal, Nisha Bhatia

import sys
import math

class PorterStemmer:

    def __init__(self):
        """The main part of the stemming algorithm starts here.
        b is a buffer holding a word to be stemmed. The letters are in b[k0],
        b[k0+1] ... ending at b[k]. In fact k0 = 0 in this demo program. k is
        readjusted downwards as the stemming progresses. Zero termination is
        not in fact used in the algorithm.

        Note that only lower case sequences are stemmed. Forcing to lower case
        should be done before stem(...) is called.
        """

        self.b = ""  # buffer for word to be stemmed
        self.k = 0
        self.k0 = 0
        self.j = 0   # j is a general offset into the string

    def cons(self, i):
        """cons(i) is TRUE <=> b[i] is a consonant."""
        if self.b[i] == 'a' or self.b[i] == 'e' or self.b[i] == 'i' or self.b[i] == 'o' or self.b[i] == 'u':
            return 0
        if self.b[i] == 'y':
            if i == self.k0:
                return 1
            else:
                return (not self.cons(i - 1))
        return 1

    def m(self):
        """m() measures the number of consonant sequences between k0 and j.
        if c is a consonant sequence and v a vowel sequence, and <..>
        indicates arbitrary presence,

           <c><v>       gives 0
           <c>vc<v>     gives 1
           <c>vcvc<v>   gives 2
           <c>vcvcvc<v> gives 3
           ....
        """
        n = 0
        i = self.k0
        while 1:
            if i > self.j:
                return n
            if not self.cons(i):
                break
            i = i + 1
        i = i + 1
        while 1:
            while 1:
                if i > self.j:
                    return n
                if self.cons(i):
                    break
                i = i + 1
            i = i + 1
            n = n + 1
            while 1:
                if i > self.j:
                    return n
                if not self.cons(i):
                    break
                i = i + 1
            i = i + 1

    def vowelinstem(self):
        """vowelinstem() is TRUE <=> k0,...j contains a vowel"""
        for i in range(self.k0, self.j + 1):
            if not self.cons(i):
                return 1
        return 0

    def doublec(self, j):
        """doublec(j) is TRUE <=> j,(j-1) contain a double consonant."""
        if j < (self.k0 + 1):
            return 0
        if (self.b[j] != self.b[j-1]):
            return 0
        return self.cons(j)

    def cvc(self, i):
        """cvc(i) is TRUE <=> i-2,i-1,i has the form consonant - vowel - consonant
        and also if the second c is not w,x or y. this is used when trying to
        restore an e at the end of a short  e.g.

           cav(e), lov(e), hop(e), crim(e), but
           snow, box, tray.
        """
        if i < (self.k0 + 2) or not self.cons(i) or self.cons(i-1) or not self.cons(i-2):
            return 0
        ch = self.b[i]
        if ch == 'w' or ch == 'x' or ch == 'y':
            return 0
        return 1

    def ends(self, s):
        """ends(s) is TRUE <=> k0,...k ends with the string s."""
        length = len(s)
        if s[length - 1] != self.b[self.k]: # tiny speed-up
            return 0
        if length > (self.k - self.k0 + 1):
            return 0
        if self.b[self.k-length+1:self.k+1] != s:
            return 0
        self.j = self.k - length
        return 1

    def setto(self, s):
        """setto(s) sets (j+1),...k to the characters in the string s, readjusting k."""
        length = len(s)
        self.b = self.b[:self.j+1] + s + self.b[self.j+length+1:]
        self.k = self.j + length

    def r(self, s):
        """r(s) is used further down."""
        if self.m() > 0:
            self.setto(s)

    def step1ab(self):
        """step1ab() gets rid of plurals and -ed or -ing. e.g.

           caresses  ->  caress
           ponies    ->  poni
           ties      ->  ti
           caress    ->  caress
           cats      ->  cat

           feed      ->  feed
           agreed    ->  agree
           disabled  ->  disable

           matting   ->  mat
           mating    ->  mate
           meeting   ->  meet
           milling   ->  mill
           messing   ->  mess

           meetings  ->  meet
        """
        if self.b[self.k] == 's':
            if self.ends("sses"):
                self.k = self.k - 2
            elif self.ends("ies"):
                self.setto("i")
            elif self.b[self.k - 1] != 's':
                self.k = self.k - 1
        if self.ends("eed"):
            if self.m() > 0:
                self.k = self.k - 1
        elif (self.ends("ed") or self.ends("ing")) and self.vowelinstem():
            self.k = self.j
            if self.ends("at"):   self.setto("ate")
            elif self.ends("bl"): self.setto("ble")
            elif self.ends("iz"): self.setto("ize")
            elif self.doublec(self.k):
                self.k = self.k - 1
                ch = self.b[self.k]
                if ch == 'l' or ch == 's' or ch == 'z':
                    self.k = self.k + 1
            elif (self.m() == 1 and self.cvc(self.k)):
                self.setto("e")

    def step1c(self):
        """step1c() turns terminal y to i when there is another vowel in the stem."""
        if (self.ends("y") and self.vowelinstem()):
            self.b = self.b[:self.k] + 'i' + self.b[self.k+1:]

    def step2(self):
        """step2() maps double suffices to single ones.
        so -ization ( = -ize plus -ation) maps to -ize etc. note that the
        string before the suffix must give m() > 0.
        """
        if self.b[self.k - 1] == 'a':
            if self.ends("ational"):   self.r("ate")
            elif self.ends("tional"):  self.r("tion")
        elif self.b[self.k - 1] == 'c':
            if self.ends("enci"):      self.r("ence")
            elif self.ends("anci"):    self.r("ance")
        elif self.b[self.k - 1] == 'e':
            if self.ends("izer"):      self.r("ize")
        elif self.b[self.k - 1] == 'l':
            if self.ends("bli"):       self.r("ble") # --DEPARTURE--
            # To match the published algorithm, replace this phrase with
            #   if self.ends("abli"):      self.r("able")
            elif self.ends("alli"):    self.r("al")
            elif self.ends("entli"):   self.r("ent")
            elif self.ends("eli"):     self.r("e")
            elif self.ends("ousli"):   self.r("ous")
        elif self.b[self.k - 1] == 'o':
            if self.ends("ization"):   self.r("ize")
            elif self.ends("ation"):   self.r("ate")
            elif self.ends("ator"):    self.r("ate")
        elif self.b[self.k - 1] == 's':
            if self.ends("alism"):     self.r("al")
            elif self.ends("iveness"): self.r("ive")
            elif self.ends("fulness"): self.r("ful")
            elif self.ends("ousness"): self.r("ous")
        elif self.b[self.k - 1] == 't':
            if self.ends("aliti"):     self.r("al")
            elif self.ends("iviti"):   self.r("ive")
            elif self.ends("biliti"):  self.r("ble")
        elif self.b[self.k - 1] == 'g': # --DEPARTURE--
            if self.ends("logi"):      self.r("log")
        # To match the published algorithm, delete this phrase

    def step3(self):
        """step3() dels with -ic-, -full, -ness etc. similar strategy to step2."""
        if self.b[self.k] == 'e':
            if self.ends("icate"):     self.r("ic")
            elif self.ends("ative"):   self.r("")
            elif self.ends("alize"):   self.r("al")
        elif self.b[self.k] == 'i':
            if self.ends("iciti"):     self.r("ic")
        elif self.b[self.k] == 'l':
            if self.ends("ical"):      self.r("ic")
            elif self.ends("ful"):     self.r("")
        elif self.b[self.k] == 's':
            if self.ends("ness"):      self.r("")

    def step4(self):
        """step4() takes off -ant, -ence etc., in context <c>vcvc<v>."""
        if self.b[self.k - 1] == 'a':
            if self.ends("al"): pass
            else: return
        elif self.b[self.k - 1] == 'c':
            if self.ends("ance"): pass
            elif self.ends("ence"): pass
            else: return
        elif self.b[self.k - 1] == 'e':
            if self.ends("er"): pass
            else: return
        elif self.b[self.k - 1] == 'i':
            if self.ends("ic"): pass
            else: return
        elif self.b[self.k - 1] == 'l':
            if self.ends("able"): pass
            elif self.ends("ible"): pass
            else: return
        elif self.b[self.k - 1] == 'n':
            if self.ends("ant"): pass
            elif self.ends("ement"): pass
            elif self.ends("ment"): pass
            elif self.ends("ent"): pass
            else: return
        elif self.b[self.k - 1] == 'o':
            if self.ends("ion") and (self.b[self.j] == 's' or self.b[self.j] == 't'): pass
            elif self.ends("ou"): pass
            # takes care of -ous
            else: return
        elif self.b[self.k - 1] == 's':
            if self.ends("ism"): pass
            else: return
        elif self.b[self.k - 1] == 't':
            if self.ends("ate"): pass
            elif self.ends("iti"): pass
            else: return
        elif self.b[self.k - 1] == 'u':
            if self.ends("ous"): pass
            else: return
        elif self.b[self.k - 1] == 'v':
            if self.ends("ive"): pass
            else: return
        elif self.b[self.k - 1] == 'z':
            if self.ends("ize"): pass
            else: return
        else:
            return
        if self.m() > 1:
            self.k = self.j

    def step5(self):
        """step5() removes a final -e if m() > 1, and changes -ll to -l if
        m() > 1.
        """
        self.j = self.k
        if self.b[self.k] == 'e':
            a = self.m()
            if a > 1 or (a == 1 and not self.cvc(self.k-1)):
                self.k = self.k - 1
        if self.b[self.k] == 'l' and self.doublec(self.k) and self.m() > 1:
            self.k = self.k -1

    def stem(self, p, i, j):
        """In stem(p,i,j), p is a char pointer, and the string to be stemmed
        is from p[i] to p[j] inclusive. Typically i is zero and j is the
        offset to the last character of a string, (p[j+1] == '\0'). The
        stemmer adjusts the characters p[i] ... p[j] and returns the new
        end-point of the string, k. Stemming never increases word length, so
        i <= k <= j. To turn the stemmer into a module, declare 'stem' as
        extern, and delete the remainder of this file.
        """
        # copy the parameters into statics
        self.b = p
        self.k = j
        self.k0 = i
        if self.k <= self.k0 + 1:
            return self.b # --DEPARTURE--

        # With this line, strings of length 1 or 2 don't go through the
        # stemming process, although no mention is made of this in the
        # published algorithm. Remove the line to match the published
        # algorithm.

        self.step1ab()
        self.step1c()
        self.step2()
        self.step3()
        self.step4()
        self.step5()
        return self.b[self.k0:self.k+1]


def create_stem( word ):
    """  This is the primary stemming function:
         create_stem takes in a word, a string,
         and returns a string (the stem of word)
         according to the porter stemmer

         the input word should contain no punctuation
    """
    p = PorterStemmer()
    word = word.lower() # lowercases word
    N = len(word)
    stem = p.stem( word, 0, N-1 )
    return stem

class TextModel:

    def __init__(self, name):
        """ the constructor for the TextModel class
            all dictionaries are started at empty
            the name is just for our own purposes, to keep things 
            organized
        """
        self.name = name
        self.words = {}   # starts empty
        self.wordlengths = {}
        self.stems = {}
        self.sentencelengths = {}
        self.punct = {}
        # you will want another dictionary for your text feature

    def __repr__(self):
        """ this method creates the string version of TextModel objects
        """
        s  = "\nModel name: " + str(self.name) + "\n"
        s += "    n. of words: " + str(len(self.words))  + "\n"
        s += "    n. of word lengths: " + str(len(self.wordlengths))  + "\n"
        s += "    n. of sentence lengths: " + str(len(self.sentencelengths))  + "\n"
        s += "    n. of stems: " + str(len(self.stems))  + "\n"
        # you will likely want another line for your custom text-feature!
        return s

    def makeWords(self,s):
        """Makes a dictionary of cleaned words"""
        dic = {}
        cleanS = self.cleanString(s)
        cleanS = cleanS.split()    
        x = 1
        for i in cleanS:
            if i not in dic:
                dic[i] = 1
            else:     
                dic[i] += 1
        self.words = dic

    def cleanString(self,s):
        """This method takes in an input string s and returns it without and 
        punctuation or upper case letters"""
        s = s.lower()
        i = 0
        while (i < len (s)):
            x= s[i:i+1]
            #if x in ".,<>&^%$%^%$":
            if (x == "!" or x == "?" or x == "." or x == ":" or x == ";" or x == "," or x == "'" or x == "-" or x == "_" or x == "(" or x == ")" or x == "[" or x == "]" or x == "{" or x == "}" or x == "|"""):
                s = s[:i] + s[i+1:]
            else:
                i+=1   
        return s


    def readTextFromFile(self, filename):
        """This functions reads the text from a file and saves it as a string"""
        f = open(filename)
        textfromfile = f.read()
        return str(textfromfile)

    def printAllDictionaries(self):
        """This function formats and prints all the dictionaries"""
        print("The text model named [ "  + self.name + " ] has dictionaries:")
        print("self.sentencelengths:", end=" ")
        print(self.sentencelengths)
        print("self.words:", end=" ")
        print(self.words)
        print("self.wordlengths:", end=" ")
        print(self.wordlengths)
        print("self.stems:", end=" ")
        print(self.stems)
        print("self.punct:", end=" ")
        print(self.punct)

    def makeSentenceLengths(self,s):
        """This function creates a dictionary with all the sentence lengths"""
        d = {}
        i = 0
        while i < len(s): 
            x= s[i:i+1]
            if (x == "!" or x == "?" or x == "."):
                str1 = self.countWords(s[:i])
                s = s[i+2:]
                i = 0
                pw = str1
                if(pw not in d):
                    d[pw] = 1
                else:
                    d[pw] += 1
            else: i+=1
        self.sentencelengths = d

    def countWords(self, s):
        """This function counts the amount of words in a given string"""
        i = 1
        for j in range (len(s)):
            if s[j:j+1] == " ":
                i+=1
        return i

    def makeWordLengths(self,s):
        """This function creates a dictionary with all the puntuation"""
        d = {}
        s = self.cleanString(s)
        i = 0
        while i < len(s):
            x= s[i:i+1]
            if (x in " \n\r"):
                str1 = len(s[:i])
                s = s[i+1:]
                i = 0
                pw = str1
                
                if(pw not in d):
                    d[pw] = 1
                else:
                    d[pw] += 1
            elif (x != " " and i+1 == len(s)):
                str1 = len(s[:i+1])
                s = s[i+1:]
                i = 0
                pw = str1
                
                if(pw not in d):
                    d[pw] = 1
                else:
                    d[pw] += 1
            else:
                i+=1
        self.wordlengths = d

    def makePunctuation(self, s):
        """This function creates a dictionary with all the puntuation"""
        d = {}
        i = 0
        while i < len(s):
            x= s[i:i+1]
            if (x == "!" or x == "?" or x == "." or x == ":" or x == ";" or x == "," or x == "'" or x == "-" or x == "_" or x == "(" or x == ")" or x == "[" or x == "]" or x == "{" or x == "}" or x == "|"""):
                s = s[i+1:]
                i = 0
                pw = x
                if(pw not in d):
                    d[pw] = 1
                else:
                    d[pw] += 1
            else:
                i+=1
        self.punct = d
    
    def makeStems(self, s):
        """This function creates a dictionary with all the word stems"""
        cleaned_str = self.cleanString(s)
        cleaned_str = cleaned_str.split()
        new_Str = ""
        for i in cleaned_str:
            string = str(create_stem(i)) + " "
            new_Str += string
        new_Str = new_Str[:-1]
        i = 0
        d = {}
        while i < len(new_Str):
            if new_Str[i] in "\n\r":
                string = new_Str[:i]
                new_Str = new_Str[i+1:]
                i = 0
                if string not in d:
                    d[string] = 1
                else:
                    d[string] += 1
            elif new_Str[i] == " " or i+1 == len(new_Str):
                string = new_Str[:i+1]
                new_Str = new_Str[i+1:]
                i = 0
                if string not in d:
                    d[string] = 1
                else:
                    d[string] += 1
            else:
                i += 1
        self.stems = d

    def normalizeDictionary(self, d):
        """Should take a dictionary d and normalize it so all the values are out of one"""
        nd = d.copy()
        sum = 0
        for k in d:
            sum += d[k]
        for i in d:
            nd[i] = (d[i])/sum     
        return nd
       
    def smallestValue(self, nd1, nd2):
        """Should take in inputs from normalized dictionary and return the smallest of the values"""
        a = list(nd1.values())
        b = list(nd2.values())
        a_min = min(a)
        b_min = min(b)
        if a_min > b_min:
            return b_min
        return a_min

    def compareDictionaries(self, d, nd1, nd2):
        """This function returns the probability that each dictionary arose from the same source"""
        epsilon = self.smallestValue(nd1,nd2)/2
        prob1 = 0
        prob2 = 0
        nd1k = nd1.keys()
        nd2k = nd2.keys()
        for i in d.keys():
            if i not in nd1k:
                prob1 += d[i] *math.log( epsilon )
            else:
                prob1 += d[i] *math.log(nd1[i])
            if i not in nd2k:
                prob2 += d[i] *math.log( epsilon )
            else:
                prob2 += d[i] *math.log(nd2[i])
        prob1 = '{0:.4g}'.format(prob1)
        prob2 = '{0:.4g}'.format(prob2)
        return "[" + str(prob1) + "      " + str(prob2) + "]"
    
    def createAllDictionaries(self, s): 
        """ should create out all five of self's 
            dictionaries in full - for testing and 
            checking how they are working...
        """
        self.makeSentenceLengths(s)
        new_s = self.cleanString(s)
        self.makeWords(new_s)
        self.makeStems(new_s)
        self.makePunctuation(s)
        self.makeWordLengths(new_s)
    
    def compareTextWithTwoModels(self, model1, model2):
        """This function will completely compare three texts with each other"""
        word1 = self.normalizeDictionary(model1.words)
        word2 = self.normalizeDictionary(model2.words)
        wordL1 = self.normalizeDictionary(model1.wordlengths)
        wordL2 = self.normalizeDictionary(model2.wordlengths)
        sL1 = self.normalizeDictionary(model1.sentencelengths)
        sL2 = self.normalizeDictionary(model2.sentencelengths)
        st1 = self.normalizeDictionary(model1.stems)
        st2 = self.normalizeDictionary(model2.stems)
        pun1 = self.normalizeDictionary(model1.punct)
        pun2 = self.normalizeDictionary(model2.punct)
        print("                 name           vsTM1        vsTM2")
        print("                 ----           -----        -----")
        print("                words          " + self.compareDictionaries(self.words,word1,word2))
        print("          wordlengths          " + self.compareDictionaries(self.wordlengths,wordL1,wordL2))
        print("      sentencelenghts          " + self.compareDictionaries(self.sentencelengths,sL1,sL2))
        print("                stems          " + self.compareDictionaries(self.stems,st1,st2))
        print("          punctuation          " + self.compareDictionaries(self.punct,pun1,pun2))   
        countm1 = 0
        countm2 = 0

        if (float(self.compareDictionaries(self.words,word1,word2).split("      ")[0][1:]) > float(self.compareDictionaries(self.words,word1,word2).split("      ")[1][:-1])):
            countm1 += 1
        if (float(self.compareDictionaries(self.wordlengths,wordL1,wordL2).split("      ")[0][1:]) > float(self.compareDictionaries(self.wordlengths,wordL1,wordL2).split("      ")[1][:-1])):
            countm1 += 1
        if (float(self.compareDictionaries(self.sentencelengths,sL1,sL2).split("      ")[0][1:]) > float(self.compareDictionaries(self.sentencelengths,sL1,sL2).split("      ")[1][:-1])):
            countm1 += 1
        if (float(self.compareDictionaries(self.stems,st1,st2).split("      ")[0][1:]) > float(self.compareDictionaries(self.stems,st1,st2).split("      ")[1][:-1])):
            countm1 += 1
        if (float(self.compareDictionaries(self.punct,pun1,pun2).split("      ")[0][1:]) > float(self.compareDictionaries(self.punct,pun1,pun2).split("      ")[1][:-1])):
            countm1 += 1
        countm2 = 5 - countm1
        print("-->  Model1 wins on " + str(countm1) + " features.")
        print("-->  Model2 wins on " + str(countm2) + " features.")
        print("\n")
        if countm1 > countm2:
            print("+++++        Model1 is the better match!         +++++")
        else:
            print("+++++        Model2 is the better match!         +++++")


