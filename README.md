**Dusty Word**

### Purpose

Allows you to ask your computer dictionary and thesarus questions in fairly natural English. Uses the [Datamuse](http://www.datamuse.com/) and [Owlbot](https://owlbot.info/api/v2/dictionary/owl) APIs. See the usage section for more.

```
$ word which sounds like new
                      datamuse thinks these words may help!
           new           knew             nu            gnu
           nue            noo            nou           neww
          niue           neuk            nnu            nuw
          gnaw            gne            gna           gnow
           gno           gnau            gni            gny
```

### Installation and Dependencies

**Linux/Mac**

Download the word script and make it executable `chmod u+x word`.

Run `./word -h`.

You can also use the python version as described for Windows. Comment out these lines if you don't want to install the colorama library:

* `from colorama import init as colorama_init`
* `colorama_init()`

**Windows**

You'll need
* Python 3.6+
* sys, re, requests, subprocess libraries
* colorama library (Windows)
* pytest (if you want to run the test suite)

Download the word.py file. Open command prompt and navigate to the place you saved it (for example `cd C:\\Users\myname\Downloads`). If you haven't installed them already, install the libraries:

    > python -m pip3 install requests
    > python -m pip3 install colorama

If you get an error about python not being found, make sure you did install it first. If you did, search the web for "windows python path".

Launch the program by running:

    > word.py --help

### Usage
```
Usage: word [options] [primary modifiers] <word|phrase>
       [primary|secondary modifiers <word|phrase|number>]

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
```

### Extra Notes

At some point I might re-implement this using nltk. For now, the grammar is fairly strict.

Other similar projects (which I haven't tried):

[drawnepicenter/leximaven](drawnepicenter/leximaven) (requires node.js)

[margaret/python-datamuse](margaret/python-datamuse) (for use directly in python programs)