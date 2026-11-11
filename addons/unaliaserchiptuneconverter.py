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

# --- RETRO HARDWARE EMULATION KNOBS ---
CRUNCH_SAMPLE_RATE = 11025  # Slightly higher rate gives cleaner vintage grit instead of total garbage
PITCH_SPEED_FACTOR = 1.12   # Clean, classic hardware pitch lift (approx. +1 semitone)
ANALOG_WARMTH_DB = 8.0      # Warm overdrive gain to saturate the low-mids natively
ANALOG_CUTOFF_HZ = 3500     # The Speaker Cone Filter: Rolls off harsh digital glassiness above 3.5kHz
FINAL_ATTENUATION_DB = -6.0 # Stabilize volume bounds for master export

def convert_to_analog_crunch():
    if len(sys.argv) < 2:
        print("--- DRAG & DROP WARM CHIPCRUNCH CONVERTER ---")
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

        # Output file tagged to reflect warm analog transformation
        output_filename = f"{name_no_ext}_RETRO_HARDWARE{original_ext}"
        output_path = os.path.join(file_dir, output_filename)

        print(f"Processing File [{file_idx}/{len(sys.argv)-1}]: {base_name}")
        
        try:
            # Load the raw audio track natively
            audio_segment = AudioSegment.from_file(input_file_path, format=clean_ext)
            
            print(" -> Down-mixing stereo channels to Mono...")
            mono_audio = audio_segment.set_channels(1)
            
            print(f" -> Shifting hardware clock by {PITCH_SPEED_FACTOR}x (Lifting Pitch)...")
            pitched_audio = mono_audio._spawn(mono_audio.raw_data, overrides={
                "frame_rate": int(mono_audio.frame_rate * PITCH_SPEED_FACTOR)
            }).set_frame_rate(mono_audio.frame_rate)
            
            print(f" -> Downsampling to legacy hardware rate ({CRUNCH_SAMPLE_RATE} Hz)...")
            bitcrushed_audio = pitched_audio.set_frame_rate(CRUNCH_SAMPLE_RATE)
            
            print(" -> Injecting warm analog drive saturation...")
            # Slices a warm low-mid band boost to simulate vintage analog tube hardware drive
            warm_saturator = bitcrushed_audio.low_pass_filter(600).high_pass_filter(100) + ANALOG_WARMTH_DB
            driven_audio = bitcrushed_audio.overlay(warm_saturator)
            
            print(f" -> Running bitstream through analog speaker cabinet filter ({ANALOG_CUTOFF_HZ} Hz)...")
            # The Magic Step: Run a double low-pass right at 3.5kHz to shave away the cold digital harshness
            analog_cabinet = driven_audio.low_pass_filter(ANALOG_CUTOFF_HZ).low_pass_filter(ANALOG_CUTOFF_HZ)
            
            # Rebalance final gain staging parameters
            final_master = analog_cabinet + FINAL_ATTENUATION_DB
            final_export = final_master.set_frame_rate(22000)
            
            print(f" -> Exporting analog retro track to: {output_filename}")
            final_export.export(output_path, format=clean_ext)
            print(f"Success! Vintage hardware emulation complete.\n")
            
        except Exception as e:
            print(f"❌ Failed to convert {base_name}. Detail: {e}\n")

if __name__ == "__main__":
    try:
        convert_to_analog_crunch()
    except Exception as e:
        print(f"An unexpected exception halted the pipeline: {e}")
        
    print("----------------------------------------")
    input("Process complete. Press ENTER to close this window...")