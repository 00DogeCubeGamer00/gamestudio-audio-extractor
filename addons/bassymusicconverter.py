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

# --- AUTOMATED PROCESSING KNOBS ---
TARGET_SAMPLE_RATE = 32000  # Corrected to exactly 11,000 Hz (11 kHz)
HIGH_CUTOFF_HZ = 22000       # Drops everything above 4kHz entirely for a muffled tone
BASS_BOOST_DB = 6.0         # Optional warm shelf boost to enrich the low end

def convert_dropped_audio():
    # sys.argv stores the file path of any item dragged and dropped onto the script
    if len(sys.argv) < 2:
        print("--- DRAG & DROP MUSIC CONVERTER ---")
        print("Status: Active and waiting.")
        print("\nHow to use:")
        print("1. Grab any audio file on your computer (.mp3, .wav, .ogg, .flac).")
        print("2. Drag it directly on top of this script file and let go!")
        return

    # Process every file that was dropped onto the script
    for file_idx in range(1, len(sys.argv)):
        input_file_path = sys.argv[file_idx]
        
        if not os.path.exists(input_file_path):
            print(f"Error: Could not track down the file at: {input_file_path}")
            continue

        # Extract path information to save the new file right next to the original
        file_dir = os.path.dirname(input_file_path)
        base_name = os.path.basename(input_file_path)
        name_no_ext, original_ext = os.path.splitext(base_name)
        
        # Clean up the extension name for pydub (removes the dot)
        clean_ext = original_ext.lower().replace(".", "")
        if clean_ext == "dat": 
            clean_ext = "mp3"  # Fallback override for raw data blocks

        # Create the final output filename
        output_filename = f"{name_no_ext}_22kHz_Mono_LowPass{original_ext}"
        output_path = os.path.join(file_dir, output_filename)

        print(f"Processing File [{file_idx}/{len(sys.argv)-1}]: {base_name}")
        
        try:
            # Load the raw audio track natively
            audio_segment = AudioSegment.from_file(input_file_path, format=clean_ext)
            
            print(" -> Down-mixing stereo channels to Mono...")
            print(f" -> Resampling digital clock to {TARGET_SAMPLE_RATE} Hz...")
            # 1. Flatten to Mono and resample to exactly 22,000 Hz
            mono_resampled = audio_segment.set_channels(1).set_frame_rate(TARGET_SAMPLE_RATE)
            
            print(f" -> Applying brick-wall high cut at {HIGH_CUTOFF_HZ} Hz...")
            # 2. Apply a double low-pass filter to aggressively strip away the treble
            filtered_audio = mono_resampled.low_pass_filter(HIGH_CUTOFF_HZ).low_pass_filter(HIGH_CUTOFF_HZ)
            
            # 3. Apply a warm bass shelf to give it that deep feel
            low_shelf = filtered_audio.low_pass_filter(200) + BASS_BOOST_DB
            mastered_audio = filtered_audio.overlay(low_shelf)
            
            print(f" -> Exporting mastered track to: {output_filename}")
            # Save the file using its original file format container
            mastered_audio.export(output_path, format=clean_ext)
            print(f"Success! Processed track saved cleanly.\n")
            
        except Exception as e:
            print(f"❌ Failed to convert {base_name}. Detail: {e}\n")

if __name__ == "__main__":
    try:
        convert_dropped_audio()
    except Exception as e:
        print(f"An unexpected exception halted the pipeline: {e}")
        
    print("----------------------------------------")
    input("Process complete. Press ENTER to close this window...")