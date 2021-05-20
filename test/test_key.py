# -*- coding: utf-8 -*-
import py.test

from key import genkey

def test_sscq(count=10):
    lstRet = []
    for i in range(count):
        lstRet.append(genkey('sscq'))
    assert len(lstRet) == count
    
def test_usdp(count=10):
    lstRet = []
    for i in range(count):
        lstRet.append(genkey('usdp'))
    assert len(lstRet) == count
    
