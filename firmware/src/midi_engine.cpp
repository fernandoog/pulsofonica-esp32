#include "midi_engine.h"

#include "config.h"

#include <Arduino.h>

#if __has_include("USB.h") && __has_include("USBMIDI.h")
#include "USB.h"
#include "USBMIDI.h"
USBMIDI MIDI;
#define PULSOFONICA_USB_MIDI 1
#else
#define PULSOFONICA_USB_MIDI 0
#endif

void MidiEngine::begin() {
  scale_index_ = 0;
  last_note_ = 0;
  leads_off_ = true;
#if PULSOFONICA_USB_MIDI
  USB.begin();
  delay(250);
#endif
}

void MidiEngine::send_note(uint8_t note, uint8_t velocity) {
#if PULSOFONICA_USB_MIDI
  if (last_note_) {
    MIDI.noteOff(last_note_, 0, MIDI_CHANNEL);
  }
  MIDI.noteOn(note, velocity, MIDI_CHANNEL);
#else
  (void)note;
  (void)velocity;
#endif
  last_note_ = note;
}

void MidiEngine::on_leads_off(bool off) {
  if (off == leads_off_) {
    return;
  }
  leads_off_ = off;
#if PULSOFONICA_USB_MIDI
  if (off && last_note_) {
    MIDI.noteOff(last_note_, 0, MIDI_CHANNEL);
    last_note_ = 0;
  }
  MIDI.controlChange(CC_EXPRESSION, off ? 0 : 100, MIDI_CHANNEL);
#endif
}

void MidiEngine::on_beat(const BeatEvent &ev) {
  if (!ev.beat || leads_off_) {
    return;
  }

  const int step = (ev.hrv_pct / 32) % PENTATONIC_LEN;
  scale_index_ = (scale_index_ + 1 + step) % PENTATONIC_LEN;
  const uint8_t note = MIDI_NOTE_ROOT + PENTATONIC[scale_index_];
  send_note(note, static_cast<uint8_t>(ev.amplitude));

#if PULSOFONICA_USB_MIDI
  MIDI.controlChange(CC_SUSTAIN, static_cast<uint8_t>(ev.amplitude), MIDI_CHANNEL);
  if (ev.instantaneous_bpm > 0) {
    const uint8_t bpm_cc = constrain(map(ev.instantaneous_bpm, 50, 160, 0, 127), 0, 127);
    MIDI.controlChange(CC_MOD_WHEEL, bpm_cc, MIDI_CHANNEL);
  }
  MIDI.controlChange(CC_TIMBRE, static_cast<uint8_t>(ev.hrv_pct), MIDI_CHANNEL);
  const int bend14 = constrain(map(ev.amplitude, 40, 127, 7200, 9192), 0, 16383);
  MIDI.pitchBend(static_cast<unsigned int>(bend14), MIDI_CHANNEL);
#endif
}

void MidiEngine::on_tick_cc(const BeatEvent &ev) {
  if (leads_off_) {
    return;
  }
#if PULSOFONICA_USB_MIDI
  MIDI.controlChange(CC_EXPRESSION, static_cast<uint8_t>(ev.contact_pct), MIDI_CHANNEL);
  if (!ev.beat && ev.instantaneous_bpm > 0) {
    const uint8_t bpm_cc = constrain(map(ev.instantaneous_bpm, 50, 160, 0, 127), 0, 127);
    MIDI.controlChange(CC_MOD_WHEEL, bpm_cc, MIDI_CHANNEL);
  }
#endif
}