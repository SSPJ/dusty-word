#!/usr/bin/env python3.6

#########/
# word searches thesaruses and reverse dictionaries with human-readable queries
# Copyright (C) 2018  Seamus Johnston https://seamusjohnston.com
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#########\

# get code from other libraries that we'll need
import sys, re, requests
from subprocess import call
from colorama import init as colorama_init
# re is a library for regular expressions
# sys(tem) is a library for interacting with the computer "outside" the program
# requests is an HTTP library for talking to websites on the internet
# subprocess is a library for running other programs (any programs, not just python)
# colorama is a library for displaying ANCI escape codes correctly on Windows
# notice that in some cases we import the entire library (import _libraryname_)
# and in others we import only a function or two (from _libraryname_ import _function_)
# in colorama we even rename the function (because init() is too vague, imo)

#### CONSTANTS
# Here we declare global contants that will be used throughout the program
# They are in UPPERCASE by convention (unlike some languages, you can't make
# constants immutable in python -- in C++ for example, we'd do const MY_VAR = 5
# and the const keyword would forbid MY_VAR from ever being changed later)

# putting this string in triple quotes means I can put line breaks in it
USAGE = """
Usage: word [options] [primary modifiers] <word|phrase>
       [primary|secondary modifiers <word|phrase|number>]

Commandline interface to Datamuse and Owlbot APIs

    -v[vv]                           verbose modes.
    -h, --help                       Print this help.

Primary modifier examples:
   meaning          "word meaning feeling tired"
   sounds like      "word which sounds like tung"
                    "word sounding like doe but spelled differently"
   rhymes with      "word rhymes with culminate"
   comes after      "word comes after sea and that rhymes with norse"
   spelled like     "word spelled like 'cens?r'"
   defined          "word nostrum defined" 
   pronunciation    "word pronunciation of otolaryngology"

Secondary modifiers:
   max              "word like beautiful max 7"         (default is 20)
   about            "word meaning refuse about trash"   (max is 5 nouns)
                    "word meaning refuse about negotiation contracts"

word tries to guess your intent. If it messes up, use quotes.
                    word meaning of life              == ml=of+life
                    word "meaning of life"            == ml=meaning+of+life
Optionally, read <<CONTRIBUTING.md>> and open an issue,
so I can fix it for the next person.
"""

# Variables for creating the API request
# API means application programming interface
# (basically, websites made for computers to read, not humans)
MAXIMUM = "20"
GLOSS = { "ml": "have a meaning like",
          "sl": "sound like",
          "sp": "are spelled like",
          "rel_jja": "is a noun describing the adjective",
          "rel_jjb": "is an adjective describing the noun",
          "rel_syn": "are synonyms of",
          "rel_trg": "are triggered by",
          "rel_ant": "are antonyms of",
          "rel_spc": "are a more general word for",
          "rel_gen": "are a specific kind of",
          "rel_com": "are the parts of",
          "rel_par": "describe things made with",
          "rel_bga": "usually follow",
          "rel_bgb": "usually preceed",
          "rel_rhy": "are perfect rhymes of",
          "rel_nry": "are approximate rhymes of",
          "rel_hom": "are homophones of",
          "rel_cns": "have the same consonants as",
          "lc": "often follow",
          "rc": "often come before",
          "topics": "are about" }

# in RESTful APIs, data is exchanged via http using a limited number of "verbs"
# you are familiar with GET from sites like youtube:
# https://www.youtube.com/watch?v=yO3MwSbs8&list=WIL&index=89 is a GET request
# v, list, and index are parameters, while yO3MwSbs8, WIL, and 89 are values

# GLOSS is a matching dictionary of parameters and what those parameters mean

#
#### END CONSTANTS

#### HELPER FUNCTIONS
#

def is_rhymes(word):
  """ Rhymes is hard to spell :3 """
  rhymes = ["rhymes", "rhytms", "rhytems", "ryhms", "rhyms", "rhymnes", "ryhmes", "rhimes", \
            "rymes", "rhtyms", "ryhtyms", "rhyemes", "rhymmes", "rymhs", "rhmes", "rhyms", \
            "rhyhms", "rhytams", "ryphmes"]
  # go through the list of mispellings, one at a time
  for r in rhymes:
    # if we get a match, return true
    # (lower() converts word to lowercase)
    if word.lower() == r:
      return True
  # if nothing matches, return false
  return False
  # the point of returning true or false from a function is that
  # we can use this function later inside an "if" statement

