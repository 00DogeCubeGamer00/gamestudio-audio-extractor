import os
from pydub import AudioSegment

# Path variables setup – update this path string to point to the A6/Demo folder you are currently targetings!
GAME_DIR = r"C:\KLECTIT"
METADATA_PATH = os.path.join(GAME_DIR, "Data", "audio_metadata.dat")
RESOURCE_PATH = os.path.join(GAME_DIR, "Data", "audio_resource.dat")
OUTPUT_DIR = os.path.join(GAME_DIR, "Data", "extracted_mastered_audio")

def run_mastering_pipeline():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Mastering folder built successfully at: {OUTPUT_DIR}")

    print("Parsing asset coordinates table...")
    chunks = []
    with open(METADATA_PATH, "r") as meta_file:
        for line in meta_file:
            line = line.strip()
            if not line or line == "-1 -1":
                break
            parts = line.split()
            if len(parts) == 2:
                chunks.append((int(parts[0]), int(parts[1])))

    print(f"Processing {len(chunks)} structural data nodes...")
    with open(RESOURCE_PATH, "rb") as res_file:
        for index, (offset, length) in enumerate(chunks):
            res_file.seek(offset)
            encrypted_data = res_file.read(length)
            
            # Apply your verified A6/A7 bitwise inversion bypass filter
            decrypted_bytes = bytearray((~b) & 0xFF for b in encrypted_data)
            
            # Temp staging file used to load binary array data safely into the audio parser
            temp_file_path = os.path.join(OUTPUT_DIR, f"temp_{index}.raw")
            with open(temp_file_path, "wb") as temp_out:
                temp_file.write(decrypted_bytes)
                
            # Automatically assign structural header tags based on unmasked data blocks
            if decrypted_bytes.startswith(b"OggS"):
                src_format = "ogg"
            elif decrypted_bytes.startswith(b"RIFF") or decrypted_bytes.startswith(b"WAVE"):
                src_format = "wav"
            else:
                src_format = "mp3"

            try:
                # Load the raw audio frame layout into the processor matrix
                audio_stream = AudioSegment.from_file(temp_file_path, format=src_format)
                track_duration = audio_stream.duration_seconds
                
                # Resample the active frame rate frequency to exactly 33200Hz
                resampled_stream = audio_stream.set_frame_rate(33200)
                
                # Execute automated sorting based on your duration metrics
                if track_duration > 60.0:
                    # Tracks over 1:00 min convert directly to Lossless FLAC format
                    output_filename = f"track_{index:02d}_master.flac"
                    target_path = os.path.join(OUTPUT_DIR, output_filename)
                    resampled_stream.export(target_path, format="flac")
                    print(f" -> Exported Lossless FLAC Master [{track_duration:.1f}s]: {output_filename}")
                else:
                    # Shorter tracks replace OGG and convert to clean WAV files
                    output_filename = f"track_{index:02d}_master.wav"
                    target_path = os.path.join(OUTPUT_DIR, output_filename)
                    resampled_stream.export(target_path, format="wav")
                    print(f" -> Exported Resampled WAV Track [{track_duration:.1f}s]: {output_filename}")
                    
            except Exception as e:
                print(f"Skipping block index {index:02d}: Stream calculation error. Details: {e}")
            finally:
                # Clean up the local temp workspace files
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

    print("\nDone! All files unmasked, resampled to 33200Hz, and cleanly sorted!")

if __name__ == "__main__":
    try:
        run_mastering_pipeline()
    except Exception as e:
        print(f"An unexpected data pipeline termination occurred: {e}")
        
    print("\n----------------------------------------")
    input("Process complete. Press ENTER to close this window...")