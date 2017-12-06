#!/usr/bin/env bats

@test "test prints usage" {
  run word
  [ "$status" -eq 0 ]
  [ "${lines[0]}" = 'Usage: word [options] [primary modifiers] <word|phrase> \' ]
}