def is_pronounced(word):
  """ Pronounced is also hard to spell """
  pronounced = ["pronounced", "pronunciation", "pronounsed", "pronouced", "pronouned", \
                "pronounciated", "prenounced", "prounouced", "pernounced", "purnounced", \
                "pronoused", "pronuced", "pronunced", "pronnounced", "pronanced", \
                "prononced", "prounounced", "prononsed", "prononuced", "pernunciation", \
                "prononciation", "prounciation", "pronouciation", "pronounciated", \
                "pronounciation", "pronanciation", "prononcation", "pernounciation", \
                "prononceation", "prenunciation", "prononseation", "prounouciation", \
                "pronuniation", "pronunication", "prenounciation", "pronuntiation", \
                "pronuncition", "pronociation", "prenunsiation", "pronounsation", \
                "pronounceation", "pronounication", "pronauciation", "pronounciacion", \
                "pronounsiation"]
  for p in pronounced:
    if word.lower() == p:
      return True
  return False

def convert_num(num):
  """ Let's let the user enter alphabetical numbers to set the max results they want """
  # create a dictionary mapping alphabetical to numeric
  nums = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, \
          "seven": 7, "eight": 8, "nine": 9, "ten": 10}
  # if user's number is less than ten
  if num in nums:
    # set user's max to the number stored in the dictionary
    # (i.e. if num is "five", nums[num] will be 5)
    return str(nums[num])
  # otherwise, let's assume they entered a numeric string (like "15")
  else:
    try:
      # we convert it to an int before turning it back into a str just to make sure
      # it really is a number -- if it's not, python will raise a ValueError
      return str(int(num))
    # if they entered something silly like "max elephants"
    except ValueError:
      # set user's max to be nothing, i.e. false
      return None

