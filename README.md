# PulsoFónica

**Instrumento MIDI biomusical** — hermano de [Biofónica](https://github.com/fernandoog/biofonica-touchme): convierte el **latido cardíaco** (ECG con **AD8232**) en notas y controladores MIDI mediante un **ESP32-C3 Super Mini** con **USB MIDI nativo**.

> **No es un dispositivo médico.** Es una herramienta artística / escénica. No uses sus lecturas para diagnóstico.

## Qué hace (como TouchMe, pero con el corazón)

| Señal bioeléctrica | Acción MIDI |
| --- | --- |
| Cada pico R (latido) | **Note On** en pentatónica menor (La), velocity = amplitud del complejo QRS |
| Intervalo R-R | **CC#1** (mod wheel) → BPM instantáneo |
| Calidad de señal | **CC#11** (expression) → contacto / intensidad útil |
| Variabilidad R-R (HRV artística) | **CC#74** (brightness) → timbre / modulación en Ableton |
| Amplitud del latido | **Pitch bend** suave + **CC#64** sustain |

Sin electrodos firmes → *leads off* → silencio MIDI (como soltar las pinzas del TouchMe).

## Contenido del repositorio

```
PulsoFonica/
├── firmware/          PlatformIO (ESP32-C3 + AD8232)
├── ableton/           PulsoFónica.als + build_pulsofonica.py
└── docs/              Cableado, MIDI, puesta en escena
```

## Hardware (BOM)

| Pieza | Enlace / nota |
| --- | --- |
| **ESP32-C3 Super Mini** | USB-C, 4 MB flash, 3.3 V lógica |
| **Módulo AD8232** (Binghe) | [Amazon B0DKJ8ZSX7](https://www.amazon.es/AD8232-Binghe-Frecuencia-Mediciones-Compatible/dp/B0DKJ8ZSX7) |
| **3× electrodos ECG** adhesivos | RA, LA, RL (muñeca derecha, izquierda, tobillo/hipo) |
| Cable dupont / tornillos | Según [docs/HARDWARE.md](docs/HARDWARE.md) |
| Cinta de cobre (opcional, masas) | Igual que en Biofónica — [B08FJ6BSG7](https://www.amazon.es/dp/B08FJ6BSG7) |

## Quick start

### 1. Flashear el ESP32

```powershell
cd firmware
pio run -e esp32-c3-supermini -t upload
```

Perfil `esp32-c3-supermini-serial` activa **USB serial** de depuración (`-DPULSOFONICA_DEBUG_SERIAL=1`).

Arduino core **≥ 3.0** (USB MIDI). Pines por defecto en `firmware/include/config.h`.

### 2. Ableton

```powershell
cd ableton
python build_pulsofonica.py
```

Abre `PulsoFónica.als` (Live 12 Suite). **Preferencias → Enlace MIDI**: entrada **PulsoFónica** o **ESP32** con **Track** activado.

Mapea **CC#74** al cutoff del pad, **CC#1** a tempo externo (Max for Live / manual).

### 3. Colocación de electrodos

1. Limpia la piel; evita cremas grasas.  
2. **LA** en antebrazo/tórax izquierdo, **RA** en derecho, **RL** referencia en tibia o cresta ilíaca.  
3. Mantén quietud las primeras pulsaciones para que el umbral se adapte.

## Concepción artística

**PulsoFónica** sitúa el organismo como **fuente única de reloj y melodía**: el concierto dura lo que dura la atención corporal del intérprete. Combina con Biofónica (TouchMe en piel + PulsoFónica en ritmo cardíaco) para un dúo **piel + pulso**.

## Licencia

Firmware y documentación: MIT (añade `LICENSE` al publicar si lo deseas). Presets Ableton: EULA de Ableton.