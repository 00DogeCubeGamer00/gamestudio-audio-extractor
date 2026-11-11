import os
import sys
import math
import struct

try:
    import static_ffmpeg
    print("Initializing embedded FFmpeg environments...")
    static_ffmpeg.add_paths() 
    print("FFmpeg and FFprobe linked successfully.\n")
except ImportError:
    print("Warning: static-ffmpeg package is missing. Run 'pip install static-ffmpeg' first.")

from pydub import AudioSegment

# --- WEIRD FRACTAL FILTER PARAMETERS ---
TARGET_SAMPLE_RATE = 22000  # Resample to your vintage 22 kHz clock
COMB_DELAY_MS = 14         # Tiny time shift that forces the hollow laser-flange sound
MODULATION_SPEED_HZ = 8    # The stuttering pulse speed (Higher = faster robotic vibration)

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

        # FIXED: Anchor path directly to the original DROPPED file folder to prevent Windows Temp folder diversion
        file_dir = os.path.dirname(os.path.abspath(input_file_path))
        base_name = os.path.basename(input_file_path)
        name_no_ext, original_ext = os.path.splitext(base_name)
        
        # Apply the short abbreviation filter to the output string name
        shorted_name = shorten_filename(name_no_ext)
        output_filename = f"{shorted_name}_STRANGE_MOD_22kHz{original_ext}"
        
        # FIXED: Forces the output to write right next to the original song file
        output_path = os.path.join(file_dir, output_filename)

        print(f"Processing Track [{file_idx}/{len(sys.argv)-1}]: {base_name}")
        
        try:
            # Load the raw audio container directly
            clean_ext = original_ext.lower().replace(".", "")
            audio_segment = AudioSegment.from_file(input_file_path, format=clean_ext)
            
            # --- TIER 1: THE INVERTED ECHO GRID (COMB FILTER) ---
            print(" -> Engineering inverted echo arrays...")
            delayed_clone = audio_segment[COMB_DELAY_MS:]
            inverted_clone = delayed_clone.invert_phase()
            # Combine waves to create a metallic, hollow, ring-modulated tone
            comb_filtered = audio_segment.overlay(inverted_clone, position=COMB_DELAY_MS)
            
            # --- TIER 2: HIGH-SPEED MATHEMATICAL VOLUME OSCILLATION ---
            print(f" -> Injecting {MODULATION_SPEED_HZ}Hz pulsing modulation grid...")
            # Down-mix to Mono and resample to exactly 22,000 Hz first to speed up processing
            final_master = comb_filtered.set_channels(1).set_frame_rate(TARGET_SAMPLE_RATE)
            
            # Extract raw audio frame data to apply the oscillator loop directly
            raw_samples = final_master.get_array_of_samples()
            num_samples = len(raw_samples)
            sample_rate = final_master.frame_rate
            
            # Create a dynamic array byte modifier
            modified_samples = list(raw_samples)
            
            # Apply an internal LFO wave loop directly to the sample amplitude arrays
            for i in range(num_samples):
                t = i / sample_rate
                oscillator_val = math.sin(2 * math.pi * MODULATION_SPEED_HZ * t)
                volume_multiplier = 0.25 if oscillator_val < 0 else 1.0
                modified_samples[i] = int(modified_samples[i] * volume_multiplier)
                
            # Reconstitute the mutated sample data array back into a standard audio structure
            final_master = final_master._spawn(struct.pack(f"<{len(modified_samples)}h", *modified_samples))
            
            # Absolute write destination enforcement
            print(f" -> Hard-exporting file straight to destination folder...")
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