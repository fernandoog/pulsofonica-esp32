#pragma once

#include "ecg_detector.h"

class MidiEngine {
public:
  void begin();
  void on_leads_off(bool off);
  void on_beat(const BeatEvent &ev);
  void on_tick_cc(const BeatEvent &ev);

private:
  uint8_t scale_index_;
  uint8_t last_note_;
  bool leads_off_;
  void send_note(uint8_t note, uint8_t velocity);
};