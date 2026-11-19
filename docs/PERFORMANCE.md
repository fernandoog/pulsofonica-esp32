# Guía de performance — PulsoFónica

## Rol escénico

Trata el **pulso audible** como metrónomo interno del intérprete, no como click externo. El público ve electrodos y un módulo diminuto: la tensión dramática viene de la **vulnerabilidad fisiológica** (complemento perfecto a Biofónica / TouchMe en la misma programación).

## Antes del concierto (15 min)

1. Flashear firmware verificado; probar **leads-off** (desconectar un electrodo → debe callar).  
2. Calentamiento: 60 s quieto para auto-umbral.  
3. Probar rango dinámico: respirar lento, subir escaleras, volver a escenario.  
4. En Ableton: lanzar **escena 1**; comprobar que CC#1 sube/baja con el pulso.

## Concierto largo (&gt;15 min)

- Usa los **3 pads en bucle** del Live Set; graba con pista **Resampling** desde Main.  
- Hidrata al intérprete; deshidratación = señal más ruidosa y CC#11 inestable.  
- Ten repuesto de parches ECG; el sudor enmascara el gel.

## Dúo Biofónica + PulsoFónica

| Artista A | TouchMe entre piel compartida → melodía táctil |
| Artista B (o mismo) | PulsoFónica → ritmo armónico y modulación CC al pad |

Sincronización: **no hace falta clock MIDI común**; el pulso es la referencia orgánica.

## Solución de problemas

| Síntoma | Acción |
| --- | --- |
| Notas espurias | Subir `REFRACTORY_MS` o `THRESHOLD_RATIO` |
| Sin notas | Revisar LOD+, LOD-, humedad de electrodos, SDN=HIGH |
| MIDI no aparece en Windows | Cable datos USB, driver, probar otro puerto |
| Mucho pitch bend | Reducir rango en Live o comentar `pitchBend` en `midi_engine.cpp` |