
from AppKit import NSSpeechSynthesizer
nssp = NSSpeechSynthesizer
ve = nssp.alloc().init()
v = 'com.apple.speech.synthesis.voice.ting-ting.compact'
ve.setVoice_(v)
s =u'\u597d'
ve.startSpeakingString_(s)

ve.setVoice_("com.apple.speech.synthesis.voice.Alex")
p = ve.phonemesFromText_('hello')
p = ve.phonemesFromText_('hello?')

ve.startSpeakingString_(p)

ve.startSpeakingString_('[[inpt PHON]]%s[[inpt PHON]]'%p)

