"""Genera el Live Set (Ableton Live 12). Ejecutar desde esta carpeta."""
from __future__ import annotations

import gzip
import re
from dataclasses import dataclass
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
PROJECT_TITLE = "PulsoFónica"
OUT_ALS = PROJECT_DIR / f"{PROJECT_TITLE}.als"

LIVE = Path(r"C:\ProgramData\Ableton\Live 12 Suite\Resources\Core Library")
BASE_ALS = LIVE / "Defaults" / "Creating Tracks" / "MIDI Track" / "Default MIDI Track.als"
INSTR = LIVE / "Devices" / "Instruments"
MIDI_FX = LIVE / "Devices" / "MIDI Effects"
AUDIO_FX = LIVE / "Devices" / "Audio Effects"

TEMPO = 72
SCALE_ROOT = 9  # A
LOOP_BARS = 64
BEATS_PER_BAR = 4


@dataclass(frozen=True)
class TrackDef:
    name: str
    annotation: str
    color: int
    instrument_adv: Path
    midi_fx: tuple[Path, ...]
    audio_fx: tuple[Path, ...]
    chord_notes: tuple[int, ...]
    velocity: int
    volume: float
    monitor: int
    send_a: float | None = None


TRACKS = (
    TrackDef(
        name="PulsoFónica — Cardio MIDI (ESP32)",
        annotation="USB MIDI PulsoFónica: cada latido=nota; CC1=BPM, CC11=contacto, CC74=HRV. Sin clip.",
        color=5,
        instrument_adv=INSTR / "Meld" / "Synth Keys" / "FM Organ.adv",
        midi_fx=(MIDI_FX / "Scale" / "Minor Pentatonic.adv",),
        audio_fx=(
            AUDIO_FX / "Reverb" / "Hall" / "Large Hall.adv",
            AUDIO_FX / "Delay" / "Ambient Spaces" / "Full Range Spatial.adv",
        ),
        chord_notes=(),
        velocity=0,
        volume=0.88,
        monitor=1,
    ),
    TrackDef(
        name="Fondo — Pad orgánico",
        annotation="Acompañamiento suave; lanzar escena «Concierto».",
        color=20,
        instrument_adv=INSTR / "Operator" / "Synth Pad" / "Thick Organ Pad.adv",
        midi_fx=(),
        audio_fx=(AUDIO_FX / "Reverb" / "Hall" / "Dark Hall.adv",),
        chord_notes=(57, 60, 64, 71),
        velocity=42,
        volume=0.58,
        monitor=1,
        send_a=0.35,
    ),
    TrackDef(
        name="Fondo — Motor graves",
        annotation="Subbajo tipo órgano de película; no compite con el tacto.",
        color=26,
        instrument_adv=INSTR / "Operator" / "Bass" / "Organ Bass.adv",
        midi_fx=(),
        audio_fx=(AUDIO_FX / "Reverb" / "Hall" / "Hall Damped.adv",),
        chord_notes=(45, 57),
        velocity=38,
        volume=0.48,
        monitor=1,
        send_a=0.2,
    ),
    TrackDef(
        name="Fondo — Bruma WAV",
        annotation="Capa etérea; mezcla baja para conciertos largos.",
        color=6,
        instrument_adv=INSTR / "Wavetable" / "Synth Pad" / "Organic Lo-Fi Pad.adv",
        midi_fx=(),
        audio_fx=(AUDIO_FX / "Reverb" / "Hall" / "Wooden Hall.adv",),
        chord_notes=(64, 67, 72, 76),
        velocity=36,
        volume=0.45,
        monitor=1,
        send_a=0.45,
    ),
)

DEVICE_TAGS = (
    "UltraAnalog",
    "Operator",
    "InstrumentMeld",
    "InstrumentVector",
    "Wavetable",
    "MidiScale",
    "MidiVelocity",
    "Reverb",
    "Echo",
    "Delay",
)