def parse(args, query):
  """ Parse the commandline args into a dictionary data structure. """

  global query_type

  # Deal first with requests for definition or pronunciation
  # 1. Make the code easier to read
  first_word = args[0]
  second_word = args[1] if len(args) > 1 else ""
  third_word = args[2] if len(args) > 2 else ""
  fourth_word = args[3] if len(args) > 3 else ""
  # we use the teranary operator (this if ____ else that) to avoid an IndexError
  # IndexError would be raised if we tried to access the second element (args[1])
  # in a list which contained only one item (eg args == ["lonely"])
  # the teranary operator (in most languages it looks like "____ ? this : that")
  # returns "this" when the if is true and "that" when the if is false
  # meaning, if len(args) is NOT greater than 1, second_word == ""

  # 2. Check for keywords in the list of arguments
  # Example: nostrum defined
  # Example: pronunciation of otolaryngology
  if first_word == "define":
    # e.g. if the first word is "define" we'll add the second word to the query
    query = {"sp": second_word, "md": "d", "max": "1", "qe": "sp", "ipa": "1"}
    # the query is a dictionary of GET parameters for the http request, eg
    # https://api.datamuse.com/words?max=1&sp=SECOND_WORD_HERE&qe=sp&md=d&ipa=1
  elif second_word == "defined" or second_word == "definition":
    query = {"sp": first_word, "md": "d", "max": "1", "qe": "sp", "ipa": "1"}
  # this one uses string interpolation (the f"" stuff)
  elif f"{second_word} {third_word}" == "means what":
    query = {"sp": first_word, "md": "d", "max": "1", "qe": "sp", "ipa": "1"}
  elif f"{second_word} {third_word} {fourth_word}" == "is said how":
    query = {"sp": first_word, "md": "r", "max": "1", "qe": "sp", "ipa": "1"}
  # this one uses regular expressions -- i.e. if the second_word is "of" or "for"
  elif first_word == "definition" and re.match(r'(of)|(for)',second_word):
    query = {"sp": third_word, "md": "d", "max": "1", "qe": "sp", "ipa": "1"}
  # the is_pronounced function returns true if first_word is a (mis)spelling of pronounced
  elif re.match(r'(of)|(for)',second_word) and is_pronounced(first_word):
    query = {"sp": third_word, "md": "r", "max": "1", "qe": "sp", "ipa": "1"}
  # the ordering in the above list is not entirely random
  # since an if-elif-else statement won't keep evaluating after it finds a match
  # it makes sense to put the most computationally complex clauses at the end
  # >>> import timeit
  # >>> timeit.timeit('from word_helpers import is_pronounced; is_pronounced("pronounced")', number=10000)
  # 0.022870146989589557
  # >>> timeit.timeit('args = ["defined"]; args[0] == "defined"', number=10000)
  # 0.002359684993280098
  # it takes 2 milliseconds to compare a string in a list 10,000 times
  # -- versus 2 centiseconds to run is_pronounced 10,000 times
  # (on my Intel Core i5 2.67GHz CPU -- obviously speed depends on the processor)
  # it's also worth noting that readability counts more than speed optimization (most of the time!)

  # Quick way to check if any of the above if statements matched
  if "sp" in query:
    # if so, we are done in this function
    if query["md"] == "r": query_type = "PRO"
    if query["md"] == "d": query_type = "DEF"
    return query

  # these will be useful later
  STOP_WORDS = ("and", "meaning", "means", "max", "about", "which", "that")

  # Parse more complicated requests for synonyms, etc
  # 0 is false in python, so this loop will run until we've removed all the args
  while len(args):
    # we must reset these vars each time the loop starts
    # in case we've deleted items from the args list
    first_word = args[0]
    second_word = args[1] if len(args) > 1 else ""
    third_word = args[2] if len(args) > 2 else ""
    # we use the teranary operator (this if ____ else that) to avoid an IndexError
    # IndexError would be raised if we tried to access the second element (args[1])
    # in a list which contained only one item (eg args == ["lonely"])
    # the teranary operator (in most languages it looks like "____ ? this : that")
    # returns "this" when the if is true and "that" when the if is false
    # meaning, if len(args) is NOT greater than 1, second_word == ""

    # Disambiguate homonym requests from spelling correction requests
    # Example: sounding like tung
    # Example: sounds like doe but spelled differently
    if re.match(r'sound((s)|(ing)) like',f"{first_word} {second_word}"):

      # again, use len(args) to avoid an IndexError
      if len(args) >= 6 and \
         re.match(r'((but)|(except)) spelled different(ly)?',f"{args[3]} {args[4]} {args[5]}"):
        # but instead of teranary operator,
        # use "short circuit logic" -- when python sees "if __A__ and __B__ ",
        # it knows that if A is false, the whole thing will be false
        # (you can't have "ice cream and potatoes" for dinner if you don't have ice cream)
        # and it won't waste time evaluating B, so re.match won't run and args[4]
        # won't be accessed and no IndexError will be raised, yay!
        # regex explained: ? means the prior thing matched zero or one times
        #                    different(ly)? matches "different" and "differently"
        query["rel_hom"] = third_word
        # now, delete 6 items from args, starting at item 0
        del args[0:6]
      else:
        query["sl"] = third_word
        del args[0:3]

    # Example: spelled like 'cens?r'
    elif re.match(r'spell((ed)|(ing)) like',f"{first_word} {second_word}"):
      # two stars (**) means "unpack" a dictionary
      # just like unpacking a suitcase, we've dumped the old contents of query
      # into a new dictionary (which we are saving with the same variable name!)
      query = {**query,"sp": third_word}
      # query["sp"] = third_word also works fine
      # just showing off how to combine two dictionaries :)
      del args[0:3]

    # Example: rhymes with culminate
    elif len(args) > 2 and second_word == "with" and is_rhymes(first_word):
      query["rel_rhy"] = third_word
      del args[0:3]

    # Example: almost rhymes with culminate
    elif len(args) > 3 and \
         f"{first_word} {third_word}" == "almost with" and \
         is_rhymes(second_word):
      query["rel_nry"] = args[3] # fourth_word
      del args[0:4]

    # Example: comes after sea
    elif f"{first_word} {second_word}" == "comes after":
      query["lc"] = third_word
      del args[0:3]
    elif first_word == "follows":
      query["lc"] = second_word
      del args[0:2]
    elif f"{first_word} {second_word}" == "comes before":
      query["rc"] = third_word
      del args[0:3]
    elif first_word == "preceeds":
      query["rc"] = second_word
      del args[0:2]

    # Example: describes paint
    elif first_word == "describes":
      query["rel_jjb"] = second_word
      del args[0:2]

    # Example: associated with feet
    elif f"{first_word} {second_word}" == "associated with" or \
         f"{first_word} {second_word}" == "triggered by":
      query["rel_trg"] = third_word
      del args[0:3]

    # Example: meaning feeling tired
    elif first_word in ["means","meaning","like"]:
      # get rid of first_word
      del args[0]
      # now short circuit logic again, plus using the tuple from ealier
      # b/c if we have "meaning deer and sounds like roe" we don't want
      # query["ml"] == "deer and sounds like roe" -- it should be just "deer"
      while len(args) and args[0] not in STOP_WORDS:
        # teranary operator prevents KeyError if "ml" not already in query dictionary
        query["ml"] = f"{query['ml']} {args[0]}" if "ml" in query else args[0]
        del args[0]
    # an example with the previous code to make things clearer
    # say args == ["means", "egg", "beater", "and", "max", "35"]
    # first_word IS in ["means","meaning","like"]
    # del first_word, args is now ["egg", "beater", "and", "max", "35"]
    # len(args) == 5, args[0] is NOT in STOP_WORDS
    # "ml" is NOT in query, so teranary returns args[0] ("egg")
    # args[0] is copied to query["ml"] (query is now {ml: "egg"})
    # del args[0], args is now ["beater", "and", "max", "35"]
      # return to top of while loop, len(args) == 4, args[0] is NOT in STOP_WORDS
      # "ml" IS in query, so teranary returns f"{query['ml']} {args[0]}" ("egg beater") 
      # f"{query['ml']} {args[0]}" is copied to query["ml"]
      # (query is now {ml: "egg beater"})
      # del args[0], args is now ["and", "max", "35"]
        # return to top of while loop, len(args) == 3,
        # args[0] IS in STOP_WORDS (args[0] == "and")
        # DO NOT enter the while loop, continue past this code block

    # Discover the topic of our query
    elif first_word == "about":
      del args[0]
      count = 0
      # Datamuse allows a max of five topic words
      while len(args) and args[0] not in STOP_WORDS and count <= 5:
        query["topics"] = f"{query['topics']} {args[0]}" if "topics" in query else args[0]
        del args[0]
        # count += 1 is the same as count = count + 1
        count += 1

    # How many results to return (max 1000)
    elif first_word in ["max", "maximum", "only"]:
      user_max = convert_num(second_word)
      if user_max and int(user_max) <= 1000:
        query["max"] = user_max
      del args[0:2]

    # Remove filler words if they weren't parsed out above
    elif first_word in ["that","which","and","like","is"]:
      del args[0]

    # Add anything not otherwise parsable to the ml parameter
    else:
      query["ml"] = f"{query['ml']} {first_word}" if "ml" in query else first_word
      del args[0]

    # this is the bottom of that massive while loop
    # if args is not empty by now, we'll start over from the top ^

  return query
  # and this is the end of the "def parse(args, query)" function
  # whew!

