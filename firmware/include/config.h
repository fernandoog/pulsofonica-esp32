#pragma once

// --- Pines (ESP32-C3 Super Mini ↔ módulo AD8232 Binghe) ---
// Ajusta si tu Super Mini usa otros GPIO libres.
static const int PIN_ECG_ADC = 4;   // ADC1_CH4 — señal OUT del AD8232
static const int PIN_LO_PLUS = 5;   // LOD+ electrodos desconectados
static const int PIN_LO_MINUS = 6;  // LOD-
static const int PIN_SDN = 7;         // alto = módulo activo
static const int PIN_ACDC = 8;        // bajo = modo DC (típico en breakouts)

// --- ADC / muestreo ---
static const int SAMPLE_HZ = 250;
static const int ADC_BITS = 12;
static const int ADC_MAX = (1 << ADC_BITS) - 1;

// --- Detección de latidos ---
static const int REFRACTORY_MS = 280;
static const float THRESHOLD_RATIO = 0.42f;
static const int BASELINE_ALPHA = 32;  // IIR lento (más alto = más lento)

// --- MIDI ---
static const uint8_t MIDI_CHANNEL = 1;
static const uint8_t MIDI_NOTE_ROOT = 57;  // A3 — encaja con Biofónica (La)
static const uint8_t PENTATONIC[] = {0, 2, 4, 7, 9, 12, 14, 16, 19, 21};
static const size_t PENTATONIC_LEN = sizeof(PENTATONIC) / sizeof(PENTATONIC[0]);

// CC (estándar Ableton / Biofónica)
static const uint8_t CC_MOD_WHEEL = 1;    // BPM instantáneo normalizado
static const uint8_t CC_EXPRESSION = 11; // calidad de contacto
static const uint8_t CC_TIMBRE = 74;     // variabilidad R-R (HRV artística)
static const uint8_t CC_SUSTAIN = 64;    // fuerza del último pico