#!/usr/bin/env pytest

# GPLv3 Copyright (C) 2018 Seamus Johnston https://seamusjohnston.com

import pytest, requests, re
import word

# At a high level, I want the app to perform these functions
# A. Given a word
# -- tell me what word I'm trying to spell
# -- tell me what a word means
# -- tell me how to say a word
# B. Given a word or a phrase
# -- tell me words that are like it

# These paramaters exist in the datamuse API but haven't been implemnted yet in the code:
# "rel_jja" "rel_jjb" "rel_syn" "rel_trg" "rel_ant" "rel_spc" "rel_gen" "rel_com" "rel_par" "rel_bga" "rel_bgb" "rel_nry" "rel_cns"

class TestWord(object):

  @pytest.fixture(scope="function", autouse=True)
  def globalvars(self,monkeypatch):
    word.verbose = 0
    word.query_type = None
    monkeypatch.setattr(requests, 'get', TestWord.mockget)

  @staticmethod
  def mockget(*args,**kwargs):
    if "accessed" in locals():
      return response
    else:
      accessed = True
      response = requests.Response()
      response.request = requests.Request('GET',*args,**kwargs).prepare()
      response.url = response.request.url
      return response

  def test_simple_query_should_encode_correctly(self):
    args = ['platypus']
    query = word.parse(args, {})
    responses = word.go_fetch(query)
    assert re.search(r'max=20',responses[0].url)
    assert re.search(r'ml=platypus',responses[0].url)

  def test_multiple_words_should_encode_correctly(self):
    args = ['elephant', 'trunk']
    query = word.parse(args, {})
    responses = word.go_fetch(query)
    assert re.search(r'ml=elephant\+trunk',responses[0].url)
  
  def test_max_should_be_setable(self):
    args = ['elephant', 'trunk', 'and', 'max', 'six']
    query = word.parse(args, {})
    responses = word.go_fetch(query)
    assert re.search(r'max=6',responses[0].url)
    assert re.search(r'ml=elephant\+trunk',responses[0].url)
  
  def test_order_should_not_change_the_query(self):
    args = ['max', 'six', 'elephant', 'trunk']
    query = word.parse(args, {})
    responses = word.go_fetch(query)
    assert re.search(r'max=6',responses[0].url)
    assert re.search(r'ml=elephant\+trunk',responses[0].url)
  
  def test_quotes_should_protect_modifier_words_as_literal(self):
    args = ['meaning of life']
    query = word.parse(args, {})
    responses = word.go_fetch(query)
    assert re.search(r'ml=meaning\+of\+life',responses[0].url)
  
  def test_meaning_should_collect_other_modifiers(self):
    args = ['meaning', 'pride', 'comes', 'before', 'a', 'fall']
    query = word.parse(args, {})
    responses = word.go_fetch(query)
    assert re.search(r'ml=pride\+comes\+before\+a\+fall',responses[0].url)
  
  def test_meaning_should_collect_until_stop_word(self):
    args = ['meaning', 'art', 'without', 'meaning', 'and', 'max', 'ten']
    query = word.parse(args, {})
    responses = word.go_fetch(query)
    assert re.search(r'max=10',responses[0].url)
    assert re.search(r'ml=art\+without',responses[0].url)
  
  def test_sounds_like_should_use_sl_paramater(self):
    args = ['which', 'sounds', 'like', 'tung']
    query = word.parse(args, {})
    responses = word.go_fetch(query)
    assert re.search(r'sl=tung',responses[0].url)
  
  def test_but_spelled_different_should_use_rel_hom_parameter(self):
    args = ['sounding', 'like', 'doe', 'but', 'spelled', 'different']
    query = word.parse(args, {})
    responses = word.go_fetch(query)
    assert re.search(r'rel_hom=doe',responses[0].url)
  
  def test_topic_should_be_setable(self):
    args = ['which', 'means', 'laps', 'and', 'is', 'about', 'running']
    query = word.parse(args, {})
    responses = word.go_fetch(query)
    assert re.search(r'ml=laps',responses[0].url)
    assert re.search(r'topics=running',responses[0].url)

  def test_spelled_like_should_use_sp_parameter(self):
    args = ['spelled', 'like', 'platapus']
    query = word.parse(args, {})
    responses = word.go_fetch(query)
    assert re.search(r'sp=platapus',responses[0].url)
  
  def test_sp_and_ml_should_be_combinable(self):
    args = ['animal', 'and', 'spelled', 'like', 'platapus']
    query = word.parse(args, {})
    responses = word.go_fetch(query)
    assert re.search(r'ml=animal',responses[0].url)
    assert re.search(r'sp=platapus',responses[0].url)
  
  def test_ryhmes_with_should_use_rel_rhy_even_when_spelled_wrong(self):
    args = ['ryhmes', 'with', 'cute']
    query = word.parse(args, {})
    responses = word.go_fetch(query)
    assert re.search(r'rel_rhy=cute',responses[0].url)
  
  def test_comes_before_should_use_rc(self):
    args = ['ryhmes', 'with', 'cute', 'and', 'comes', 'before', 'bowl']
    query = word.parse(args, {})
    responses = word.go_fetch(query)
    assert re.search(r'rel_rhy=cute',responses[0].url)
    assert re.search(r'rc=bowl',responses[0].url)
  
  def test_comes_after_should_use_lc(self):
    args = ['ryhmes', 'with', 'cute', 'and', 'comes', 'after', 'leather']
    query = word.parse(args, {})
    responses = word.go_fetch(query)
    assert re.search(r'rel_rhy=cute',responses[0].url)
    assert re.search(r'lc=leather',responses[0].url)
  
  def test_definition_of_should_use_owlbot(self):
    args = ['definition', 'of', 'nostrum']
    word.query_type = "DEF"
    query = word.parse(args, {})
    responses = word.go_fetch(query)
    assert re.search(r'owlbot\.info',responses[0].url) or re.search(r'owlbot\.info',responses[1].url)
  
  def test_pernounciation_of_should_use_meta_data_r_even_when_spelled_wrong(self):
    args = ['pernounciation', 'of', 'nostrum']
    word.query_type = "PRO"
    query = word.parse(args, {})
    responses = word.go_fetch(query)
    assert re.search(r'sp=nostrum',responses[0].url)
    assert re.search(r'qe=sp',responses[0].url)
    assert re.search(r'md=r',responses[0].url)
    assert re.search(r'ipa=1',responses[0].url)
