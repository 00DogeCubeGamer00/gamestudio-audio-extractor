import os
import sys

try:
    import static_ffmpeg
    print("Initializing embedded FFmpeg environments...")
    static_ffmpeg.add_paths() 
    print("FFmpeg and FFprobe binary streams linked successfully.\n")
except ImportError:
    print("Warning: static-ffmpeg package is missing. Run 'pip install static-ffmpeg' first.")

from pydub import AudioSegment

# --- WEIRD FRACTAL FILTER PARAMETERS ---
TARGET_SAMPLE_RATE = 22000  # Resample directly to your 22 kHz clock
COMB_DELAY_MS = 14         # Metallic laser-flange delay loop
MODULATION_SPEED_HZ = 8    # Speed of the gating stutter pulse

def shorten_filename(name):
    """Applies strict structural abbreviations to filename strings"""
    name = name.replace("The ", "T_").replace("the ", "T_")
    name = name.replace("World_Map", "WM_x.")
    name = name.replace("Fledgling_Fields", "FF_x..rst")
    name = name.replace("Castle_Collapse", "CC_x..rst")
    name = name.replace("extracted_", "EX_")
    name = name.replace("master", "M")
    return "".join(c for c in name if c.isalnum() or c in "._-").strip()

def apply_strange_modulation():
    if len(sys.argv) < 2:
        print("--- DRAG & DROP STRANGE MODULATOR TOOL ---")
        print("Status: Active and waiting.")
        print("\nHow to use:")
        print("1. Grab any audio file on your computer (.mp3, .wav, .ogg, .flac).")
        print("2. Drag it directly on top of this script file and let go!")
        return

    for file_idx in range(1, len(sys.argv)):
        input_file_path = sys.argv[file_idx]
        
        if not os.path.exists(input_file_path):
            print(f"Error: Could not locate the file segment at: {input_file_path}")
            continue

        # Anchor pathing parameters straight to the original input file location directory
        file_dir = os.path.dirname(os.path.abspath(input_file_path))
        base_name = os.path.basename(input_file_path)
        name_no_ext, original_ext = os.path.splitext(base_name)
        
        # Apply the short abbreviation filter to the output string name
        shorted_name = shorten_filename(name_no_ext)
        output_filename = f"{shorted_name}_STRANGE_MOD_22kHz{original_ext}"
        output_path = os.path.join(file_dir, output_filename)

        print(f"Processing File [{file_idx}/{len(sys.argv)-1}]: {base_name}")
        
        try:
            # Load the raw audio container directly as STEREO to keep phase channels wide
            clean_ext = original_ext.lower().replace(".", "")
            base_audio = AudioSegment.from_file(input_file_path, format=clean_ext).set_channels(2)
            
            # --- TIER 1: THE STEREO WIDE ECHO GRID (COMB FILTER) ---
            print(" -> Engineering non-canceling stereo inverted echo arrays...")
            delayed_clone = base_audio[COMB_DELAY_MS:]
            
            # The Magic Fix: Pan the original to the Left (-1.0) and the inverted clone to the Right (1.0)
            # This allows the laser-flange phase effect to interact without colliding and zeroing out!
            left_channel = base_audio.pan(-1.0)
            right_channel = delayed_clone.invert_phase().pan(1.0)
            
            # Overlay them securely as independent stereo channels
            comb_filtered = left_channel.overlay(right_channel, position=COMB_DELAY_MS)
            
            # --- TIER 2: STREAM-SAFE FRACTIONAL CHUNK GATING (THE STUTTER) ---
            print(f" -> Applying dynamic volume modulation grid ({MODULATION_SPEED_HZ}Hz)...")
            chunk_duration_ms = int(1000 / (MODULATION_SPEED_HZ * 2))
            
            processed_chunks = []
            for i in range(0, len(comb_filtered), chunk_duration_ms):
                chunk = comb_filtered[i:i + chunk_duration_ms]
                # Introduce the gating effect cleanly via native decibel drops
                if (i // chunk_duration_ms) % 2 == 0:
                    chunk = chunk - 15.0  
                processed_chunks.append(chunk)
            
            print(" -> Recompiling processed sound blocks natively...")
            stitched_audio = AudioSegment.empty()
            for chunk in processed_chunks:
                stitched_audio += chunk
            
            # --- TIER 3: CONSOLIDATION & DOWN-SAMPLING ---
            print(f" -> Down-mixing final master to Mono @ {TARGET_SAMPLE_RATE}Hz...")
            # Down-mix to mono safely at the absolute end, locking in the altered phase data!
            final_master = stitched_audio.set_channels(1).set_frame_rate(TARGET_SAMPLE_RATE)
            
            print(f" -> Hard-exporting populated bitstream to destination folder...")
            final_master.export(output_path, format=clean_ext)
            print(f"Success! Rebuilt track saved cleanly right next to your original file at:")
            print(f" -> {output_path}\n")
            
        except Exception as e:
            print(f"❌ Failed to mutate track data. Detail: {e}\n")

if __name__ == "__main__":
    try:
        apply_strange_modulation()
    except Exception as e:
        print(f"A runtime pipeline exception occurred: {e}")
        
    print("----------------------------------------")
    input("Process complete. Press ENTER to close this window...")