def go_fetch(query):
  """ Turn the query dictionary into a real http request using the requests library! """
  responses = []
  explained = ""
  global query_type
  global verbose
  global GLOSS
  global MAXIMUM

  if   query_type == "PRO": explained = f"You asked for the pronunciation of '{query['sp']}'."
  elif query_type == "DEF": explained = f"You asked for the definition of '{query['sp']}'."
  else:
    # loop through the dictionary, one key at a time, and explain what each entry is for
    query_glossed = []
    for param in query:
      # if this one is max or md (metadata), skip it
      if param == "max" or param == "md": continue
      # it's not an accident that the keys in query are the same as the keys in GLOSS
      query_glossed.append(f"{GLOSS[param]} {query[param]}")
      # eg GLOSS has {"sp": "are spelled like"} and query has {"sp": "dear"}, then
      # explained[0] == f"{GLOSS['sp']} {query['sp']} == "are spelled like dear"
    explained = "You asked for words which " + " and ".join(query_glossed)

  # Let's set a default
  if "max" not in query: query["max"] = MAXIMUM

  # there's a TON of stuff going on in this line
  datamuse = requests.get('https://api.datamuse.com/words',params=query)
  # first, the requests library's get() function "urlencodes" the url and parameters
  # e.g. if query == {"ml": "ringing in the ears"}, it becomes "?ml=ringing+in+the+ears"
  # next, it opens an http connection to datamuse.com, something like:
  # *   Trying 54.225.209.164...
  # * Connected to api.datamuse.com (54.225.209.164) port 443 (#0)
  # then, it sends an http request which consists of a "header" and (optionally) a "body"
  # which looks something like this:
  #
  # GET https://api.datamuse.com/words?ml=ringing+in+the+ears
  # Connection: 'keep-alive'
  # Accept: */*
  # User-Agent: python-requests/2.18.4
  # Accept-Encoding: gzip, deflate
  # 
  # and the datamuse API sends back a response which looks something like:
  # HTTP/1.1 200 OK
  # Cache-Control: no-transform, max-age=86400
  # Content-Type: application/json
  # Date: Fri, 02 Feb 2018 02:53:45 GMT
  # Vary: Accept-Encoding
  # Content-Length: 4634
  # Connection: keep-alive
  #
  # [{"word":"tinnitus","score":51691,"tags":["syn","n"]},{"word":"ring",". . . 
  #
  # then the response is parsed into a python object
  # (sticks the headers in one variable, the body into another, etc)
  # and the object is returned from get() and we store it in "datamuse"
  # finally, we stick the response object into a list, like so:
  responses.append(datamuse)

  # If a definition is asked for, we'll use two APIs
  if query_type == "DEF":
    owlbot = requests.get(f"https://owlbot.info/api/v2/dictionary/{query['sp']}")
    responses.append(owlbot)

  # print out helpful info if the user asked for it
  if verbose: print(explained)  # Plain english description of our query

  return responses

