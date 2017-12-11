#!/usr/bin/env bats

@test "test prints usage" {
  run word
  [ "$status" -eq 0 ]
  [ "${lines[0]}" = 'Usage: word [options] [primary modifiers] <word|phrase> \' ]
}

# At a high level, I want the app to perform these functions
# A. Given a word
# -- tell me what word I'm trying to spell
# -- tell me what a word means
# -- tell me how to say a word
# B. Given a word or a phrase
# -- tell me words that are like it

