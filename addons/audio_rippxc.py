import os
import sys

# Dynamic Phase 1: Ingest and register the embedded FFmpeg binary engine on the fly
try:
    import static_ffmpeg
    print("Initializing embedded FFmpeg environments...")
    static_ffmpeg.add_paths() 
    print("FFmpeg and FFprobe binary streams linked successfully.")
except ImportError:
    print("Warning: static-ffmpeg package is missing. Run 'pip install static-ffmpeg' first.")

from pydub import AudioSegment

# THE MAGIC FIX: Automatically detect the exact folder where THIS file sits, no matter what it is named!
CURRENT_SCRIPT_PATH = os.path.abspath(__file__)
GAME_DIR = os.path.dirname(CURRENT_SCRIPT_PATH)
SCRIPT_NAME = os.path.basename(CURRENT_SCRIPT_PATH)

# Look for the required asset structures right where the script was clicked
METADATA_PATH = os.path.join(GAME_DIR, "audio_metadata.dat")
RESOURCE_PATH = os.path.join(GAME_DIR, "audio_resource.dat")
OUTPUT_DIR = os.path.join(GAME_DIR, "extracted_mastered_audio")

# --- MASTERING AND AUDIO DISTORTION TUNING KNOBS ---
BASS_BOOST_DB = 6.0        # Heavy low-end punch (+6.0 dB below 150Hz)
LOW_CUTOFF_HZ = 150        # Frequency floor boundary for bass tracking

HIGH_CUTOFF_HZ = 4000      # Target high frequencies above 4kHz for distortion
HIGH_DISTORTION_DB = 15.0  # Force severe high-end saturation and harmonic clipping
HIGH_ATTENUATION_DB = -6.0 # Restrain final distorted volume to prevent total track blowout

def execute_portable_mastering_chain():
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
                chunks.append((int(parts[0]), int(parts[1])))

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
                
                # High-precision resampling down to exactly 33,200 Hz
                resampled_segment = audio_segment.set_frame_rate(33200)
                
                # 1. APPLY BASS FILTER: Isolate and boost low-end punch
                low_frequencies = resampled_segment.low_pass_filter(LOW_CUTOFF_HZ)
                boosted_bass = low_frequencies + BASS_BOOST_DB
                
                # 2. APPLY HIGH DISTORTION FILTER: Isolate highs, drive into severe hard clipping, then mix back
                high_frequencies = resampled_segment.high_pass_filter(HIGH_CUTOFF_HZ)
                # Boost the high frequencies massively past 0dB to force hard digital clipping distortion
                clipped_highs = high_frequencies + HIGH_DISTORTION_DB
                # Bring the distorted payload volume back down slightly so it doesn't drown out the music
                mastered_highs = clipped_highs + HIGH_ATTENUATION_DB
                
                # Merge the boosted bass, distorted highs, and the clean master track together
                mastered_track = resampled_segment.overlay(boosted_bass).overlay(mastered_highs)
                
                # Evaluate duration bounds to route file tracking formats
                if duration_seconds > 60.0:
                    final_filename = f"track_{index:02d}_bassy_distorted_master.flac"
                    final_path = os.path.join(OUTPUT_DIR, final_filename)
                    mastered_track.export(final_path, format="flac")
                    print(f" -> Mastered Lossless FLAC [33.2kHz + Gritty Highs]: {final_filename}")
                else:
                    final_filename = f"track_{index:02d}_bassy_distorted_master.wav"
                    final_path = os.path.join(OUTPUT_DIR, final_filename)
                    mastered_track.export(final_path, format="wav")
                    print(f" -> Mastered Waveform WAV [33.2kHz + Gritty Highs]: {final_filename}")
                    
            except Exception as e:
                print(f"Skipping structural node {index:02d}: Stream parsing error. Detail: {e}")
            finally:
                # Clean up local workspace file array variables immediately
                if os.path.exists(temp_raw_path):
                    os.remove(temp_raw_path)

    print(f"\nSuccess! All available files processed cleanly by '{SCRIPT_NAME}'!")

if __name__ == "__main__":
    try:
        execute_portable_mastering_chain()
    except Exception as e:
        print(f"A processing exception interrupted execution: {e}")
        
    print("\n----------------------------------------")
    input("Process complete. Press ENTER to close this window...")