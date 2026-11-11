import os
import sys

# Phase 1: Ingest and register the embedded FFmpeg binary engine on the fly
try:
    import static_ffmpeg
    print("Initializing embedded FFmpeg environments...")
    static_ffmpeg.add_paths() 
    print("FFmpeg and FFprobe binary streams linked successfully.\n")
except ImportError:
    print("Warning: static-ffmpeg package is missing. Run 'pip install static-ffmpeg' first.")

from pydub import AudioSegment

# --- CHIPCRUNCH AND BITCRUSHER TUNING KNOBS ---
CRUNCH_SAMPLE_RATE = 8000   # Lowering this (e.g. 8000 or 11025) creates intense retro lo-fi aliasing hiss
PITCH_SPEED_FACTOR = 1.15   # 1.15x speed factor slightly raises the pitch and tempo for a chipmunk feel
DRIVE_SATURATION_DB = 18.0  # Drive volume heavily past 0dB to force severe square-wave clipping distortion
FINAL_ATTENUATION_DB = -12.0 # Pull the final volume back down so it doesn't blow out your speakers

def convert_to_chipcrunch():
    if len(sys.argv) < 2:
        print("--- DRAG & DROP CHIPCRUNCH CONVERTER ---")
        print("Status: Active and waiting.")
        print("\nHow to use:")
        print("1. Grab any audio file on your computer (.mp3, .wav, .ogg, .flac).")
        print("2. Drag it directly on top of this script file and let go!")
        return

    for file_idx in range(1, len(sys.argv)):
        input_file_path = sys.argv[file_idx]
        
        if not os.path.exists(input_file_path):
            print(f"Error: Could not track down the file at: {input_file_path}")
            continue

        file_dir = os.path.dirname(input_file_path)
        base_name = os.path.basename(input_file_path)
        name_no_ext, original_ext = os.path.splitext(base_name)
        
        clean_ext = original_ext.lower().replace(".", "")
        if clean_ext == "dat": 
            clean_ext = "mp3"

        # Output name marker indicating chipcrunch transmutation
        output_filename = f"{name_no_ext}_CHIPCRUNCHED{original_ext}"
        output_path = os.path.join(file_dir, output_filename)

        print(f"Processing File [{file_idx}/{len(sys.argv)-1}]: {base_name}")
        
        try:
            # Load the raw audio track natively
            audio_segment = AudioSegment.from_file(input_file_path, format=clean_ext)
            
            print(" -> Down-mixing stereo channels to Mono...")
            mono_audio = audio_segment.set_channels(1)
            
            print(f" -> Speeding up playback timeline by {PITCH_SPEED_FACTOR}x (Shifting Pitch Higher)...")
            # Activating a speed shift on a modified frame rate naturally forces a clean pitch raise
            pitched_audio = mono_audio._spawn(mono_audio.raw_data, overrides={
                "frame_rate": int(mono_audio.frame_rate * PITCH_SPEED_FACTOR)
            }).set_frame_rate(mono_audio.frame_rate)
            
            print(f" -> Bitcrushing sample resolution down to {CRUNCH_SAMPLE_RATE} Hz (Forcing Aliasing Hiss)...")
            # Down-sampling to a brutal 8kHz crushes the audio tracking timeline
            bitcrushed_audio = pitched_audio.set_frame_rate(CRUNCH_SAMPLE_RATE)
            
            print(" -> Overdriving signal into extreme digital clipping saturation...")
            # Smash the audio into hard digital square-wave clipping, then lower the master output gain
            distorted_payload = bitcrushed_audio + DRIVE_SATURATION_DB
            final_master = distorted_payload + FINAL_ATTENUATION_DB
            
            # Re-convert back to a safe rate for file export while keeping the crunchy artifacting locked in
            final_export = final_master.set_frame_rate(22000)
            
            print(f" -> Exporting chipcrunched track to: {output_filename}")
            final_export.export(output_path, format=clean_ext)
            print(f"Success! Retro 8-bit conversion complete.\n")
            
        except Exception as e:
            print(f"❌ Failed to convert {base_name}. Detail: {e}\n")

if __name__ == "__main__":
    try:
        convert_to_chipcrunch()
    except Exception as e:
        print(f"An unexpected exception halted the pipeline: {e}")
        
    print("----------------------------------------")
    input("Process complete. Press ENTER to close this window...")