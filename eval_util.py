# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Provides functions to help with evaluating models."""
import datetime
import numpy as np
import tensorflow as tf

from tensorflow.python.platform import gfile
   
def levenshtein(source, target):
    if len(source) < len(target):
        return levenshtein(target, source)

    # So now we have len(source) >= len(target).
    if len(target) == 0:
        return len(source)

    # We call tuple() to force strings to be used as sequences
    # ('c', 'a', 't', 's') - numpy uses them as values by default.
    source = np.array(tuple(source))
    target = np.array(tuple(target))

    # We use a dynamic programming algorithm, but with the
    # added optimization that we only need the last two rows
    # of the matrix.
    previous_row = np.arange(target.size + 1)
    for s in source:
        # Insertion (target grows longer than source):
        current_row = previous_row + 1

        # Substitution or matching:
        # Target and source items are aligned, and either
        # are different (cost of 1), or are the same (cost of 0).
        current_row[1:] = np.minimum(
                current_row[1:],
                np.add(previous_row[:-1], target != s))

        # Deletion (target grows shorter than source):
        current_row[1:] = np.minimum(
                current_row[1:],
                current_row[0:-1] + 1)

        previous_row = current_row

    return previous_row[-1]

def read_vocab(path):#'vocabulary.txt'
    if not tf.gfile.Exists(path):
        print('no file!')
        return []
    f = tf.gfile.GFile(path)
    s=  str(f.readline())
    l = []
    while s:
        l.append( [int(i) for i in s.split()])
        s=  str(f.readline())
    #print (l)
    return l

def getIndex(c,voc):
    for name, age in voc.iteritems():
        if age == c:
            return name
    print("-"*30,"error-",c)
    return None

def get_characters():
    vocabulary = {}
    nrC=1
    vocabulary['%%'] = 0 
    '''
    c = '0'
    
    while ord(c) != ord('9')+1:
        vocabulary[c] = nrC
        nrC = nrC + 1
        c = chr(ord(c)+1)
    c = 'A'
    while ord(c) != ord('Z')+1:
        vocabulary[c] = nrC
        nrC = nrC + 1
        c = chr(ord(c)+1)
    '''
    c = 'a'
    while ord(c) != ord('z')+1:
        vocabulary[c] = nrC
        nrC = nrC + 1
        c = chr(ord(c)+1)
    '''
    cr = [',','.','"','\'',' ','-','#','(',')',';','?',':','*','&','!','/','']
    for c in cr:
        vocabulary[c] = nrC
        nrC = nrC + 1
    '''
    vocabulary[' '] = nrC
    nrC += 1
    vocabulary[''] = nrC
    return vocabulary

def show_prediction(dec, label, top_k=3):
    voc = get_characters()
    for i,word in enumerate(label[:top_k]):
        print('cor:',[getIndex(j,voc) for j in word if j])
        for guess_batch in dec:
            print('pred',[getIndex(j,voc) for j in guess_batch[i] if j])
        print('-'*10)

def calculate_models_error_withLanguageModel(decodedPr, labels_val, vocabulary,top_k):
    if len(vocabulary) == 0:
        return -1
    voc_guess = np.zeros(len(decodedPr[0]),dtype=np.int32)
    for guess_batch in decodedPr:
        for k,guess in enumerate(guess_batch):
            mini = 1000
            for i,word in enumerate(vocabulary):
                ed = levenshtein(word,guess)
                if ed<mini:
                    mini = ed
                    voc_guess[k] = i
    err = 0.0
    newGuess = []
    for k,truth in  enumerate(labels_val):
        newGuess.append(vocabulary[voc_guess[k]])
        err += levenshtein(truth, vocabulary[voc_guess[k]])/float(len(truth))
    err /= len(labels_val)  
    return err, newGuess