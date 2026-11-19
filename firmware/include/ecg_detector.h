#pragma once

#include <cstdint>

struct BeatEvent {
  bool beat;
  int amplitude;
  int instantaneous_bpm;
  int contact_pct;
  int hrv_pct;
};

class EcgDetector {
public:
  void begin();
  BeatEvent process_sample(int raw_adc, bool leads_off);

private:
  void reset_threshold();
  int baseline_;
  int threshold_;
  int last_peak_ms_;
  int last_rr_ms_;
  int rr_history_[8];
  uint8_t rr_idx_;
  int peak_count_;
  int moving_hp_;
};