def load_device_block(adv_path: Path) -> str:
    raw = gzip.open(adv_path, "rb").read().decode("utf-8")
    for tag in DEVICE_TAGS:
        match = re.search(rf"<{tag}>.*?</{tag}>", raw, re.DOTALL)
        if match:
            block = match.group(0)
            return block.replace(f"<{tag}>", f'<{tag} Id="0">', 1)
    raise RuntimeError(f"No device block in {adv_path}")


def collect_ids(fragment: str) -> set[int]:
    return {int(x) for x in re.findall(r'\bId="(\d+)"', fragment)}


def reindex_ids_sequential(fragment: str, next_id: int) -> tuple[str, int]:
    """Cada atributo Id= debe ser único (listas Lom); no reutilizar por valor antiguo."""

    def replace(_match: re.Match[str]) -> str:
        nonlocal next_id
        assigned = next_id
        next_id += 1
        return f'Id="{assigned}"'

    return re.sub(r'\bId="\d+"', replace, fragment), next_id


def reindex_device_automation(device_xml: str, next_id: int) -> tuple[str, int]:
    counter = next_id

    def assign_id(match: re.Match[str]) -> str:
        nonlocal counter
        tag = match.group(1)
        closer = match.group(2)
        assigned = counter
        counter += 1
        return f'<{tag} Id="{assigned}"{closer}'

    device_xml = re.sub(
        r"<(AutomationTarget|ModulationTarget|Pointee) Id=\"\d+\"(\s*/>|>)",
        assign_id,
        device_xml,
    )
    return device_xml, counter


