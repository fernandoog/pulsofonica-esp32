#include "ecg_detector.h"

#include "config.h"

#include <Arduino.h>
#include <algorithm>
#include <cmath>

void EcgDetector::begin() {
  baseline_ = ADC_MAX / 2;
  threshold_ = static_cast<int>(ADC_MAX * THRESHOLD_RATIO);
  last_peak_ms_ = 0;
  last_rr_ms_ = 0;
  rr_idx_ = 0;
  peak_count_ = 0;
  moving_hp_ = 0;
  for (int &v : rr_history_) {
    v = 0;
  }
}

void EcgDetector::reset_threshold() {
  threshold_ = baseline_ + static_cast<int>((ADC_MAX / 2 - baseline_) * THRESHOLD_RATIO);
}

BeatEvent EcgDetector::process_sample(int raw_adc, bool leads_off) {
  BeatEvent ev{};
  ev.beat = false;
  ev.amplitude = 0;

  if (leads_off) {
    ev.contact_pct = 0;
    ev.instantaneous_bpm = 0;
    ev.hrv_pct = 0;
    return ev;
  }

  baseline_ += (raw_adc - baseline_) / BASELINE_ALPHA;
  const int hp = raw_adc - baseline_;
  moving_hp_ = (moving_hp_ * 7 + hp) / 8;
  const int signal = moving_hp_;

  if (peak_count_ < 8) {
    threshold_ = std::max(threshold_, std::abs(signal));
  }

  ev.contact_pct = constrain(map(std::abs(signal), 0, 400, 10, 127), 0, 127);

  const uint32_t now = millis();
  const bool refractory = (now - last_peak_ms_) < static_cast<uint32_t>(REFRACTORY_MS);

  if (!refractory && signal > threshold_ && signal > 80) {
    ev.beat = true;
    ev.amplitude = constrain(map(signal, threshold_, threshold_ + 900, 40, 127), 1, 127);

    if (last_peak_ms_ > 0) {
      last_rr_ms_ = static_cast<int>(now - last_peak_ms_);
      rr_history_[rr_idx_ % 8] = last_rr_ms_;
      rr_idx_++;
      if (last_rr_ms_ > 0) {
        ev.instantaneous_bpm = constrain(60000 / last_rr_ms_, 40, 200);
      }
    }
    last_peak_ms_ = now;
    peak_count_++;

    int sum = 0;
    int count = 0;
    for (int v : rr_history_) {
      if (v > 0) {
        sum += v;
        count++;
      }
    }
    if (count >= 3) {
      const int mean = sum / count;
      int var_sum = 0;
      for (int v : rr_history_) {
        if (v > 0) {
          var_sum += abs(v - mean);
        }
      }
      const int mad = var_sum / count;
      ev.hrv_pct = constrain(map(mad, 0, 120, 0, 127), 0, 127);
    }
  }

  if (peak_count_ > 0 && (now % 2000) < 5) {
    threshold_ = static_cast<int>(baseline_ + (threshold_ - baseline_) * 0.92f);
    threshold_ = std::max(threshold_, 120);
  }

  if (!ev.beat) {
    ev.instantaneous_bpm = last_rr_ms_ > 0 ? constrain(60000 / last_rr_ms_, 40, 200) : 0;
    int sum = 0, count = 0;
    for (int v : rr_history_) {
      if (v > 0) {
        sum += v;
        count++;
      }
    }
    if (count >= 3) {
      const int mean = sum / count;
      int var_sum = 0;
      for (int v : rr_history_) {
        if (v > 0) var_sum += abs(v - mean);
      }
      ev.hrv_pct = constrain(map(var_sum / count, 0, 120, 0, 127), 0, 127);
    }
  }

  return ev;
}