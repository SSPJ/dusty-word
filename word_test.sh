#!/usr/bin/env bats

@test "test prints usage" {
  run word
  [ "$status" -eq 1 ]
  [ "${lines[0]}" = 'Usage: word [options] [primary modifiers] <word|phrase> \' ]
}

# At a high level, I want the app to perform these functions
# A. Given a word
# -- tell me what word I'm trying to spell
# -- tell me what a word means
# -- tell me how to say a word
# B. Given a word or a phrase
# -- tell me words that are like it

# These paramaters exist in the datamuse API but haven't been implemnted yet in the code:
# "rel_jja" "rel_jjb" "rel_syn" "rel_trg" "rel_ant" "rel_spc" "rel_gen" "rel_com" "rel_par" "rel_bga" "rel_bgb" "rel_nry" "rel_cns"

@test "simple query should encode correctly" {
  run word -x platypus
  [ "$status" -eq 0 ]
  [ "${lines[1]}" = 'I ran curl -sG "https://api.datamuse.com/words?max=20&ml=platypus"' ]
}
@test "multiple words should encode correctly" {
  run word -x elephant trunk
  [ "$status" -eq 0 ]
  [ "${lines[1]}" = 'I ran curl -sG "https://api.datamuse.com/words?max=20&ml=elephant%20trunk"' ]
}
@test "max should be setable" {
  run word -x elephant trunk and max six
  [ "$status" -eq 0 ]
  [ "${lines[1]}" = 'I ran curl -sG "https://api.datamuse.com/words?max=6&ml=elephant%20trunk"' ]
}
@test "order should not change the query" {
  run word -x max six elephant trunk
  [ "$status" -eq 0 ]
  [ "${lines[1]}" = 'I ran curl -sG "https://api.datamuse.com/words?max=6&ml=elephant%20trunk"' ]
}
@test "quotes should protect modifier words as literal" {
  run word -x "meaning of life"
  [ "$status" -eq 0 ]
  [ "${lines[1]}" = 'I ran curl -sG "https://api.datamuse.com/words?max=20&ml=meaning%20of%20life"' ]
}
@test "'meaning' should collect other modifiers" {
  run word -x meaning pride comes before a fall
  [ "$status" -eq 0 ]
  [ "${lines[1]}" = 'I ran curl -sG "https://api.datamuse.com/words?max=20&ml=pride%20comes%20before%20a%20fall"' ]
}
@test "'meaning' should collect until stop word" {
  run word -x meaning art without meaning and max ten
  [ "$status" -eq 0 ]
  [ "${lines[1]}" = 'I ran curl -sG "https://api.datamuse.com/words?max=10&ml=art%20without"' ]
}
@test "'sounds like' should use sl paramater" {
  run word -x which sounds like tung
  [ "$status" -eq 0 ]
  [ "${lines[1]}" = 'I ran curl -sG "https://api.datamuse.com/words?max=20&sl=tung"' ]
}
@test "'but spelled different' should use rel_hom parameter" {
  run word -x sounding like doe but spelled different
  [ "$status" -eq 0 ]
  [ "${lines[1]}" = 'I ran curl -sG "https://api.datamuse.com/words?max=20&rel_hom=doe"' ]
}
@test "topic should be setable" {
  run word -x which means laps and is about running
  [ "$status" -eq 0 ]
  [ "${lines[1]}" = 'I ran curl -sG "https://api.datamuse.com/words?max=20&ml=laps&topics=running"' ]
}
@test "'spelled like' should use sp parameter" {
  run word -x spelled like platapus
  [ "$status" -eq 0 ]
  [ "${lines[1]}" = 'I ran curl -sG "https://api.datamuse.com/words?max=20&sp=platapus"' ]
}
@test "sp and ml should be combinable" {
  run word -x animal and spelled like platapus
  [ "$status" -eq 0 ]
  [ "${lines[1]}" = 'I ran curl -sG "https://api.datamuse.com/words?max=20&ml=animal&sp=platapus"' ]
}
@test "'ryhmes with' should use rel_rhy even when spelled wrong" {
  run word -x ryhmes with cute
  [ "$status" -eq 0 ]
  [ "${lines[1]}" = 'I ran curl -sG "https://api.datamuse.com/words?max=20&rel_rhy=cute"' ]
}
@test "'comes before' should use rc" {
  run word -x ryhmes with cute and comes before bowl
  [ "$status" -eq 0 ]
  [ "${lines[1]}" = 'I ran curl -sG "https://api.datamuse.com/words?max=20&rel_rhy=cute&rc=bowl"' ]
}
@test "'comes after' should use lc" {
  run word -x ryhmes with cute and comes after leather
  [ "$status" -eq 0 ]
  [ "${lines[1]}" = 'I ran curl -sG "https://api.datamuse.com/words?max=20&rel_rhy=cute&lc=leather"' ]
}
@test "'definition of' should use owlbot" {
  run word -x definition of nostrum
  [ "$status" -eq 0 ]
  [ "${lines[1]}" = 'I ran curl -sG "https://owlbot.info/api/v2/dictionary/nostrum"' ]
}
@test "'pernounciation of' should use md=r even when spelled wrong" {
  run word -x pernounciation of nostrum
  [ "$status" -eq 0 ]
  [ "${lines[1]}" = 'I ran curl -sG "https://api.datamuse.com/words?max=1&sp=nostrum&qe=sp&md=r&ipa=1"' ]
}

