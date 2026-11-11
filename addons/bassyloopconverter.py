import os
import sys

try:
    import static_ffmpeg
    print("Initializing embedded FFmpeg environments...")
    static_ffmpeg.add_paths() 
    print("FFmpeg and FFprobe linked successfully.\n")
except ImportError:
    print("Warning: static-ffmpeg package is missing. Run 'pip install static-ffmpeg' first.")

from pydub import AudioSegment

# --- AUDIO METRIC PARAMETERS ---
TARGET_SAMPLE_RATE = 22000  # 22 kHz clock
LOOP_START_MS = 10000       # 10 seconds in milliseconds
LOOP_END_MS = 15000         # 15 seconds in milliseconds
TARGET_DURATION_MS = 180000 # Exactly 3 minutes (180,000 ms)

def shorten_filename(name):
    """Applies strict structural abbreviations to filename strings"""
    name = name.replace("The ", "T_").replace("the ", "T_")
    name = name.replace("World_Map", "WM_x.")
    name = name.replace("Fledgling_Fields", "FF_x..rst")
    name = name.replace("Castle_Collapse", "CC_x..rst")
    name = name.replace("extracted_", "EX_")
    name = name.replace("master", "M")
    # Clean up redundant double spacing or underscores
    return "".join(c for c in name if c.isalnum() or c in "._-").strip()

def build_loop_pipeline():
    if len(sys.argv) < 2:
        print("--- DRAG & DROP LO-FI LOOPER TOOL ---")
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

        file_dir = os.path.dirname(input_file_path)
        base_name = os.path.basename(input_file_path)
        name_no_ext, original_ext = os.path.splitext(base_name)
        
        # Apply the short abbreviation matrix block to the output string name
        shorted_name = shorten_filename(name_no_ext)
        output_filename = f"{shorted_name}_22kHz_3Min_Loop{original_ext}"
        output_path = os.path.join(file_dir, output_filename)

        print(f"Processing Track [{file_idx}/{len(sys.argv)-1}]: {base_name}")
        
        try:
            # Load the raw audio container directly
            clean_ext = original_ext.lower().replace(".", "")
            audio_segment = AudioSegment.from_file(input_file_path, format=clean_ext)
            
            # Verify file has enough data duration to slice the 10-15s segment
            if len(audio_segment) < LOOP_END_MS:
                print(f"❌ Error: Track is too short ({len(audio_segment)/1000:.2f}s). Must be at least 15s long.")
                continue

            print(" -> Slicing audio boundary layer exactly between 0:10 and 0:15...")
            # Slice the exact 5-second block natively
            five_second_chunk = audio_segment[LOOP_START_MS:LOOP_END_MS]
            
            print(" -> Building 3-minute continuous repetition block...")
            # Calculate how many full loops are required to fill 3 minutes (180,000ms / 5,000ms = 36 loops)
            loops_needed = int(TARGET_DURATION_MS / len(five_second_chunk))
            looped_audio = five_second_chunk * loops_needed
            
            # Strict boundary enforcement: crop or pad to ensure it hits exactly 3:00.000
            final_loop_block = looped_audio[:TARGET_DURATION_MS]
            
            print(f" -> Merging channel array to Mono and downsampling to {TARGET_SAMPLE_RATE}Hz...")
            # Flatten to Mono and drop sample clock to 22,000 Hz natively
            mastered_audio = final_loop_block.set_channels(1).set_frame_rate(TARGET_SAMPLE_RATE)
            
            print(f" -> Compiling mastered track to file: {output_filename}")
            mastered_audio.export(output_path, format=clean_ext)
            print("Success! Loop mastering complete.\n")
            
        except Exception as e:
            print(f"❌ Failed to process track data. Detail: {e}\n")

if __name__ == "__main__":
    try:
        build_loop_pipeline()
    except Exception as e:
        print(f"A pipeline runtime error occurred: {e}")
        
    print("----------------------------------------")
    input("Process complete. Press ENTER to close this window...")