def fortune_cookie():
  """ Give the user something nice if the query fails :) """
  r = requests.get('http://www.bsdfortune.com')
  # a regular expression in python can be "compiled"
  # which a) makes it a tiny bit faster (important if you are using the same one many times)
  # and b) gives access to some more advanced features, like re.MULTILINE
  # www.bsdfortune.com doesn't have an API, so this regex is for getting the fortune out
  # of the source code of a human-readable webpage
  rx = re.compile(r'http://www\.aasted\.org -->\n(.*)<br/> \n</p>\n<a href="./" rel="self" title="BSD Fortune">',re.MULTILINE|re.DOTALL)
  s = re.search(rx,r.text)
  # then use substitution to remove "<br/>" tags (substitution: replace with nothing, lol)
  # s.groups() returns the caputred groups in the regex above in a list
  # s.groups()[0] gets the first item in the list (in this case, the text of the fortune)
  quote = re.sub(r'<br/>','',s.groups()[0])
  return quote

def print_response(responses):
  """ Turn JSON formatted responses into nice printable output. """
  connection_error, empty_results = False, False

  global query_type
  global verbose

  for index, response in enumerate(responses):
    if response.status_code != requests.codes.OK:
      connection_error = True
      del responses[index]
    elif response.json() == []:
      empty_results = True
      del responses[index]

  colorama_init()

  if responses == [] and connection_error == True:
    print("\033[0;36mUnable to reach API.\033[0m Check your internet connection or try again with more feeling.")
    sys.exit(1)
  elif responses == [] and empty_results == True:
    try:
      fortune = call(['fortune','-s'])
    except FileNotFoundError:
      fortune = fortune_cookie()
    if fortune:
      print("\033[0;36mNo results found!\033[0m Have a fortune cookie:")
      print(fortune)
    else:
      print("\033[0;36mNo results found!\033[0m Try a paper dictionary instead?")
    sys.exit(1)

  if query_type == "DEF":
    for response in responses:
      # print out helpful info if the user asked for it
      if verbose > 1: print(response.url)     # What we asked the remote server
      if verbose > 2: print(response.text)    # The raw return JSON
      if re.search(r'datamuse',response.url):
        api = "datamuse"
        payload = response.json()[0]
        word = payload["word"]
        definition = '\n'.join(payload['defs'])
        lines = []
        for entry in payload['defs']:
          type,_def = re.match(r'([^\\]*)\t(.*)',entry).groups()
          line = f"{type.ljust(11)} {_def}"
          lines.append(line)
        definition = '\n'.join(lines)
      else:
        api = "owlbot"
        payload = response.json()
        word = re.search(r'dictionary/(.*)$',response.url).groups()[0]
        lines = []
        for entry in payload:
          line = f"{entry['type'].ljust(11)} {entry['definition']}"
          if entry['example']: line += f"\n{' ' * 12}Example:{entry['example']}"
          lines.append(line)
        definition = '\n'.join(lines)
      print(f"\033[0;36m{api}\033[0m says word \033[0;32m{word}\033[0m means")
      print(definition)
  if query_type == "PRO":
    # print out helpful info if the user asked for it
    if verbose > 1: print("The answer came from: ",responses[0].url)
    if verbose > 2: print("The raw JSON response was: ",responses[0].text)
    payload = responses[0].json()[0]
    word = payload["word"]
    for tag in payload['tags']:
      if   re.match(r'pron:',tag):
        pron = re.match(r'pron:(.*)',tag).groups()[0]
      elif re.match(r'ipa_pron:',tag):
        ipa = re.match(r'ipa_pron:(.*)',tag).groups()[0]
    pronunciation = f"\033[0;32m{pron}\033[0m (\033[0;32m{ipa}\033[0m)"
    print(f"\033[0;36mdatamuse\033[0m says word \033[0;32m{word}\033[0m is pronounced like {pronunciation}")
  else:
    # print out helpful info if the user asked for it
    if verbose > 1: print("The answer came from: ",responses[0].url)
    if verbose > 2: print("The raw JSON response was: ",responses[0].text)
    payload = responses[0].json()
    for entry in payload:
      entry['tags'] = ', '.join(entry['tags']) if 'tags' in entry else ''
    fentry = lambda entry: (f"\033[0;32m{entry['word'].rjust(13)}\033[0m "
                            f"\033[0;36m{str(entry['tags']).rjust(13)}\033[0m ")
    entries = list(map(fentry, payload))
    lines = (''.join(entries[i:i+3]) for i in range(0,len(entries),3))
    print("\033[0;36mdatamuse thinks these words may help!\033[0m".rjust(94))
    print('\n'.join(lines))

