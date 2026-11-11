import os
import sys

# Phase 1: Ingest and register the embedded FFmpeg binary engine on the fly
try:
    import static_ffmpeg
    print("Initializing embedded FFmpeg environments...")
    static_ffmpeg.add_paths() 
    print("FFmpeg and FFprobe binary streams linked successfully.")
except ImportError:
    print("Warning: static-ffmpeg package is missing. Run 'pip install static-ffmpeg' first.")

from pydub import AudioSegment

# Automatically detect the exact folder where THIS file sits, no matter what it is named
CURRENT_SCRIPT_PATH = os.path.abspath(__file__)
GAME_DIR = os.path.dirname(CURRENT_SCRIPT_PATH)
SCRIPT_NAME = os.path.basename(CURRENT_SCRIPT_PATH)

# Look for the required asset structures right where the script was clicked
METADATA_PATH = os.path.join(GAME_DIR, "audio_metadata.dat")
RESOURCE_PATH = os.path.join(GAME_DIR, "audio_resource.dat")
OUTPUT_DIR = os.path.join(GAME_DIR, "extracted_mastered_audio")

# --- MASTERING AND FILTER TUNING KNOBS ---
TARGET_SAMPLE_RATE = 22000 # Down-sampled target frequency clock (22 kHz)
HIGH_CUTOFF_HZ = 4000      # Brick-wall filter boundary: drops everything above 4kHz entirely
BASS_BOOST_DB = 4.0        # Optional warm shelf boost to enrich the newly isolated low frequencies

def execute_low_mid_mono_pipeline():
    print(f"Running script natively via: '{SCRIPT_NAME}'")
    
    if not os.path.exists(METADATA_PATH) or not os.path.exists(RESOURCE_PATH):
        print("\n--- LOCATION PROFILE ROUTING ERROR ---")
        print(f"Current Directory Searched: {GAME_DIR}")
        print("Error: Could not find 'audio_metadata.dat' or 'audio_resource.dat' in this folder.")
        print("Fix: Drop this .py script directly inside the game's '\\Data\\' folder and click it again!")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created secure mastering vault: {OUTPUT_DIR}")

    print("Parsing asset coordinates map layout...")
    chunks = []
    with open(METADATA_PATH, "r") as meta_file:
        for line in meta_file:
            line = line.strip()
            if not line or line == "-1 -1":
                break
            parts = line.split()
            if len(parts) == 2:
                # FIX: Explicitly target the individual indices of the parts list
                offset = int(parts[0])
                length = int(parts[1])
                chunks.append((offset, length))

    print(f"Successfully mapped {len(chunks)} target streams. Processing audio matrix...")
    
    with open(RESOURCE_PATH, "rb") as res_file:
        for index, (offset, length) in enumerate(chunks):
            res_file.seek(offset)
            encrypted_data = res_file.read(length)
            
            # Apply your verified engine-override bitwise NOT unmasking operation
            decrypted_bytes = bytearray((~b) & 0xFF for b in encrypted_data)
            
            # Localized temporary workspace file array layer
            temp_raw_path = os.path.join(OUTPUT_DIR, f"temp_unmasked_{index}.dat")
            with open(temp_raw_path, "wb") as temp_file:
                temp_file.write(decrypted_bytes)
                
            if decrypted_bytes.startswith(b"OggS"):
                native_format = "ogg"
            elif decrypted_bytes.startswith(b"RIFF") or decrypted_bytes.startswith(b"WAVE"):
                native_format = "wav"
            else:
                native_format = "mp3"

            try:
                # Load the clean unmasked byte frames into the tracking workspace
                audio_segment = AudioSegment.from_file(temp_raw_path, format=native_format)
                duration_seconds = audio_segment.duration_seconds
                
                # 1. DOWN-MIX TO MONO & RESAMPLE: Convert channel map to 1 (Mono) and clock to 22,000 Hz
                mono_resampled = audio_segment.set_channels(1).set_frame_rate(TARGET_SAMPLE_RATE)
                
                # 2. BRICK-WALL HIGH CUT: Strip all frequencies above 4,000 Hz cleanly from the timeline
                # Running a low-pass filter twice creates a steeper, tighter roll-off slope
                filtered_audio = mono_resampled.low_pass_filter(HIGH_CUTOFF_HZ).low_pass_filter(HIGH_CUTOFF_HZ)
                
                # 3. OPTIONAL WARM SHELF: Lightly boost isolated low-end to balance the heavy high-cut muffling
                low_shelf = filtered_audio.low_pass_filter(200) + BASS_BOOST_DB
                mastered_audio = filtered_audio.overlay(low_shelf)
                
                # Evaluate duration bounds to route file tracking formats
                if duration_seconds > 60.0:
                    final_filename = f"track_{index:02d}_low_mid_mono.flac"
                    final_path = os.path.join(OUTPUT_DIR, final_filename)
                    mastered_audio.export(final_path, format="flac")
                    print(f" -> Mastered Mono FLAC [22kHz + High-Cut]: {final_filename}")
                else:
                    final_filename = f"track_{index:02d}_low_mid_mono.wav"
                    final_path = os.path.join(OUTPUT_DIR, final_filename)
                    mastered_audio.export(final_path, format="wav")
                    print(f" -> Mastered Mono WAV [22kHz + High-Cut]: {final_filename}")
                    
            except Exception as e:
                print(f"Skipping structural node {index:02d}: Stream parsing error. Detail: {e}")
            finally:
                # Clean up local workspace file array variables immediately
                if os.path.exists(temp_raw_path):
                    os.remove(temp_raw_path)

    print(f"\nSuccess! All available files processed cleanly by '{SCRIPT_NAME}'!")

if __name__ == "__main__":
    try:
        execute_low_mid_mono_pipeline()
    except Exception as e:
        print(f"A processing exception interrupted execution: {e}")
        
    print("\n----------------------------------------")
    input("Process complete. Press ENTER to close this window...")