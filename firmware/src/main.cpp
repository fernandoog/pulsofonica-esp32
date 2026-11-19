#include <Arduino.h>

#include "config.h"
#include "ecg_detector.h"
#include "midi_engine.h"

EcgDetector detector;
MidiEngine midi;

static uint32_t last_sample_us;
static uint32_t last_cc_ms;

bool read_leads_off() {
  const bool lo_plus = digitalRead(PIN_LO_PLUS);
  const bool lo_minus = digitalRead(PIN_LO_MINUS);
  return lo_plus || lo_minus;
}

void setup_hw() {
  pinMode(PIN_LO_PLUS, INPUT);
  pinMode(PIN_LO_MINUS, INPUT);
  pinMode(PIN_SDN, OUTPUT);
  pinMode(PIN_ACDC, OUTPUT);
  digitalWrite(PIN_SDN, HIGH);
  digitalWrite(PIN_ACDC, LOW);

  analogReadResolution(ADC_BITS);
  analogSetPinAttenuation(PIN_ECG_ADC, ADC_11db);
}

void setup() {
#if defined(PULSOFONICA_DEBUG_SERIAL)
  Serial.begin(115200);
  delay(500);
  Serial.println("PulsoFonica debug — USB serial (no MIDI en este entorno)");
#endif

  setup_hw();
  detector.begin();
  midi.begin();
  last_sample_us = micros();
  last_cc_ms = millis();
}

void loop() {
  const uint32_t now_us = micros();
  const uint32_t interval_us = 1000000UL / SAMPLE_HZ;
  if (now_us - last_sample_us < interval_us) {
    return;
  }
  last_sample_us += interval_us;

  const bool leads_off = read_leads_off();
  midi.on_leads_off(leads_off);

  const int raw = analogRead(PIN_ECG_ADC);
  const BeatEvent ev = detector.process_sample(raw, leads_off);

  if (ev.beat) {
    midi.on_beat(ev);
#if defined(PULSOFONICA_DEBUG_SERIAL)
    Serial.printf("BEAT amp=%d bpm=%d hrv=%d raw=%d\n", ev.amplitude, ev.instantaneous_bpm, ev.hrv_pct, raw);
#endif
  }

  const uint32_t now_ms = millis();
  if (now_ms - last_cc_ms >= 40) {
    last_cc_ms = now_ms;
    midi.on_tick_cc(ev);
  }
}