# Mapa MIDI — PulsoFónica

Canal por defecto: **1** (cambiar `MIDI_CHANNEL` en `config.h`).

## Notas

| Evento | Comportamiento |
| --- | --- |
| **Note On** | Cada latido detectado; nota en **pentatónica menor** desde **A3 (57)** |
| **Note Off** | Al sonar el siguiente latido (legato rítmico, un sonido por pulso) |
| **Velocity** | 40–127 según amplitud del pico R |

La escala avanza 1–2 pasos según **HRV** (salto controlado, no aleatorio caótico).

## Controladores (para Ableton / Biofónica)

| CC | Nombre GM | PulsoFónica envía |
| --- | --- | --- |
| **1** | Modulation | BPM instantáneo (50–160 → 0–127) |
| **11** | Expression | “Contacto musical” (señal útil vs ruido) |
| **64** | Sustain | Fuerza del último latido |
| **74** | Brightness / M-S | Variabilidad R-R (HRV expresiva) |

## Pitch bend

± rango configurado en Live; firmware envía desplazamiento acotado según amplitud del pulso (refino tonal entre latidos).

## Integración con `PulsoFónica.als`

Pista **1 — PulsoFónica Cardio MIDI**:

- **MIDI From**: dispositivo USB PulsoFónica / ESP32  
- Instrumento **Meld FM Organ** + escala MIDI + reverb/delay espacial  
- Pistas 2–4: mismo **fondo** de 64 compases que Biofónica (lanzar escena 1)

Sugerencia de mapeo en Live:

1. **MIDI Mapping** → CC#74 → *Filter Freq* del pad de fondo.  
2. CC#1 → macro “Brillo pulso” o LFO amount.  
3. CC#11 → volumen del lead si el intérprete se mueve mucho en escena.

## Ajuste de sensibilidad

En `config.h`:

- `THRESHOLD_RATIO` — sube si detecta falsos latidos; baja si pierde QRS.  
- `REFRACTORY_MS` — mínimo entre picos (280 ms ≈ 214 BPM máx).  
- `SAMPLE_HZ` — 250 Hz recomendado; 500 si quieres más precisión (más CPU).