def build_drone_clip(
    clip_id: int,
    name: str,
    notes: tuple[int, ...],
    velocity: int,
    bars: int = LOOP_BARS,
) -> str:
    loop_end = bars * BEATS_PER_BAR
    chords = (
        (0, (57, 60, 64)),
        (bars // 4, (53, 57, 60)),
        (bars // 2, (48, 55, 60)),
        (3 * bars // 4, (55, 59, 62)),
    )
    key_tracks: dict[int, list[str]] = {}
    for start_bar, chord in chords:
        start = float(start_bar * BEATS_PER_BAR)
        duration = float((bars // 4) * BEATS_PER_BAR - 0.1)
        for note in chord:
            if note not in notes:
                continue
            key_tracks.setdefault(note, []).append(
                f'<MidiNoteEvent Time="{start}" Duration="{duration}" '
                f'Velocity="{velocity}" OffVelocity="0" NoteId="0" />'
            )
    if not key_tracks and notes:
        duration = float(loop_end - 0.1)
        for note in notes:
            key_tracks[note] = [
                f'<MidiNoteEvent Time="0" Duration="{duration}" '
                f'Velocity="{velocity}" OffVelocity="0" NoteId="0" />'
            ]

    key_track_xml = []
    kt_id = 1
    for pitch in sorted(key_tracks):
        events = "\n\t\t\t\t\t\t\t".join(key_tracks[pitch])
        key_track_xml.append(
            f"""<KeyTrack Id="{kt_id}">
\t\t\t\t\t\t\t\t<Notes>
\t\t\t\t\t\t\t\t\t{events}
\t\t\t\t\t\t\t\t</Notes>
\t\t\t\t\t\t\t</KeyTrack>"""
        )
        kt_id += 1

    notes_section = (
        "<Notes>\n\t\t\t\t\t\t<KeyTracks>\n\t\t\t\t\t\t\t"
        + "\n\t\t\t\t\t\t\t".join(key_track_xml)
        + "\n\t\t\t\t\t\t</KeyTracks>\n\t\t\t\t\t</Notes>"
        if key_track_xml
        else "<Notes><KeyTracks></KeyTracks></Notes>"
    )

    return f"""<MidiClip Id="{clip_id}" Time="0">
\t\t\t\t\t\t\t\t<LomId Value="0" />
\t\t\t\t\t\t\t\t<LomIdView Value="0" />
\t\t\t\t\t\t\t\t<CurrentStart Value="0" />
\t\t\t\t\t\t\t\t<CurrentEnd Value="{loop_end}" />
\t\t\t\t\t\t\t\t<Loop>
\t\t\t\t\t\t\t\t\t<LoopStart Value="0" />
\t\t\t\t\t\t\t\t\t<LoopEnd Value="{loop_end}" />
\t\t\t\t\t\t\t\t\t<StartRelative Value="0" />
\t\t\t\t\t\t\t\t\t<LoopOn Value="true" />
\t\t\t\t\t\t\t\t\t<OutMarker Value="{loop_end}" />
\t\t\t\t\t\t\t\t\t<HiddenLoopStart Value="0" />
\t\t\t\t\t\t\t\t\t<HiddenLoopEnd Value="{loop_end}" />
\t\t\t\t\t\t\t\t</Loop>
\t\t\t\t\t\t\t\t<Name Value="{name}" />
\t\t\t\t\t\t\t\t<Annotation Value="Bucle {bars} compases (~{bars * 4 * 60 // TEMPO // 60} min en {TEMPO} BPM)" />
\t\t\t\t\t\t\t\t<Color Value="20" />
\t\t\t\t\t\t\t\t<LaunchMode Value="0" />
\t\t\t\t\t\t\t\t<LaunchQuantisation Value="0" />
\t\t\t\t\t\t\t\t<TimeSignature>
\t\t\t\t\t\t\t\t\t<TimeSignatures>
\t\t\t\t\t\t\t\t\t\t<RemoteableTimeSignature Id="0">
\t\t\t\t\t\t\t\t\t\t\t<Numerator Value="4" />
\t\t\t\t\t\t\t\t\t\t\t<Denominator Value="4" />
\t\t\t\t\t\t\t\t\t\t\t<Time Value="0" />
\t\t\t\t\t\t\t\t\t\t</RemoteableTimeSignature>
\t\t\t\t\t\t\t\t\t</TimeSignatures>
\t\t\t\t\t\t\t\t</TimeSignature>
\t\t\t\t\t\t\t\t<Envelopes>
\t\t\t\t\t\t\t\t\t<Envelopes />
\t\t\t\t\t\t\t\t</Envelopes>
\t\t\t\t\t\t\t\t<ScrollerTimePreserver>
\t\t\t\t\t\t\t\t\t<LeftTime Value="0" />
\t\t\t\t\t\t\t\t\t<RightTime Value="{loop_end}" />
\t\t\t\t\t\t\t\t</ScrollerTimePreserver>
\t\t\t\t\t\t\t\t<TimeSelection>
\t\t\t\t\t\t\t\t\t<AnchorTime Value="0" />
\t\t\t\t\t\t\t\t\t<OtherTime Value="0" />
\t\t\t\t\t\t\t\t</TimeSelection>
\t\t\t\t\t\t\t\t<Legato Value="true" />
\t\t\t\t\t\t\t\t<Ram Value="false" />
\t\t\t\t\t\t\t\t<GrooveSettings>
\t\t\t\t\t\t\t\t\t<GrooveId Value="-1" />
\t\t\t\t\t\t\t\t</GrooveSettings>
\t\t\t\t\t\t\t\t<Disabled Value="false" />
\t\t\t\t\t\t\t\t<VelocityAmount Value="0" />
\t\t\t\t\t\t\t\t<FollowAction>
\t\t\t\t\t\t\t\t\t<FollowTime Value="{loop_end}" />
\t\t\t\t\t\t\t\t\t<IsLinked Value="true" />
\t\t\t\t\t\t\t\t\t<LoopIterations Value="100" />
\t\t\t\t\t\t\t\t\t<FollowActionA Value="0" />
\t\t\t\t\t\t\t\t\t<FollowActionB Value="0" />
\t\t\t\t\t\t\t\t\t<FollowChanceA Value="100" />
\t\t\t\t\t\t\t\t\t<FollowChanceB Value="0" />
\t\t\t\t\t\t\t\t\t<JumpIndexA Value="0" />
\t\t\t\t\t\t\t\t\t<JumpIndexB Value="0" />
\t\t\t\t\t\t\t\t\t<FollowActionEnabled Value="false" />
\t\t\t\t\t\t\t\t</FollowAction>
\t\t\t\t\t\t\t\t<Grid>
\t\t\t\t\t\t\t\t\t<FixedNumerator Value="1" />
\t\t\t\t\t\t\t\t\t<FixedDenominator Value="16" />
\t\t\t\t\t\t\t\t\t<GridIntervalPixel Value="20" />
\t\t\t\t\t\t\t\t\t<Ntoles Value="2" />
\t\t\t\t\t\t\t\t\t<SnapToGrid Value="true" />
\t\t\t\t\t\t\t\t\t<Fixed Value="false" />
\t\t\t\t\t\t\t\t</Grid>
\t\t\t\t\t\t\t\t<FreezeStart Value="0" />
\t\t\t\t\t\t\t\t<FreezeEnd Value="0" />
\t\t\t\t\t\t\t\t<IsWarped Value="true" />
\t\t\t\t\t\t\t\t<TakeId Value="0" />
\t\t\t\t\t\t\t\t<IsInKey Value="true" />
\t\t\t\t\t\t\t\t<ScaleInformation>
\t\t\t\t\t\t\t\t\t<Root Value="{SCALE_ROOT}" />
\t\t\t\t\t\t\t\t\t<Name Value="2" />
\t\t\t\t\t\t\t\t</ScaleInformation>
\t\t\t\t\t\t\t\t<AutomationEnvelopesListWrapper LomId="0" />
\t\t\t\t\t\t\t\t{notes_section}
\t\t\t\t\t\t\t</MidiClip>"""


def extract_midi_track(xml: str) -> str:
    match = re.search(r"<MidiTrack Id=\"\d+\".*?</MidiTrack>", xml, re.DOTALL)
    if not match:
        raise RuntimeError("No MidiTrack in base template")
    return match.group(0)


def patch_track(
    track_xml: str,
    track: TrackDef,
    track_index: int,
    next_pointee: int,
) -> tuple[str, int]:
    track_xml = re.sub(
        r"<EffectiveName Value=\"[^\"]*\" />\s*"
        r"<UserName Value=\"[^\"]*\" />\s*"
        r"<Annotation Value=\"[^\"]*\" />",
        (
            f'<EffectiveName Value="{track_index + 1}-MIDI" />\n\t\t\t\t\t'
            f'<UserName Value="{track.name}" />\n\t\t\t\t\t'
            f'<Annotation Value="{track.annotation}" />'
        ),
        track_xml,
        count=1,
    )
    track_xml = re.sub(
        r"<Color Value=\"\d+\" />",
        f'<Color Value="{track.color}" />',
        track_xml,
        count=1,
    )
    track_xml = re.sub(
        r"<MonitoringEnum Value=\"\d+\" />",
        f'<MonitoringEnum Value="{track.monitor}" />',
        track_xml,
        count=1,
    )
    vol = track.volume
    track_xml = re.sub(
        r"(<Volume>\s*<LomId Value=\"0\" />\s*)<Manual Value=\"[\d.]+\" />",
        rf'\1<Manual Value="{vol}" />',
        track_xml,
        count=1,
    )

    if track.chord_notes:
        clip = build_drone_clip(9000 + track_index, f"Concierto — {track.name}", track.chord_notes, track.velocity)
        clip_slot = f"""<ClipSlot Id="0">
\t\t\t\t\t\t\t\t<LomId Value="0" />
\t\t\t\t\t\t\t\t<ClipSlot>
\t\t\t\t\t\t\t\t\t<Value>
\t\t\t\t\t\t\t\t\t\t{clip}
\t\t\t\t\t\t\t\t\t</Value>
\t\t\t\t\t\t\t\t</ClipSlot>
\t\t\t\t\t\t\t\t<HasStop Value="true" />
\t\t\t\t\t\t\t</ClipSlot>"""
        track_xml = re.sub(
            r"(<MainSequencer>.*?<ClipSlotList>)\s*<ClipSlot Id=\"0\">.*?</ClipSlot>\s*(</ClipSlotList>)",
            rf"\1\n\t\t\t\t\t\t{clip_slot}\n\t\t\t\t\t\2",
            track_xml,
            count=1,
            flags=re.DOTALL,
        )

    # Reindexar pista/clips; los dispositivos van después para no romper el grafo Lom (evita crash).
    track_xml, next_pointee = reindex_ids_sequential(track_xml, next_pointee)

    devices: list[str] = []
    for adv in track.midi_fx:
        dev, next_pointee = reindex_device_automation(load_device_block(adv), next_pointee)
        devices.append(dev)
    dev, next_pointee = reindex_device_automation(
        load_device_block(track.instrument_adv), next_pointee
    )
    devices.append(dev)
    for adv in track.audio_fx:
        dev, next_pointee = reindex_device_automation(load_device_block(adv), next_pointee)
        devices.append(dev)

    chain = "\n\t\t\t\t\t\t\t".join(devices)
    track_xml = track_xml.replace(
        "<DeviceChain>\n\t\t\t\t\t\t<Devices />\n\t\t\t\t\t\t<SignalModulations />",
        f"<DeviceChain>\n\t\t\t\t\t\t<Devices>\n\t\t\t\t\t\t\t{chain}\n\t\t\t\t\t\t</Devices>\n\t\t\t\t\t\t<SignalModulations />",
        1,
    )

    track_xml = re.sub(
        r"<MidiTrack Id=\"\d+\"",
        f'<MidiTrack Id="{track_index}"',
        track_xml,
        count=1,
    )
    return track_xml, next_pointee


def build_live_set() -> str:
    base = gzip.open(BASE_ALS, "rb").read().decode("utf-8")
    track_tpl = extract_midi_track(base)
    next_id = int(re.search(r'<NextPointeeId Value="(\d+)"', base).group(1))
    built_tracks: list[str] = []
    for idx, tdef in enumerate(TRACKS):
        # Cada pista necesita IDs Lom únicos; compartir id_map duplicaba AutomationTarget.
        track_xml, next_id = patch_track(track_tpl, tdef, idx, next_id)
        built_tracks.append(track_xml)

    tracks_block = "\n\t\t\t".join(built_tracks)
    xml = re.sub(
        r"<Tracks>.*?</Tracks>",
        f"<Tracks>\n\t\t\t{tracks_block}\n\t\t</Tracks>",
        base,
        count=1,
        flags=re.DOTALL,
    )
    xml = re.sub(
        r"<NextPointeeId Value=\"\d+\" />",
        f'<NextPointeeId Value="{next_id + 500}" />',
        xml,
        count=1,
    )
    xml = re.sub(
        r"(<Tempo>\s*<LomId Value=\"0\" />\s*)<Manual Value=\"[\d.]+\" />",
        rf'\1<Manual Value="{TEMPO}" />',
        xml,
        count=1,
    )
    xml = xml.replace(
        "<ScaleInformation>\n\t\t\t<Root Value=\"0\" />\n\t\t\t<Name Value=\"0\" />",
        f"<ScaleInformation>\n\t\t\t<Root Value=\"{SCALE_ROOT}\" />\n\t\t\t<Name Value=\"2\" />",
    )
    xml = re.sub(
        r"<Annotation Value=\"\" />\s*<SoloOrPflSavedValue",
        (
            f'<Annotation Value="{PROJECT_TITLE}: ESP32+AD8232 — latido como instrumento. '
            'Lanzar escena 1. Mapea CC en Ableton." />\n\t\t'
            "<SoloOrPflSavedValue"
        ),
        xml,
        count=1,
    )
    return xml


def main() -> None:
    xml = build_live_set()
    with gzip.open(OUT_ALS, "wb", compresslevel=9) as f:
        f.write(xml.encode("utf-8"))
    print(f"Written: {OUT_ALS} ({OUT_ALS.stat().st_size} bytes)")


if __name__ == "__main__":
    main()