#
#### END HELPER FUNCTIONS

if __name__ == "__main__":

  # if there are no comandline arguments or if the first arg is help
  if len(sys.argv) == 1 or sys.argv[1] in ["-h","--help"]:
    # print instructions
    print(USAGE)
    # and exit the program
    sys.exit()
  # sys.argv is a list of stuff you typed to start the program
  # if you typed "word.py --help" you get sys.argv == ["word.py","--help"]

  # copy sys.argv starting with the second element (index 1)
  args = sys.argv[1:]

  # a flag to set if the user asks for definitions or pronuciation help
  query_type = None

  # verbose flag is off (set to zero/false) by default
  verbose = 0

  # Turn on verbose flag if asked (this will output helpful debugging info)
  # if first comandline arg starts with a dash followed by 1, 2, or 3 v's
  if re.match(r"-(?:v){1,3}\b",args[0]):
    # set verbose to the number of v's (minus 1 for the dash!)
    verbose = len(args[0]) - 1
    # get rid of the flag from the list, so we don't re-read it later
    args.pop(0)
  # regex explained: -(?:v){1,3}\b
  #   -     literal dash
  #   (?:)  a NON capturing group (will make more sense later)
  #   v     literal letter v
  #   {1,3} the prior group, found once, twice, or thrice (in a row)
  #   \b    word boundary (so we match "-v" or "-vvv" not "-vvvabc")

  # here's the "heart" of the program <3
  # 1. turn the user input into a usable web address
  query = parse(args, {})
  # 2. go get data from that web address
  responses = go_fetch(query)
  # 3. print out the response we got back from the internet
  print_response(responses)
