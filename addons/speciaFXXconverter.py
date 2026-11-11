import os
import sys
import math
import array

try:
    import static_ffmpeg
    print("Initializing embedded FFmpeg environments...")
    static_ffmpeg.add_paths() 
    print("FFmpeg and FFprobe binary streams linked successfully.\n")
except ImportError:
    print("Warning: static-ffmpeg package is missing. Run 'pip install static-ffmpeg' first.")

from pydub import AudioSegment

# --- WEIRD RETRO MODULATOR PARAMETERS ---
TARGET_SAMPLE_RATE = 22000  # Resample directly to your 22 kHz clock
MODULATION_SPEED_HZ = 8    # Speed of the gating stutter pulse (8 Hz)

def shorten_filename(name):
    """Applies strict structural abbreviations to game asset filename strings"""
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

        print(f"Processing Track [{file_idx}/{len(sys.argv)-1}]: {base_name}")
        
        try:
            # Load the raw audio container directly
            clean_ext = original_ext.lower().replace(".", "")
            audio_segment = AudioSegment.from_file(input_file_path, format=clean_ext)
            
            # Standardize track properties to signed 16-bit 22kHz Mono FIRST to secure data type alignment
            print(f" -> Consolidating channel arrays into Mono @ {TARGET_SAMPLE_RATE}Hz...")
            base_audio = audio_segment.set_channels(1).set_frame_rate(TARGET_SAMPLE_RATE).set_sample_width(2)
            
            # --- TIER 1: HIGH-SPEED NATIVE BINARY AMPLITUDE MODULATION (THE RETRO STUTTER) ---
            print(f" -> Injecting mathematical modulation grid ({MODULATION_SPEED_HZ}Hz)...")
            
            # Extract the raw signed 16-bit short soundwave arrays natively ('h' typecode)
            raw_samples = array.array('h', base_audio.raw_data)
            num_samples = len(raw_samples)
            sample_rate = base_audio.frame_rate
            
            # Create a dynamic array byte modifier to adjust the waveforms directly
            modified_samples = list(raw_samples)
            
            # Apply an internal LFO wave loop directly to the sample amplitude arrays without phase cancellation
            for i in range(num_samples):
                timestamp = i / sample_rate
                # Generate a hard square-wave pulsing multiplier using sine wave boundaries
                oscillator_val = math.sin(2 * math.pi * MODULATION_SPEED_HZ * timestamp)
                
                # If the oscillator is in the negative phase, drop the sample volume cleanly by 85%
                if oscillator_val < 0:
                    modified_samples[i] = int(modified_samples[i] * 0.15)
                    
            # Rebuild the modified sample array back into a standard, stable audio bytes payload
            import struct
            packed_data = struct.pack(f"<{len(modified_samples)}h", *modified_samples)
            final_master = base_audio._spawn(packed_data)
            
            # Absolute write destination execution
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