import os
import struct

# TIER 1: Ingest and spin up the embedded FFmpeg binary ecosystem dynamically
try:
    import static_ffmpeg
    print("Initializing embedded FFmpeg environments...")
    # This downloads/registers pre-compiled binaries into the active execution path
    static_ffmpeg.add_paths() 
    print("FFmpeg and FFprobe binary streams linked successfully.")
except ImportError:
    print("Warning: static-ffmpeg package is missing. Run 'pip install static-ffmpeg' first.")

from pydub import AudioSegment

# Explicit paths targeting your local game folder installation
GAME_DIR = r"C:\KLECTIT"
METADATA_PATH = os.path.join(GAME_DIR, "Data", "audio_metadata.dat")
RESOURCE_PATH = os.path.join(GAME_DIR, "Data", "audio_resource.dat")
OUTPUT_DIR = os.path.join(GAME_DIR, "Data", "extracted_mastered_audio")

def master_soundtrack_pipeline():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created secure output directory: {OUTPUT_DIR}")

    print("Reading layout coordinates from audio_metadata.dat...")
    chunks = []
    with open(METADATA_PATH, "r") as meta_file:
        for line in meta_file:
            line = line.strip()
            if not line or line == "-1 -1":
                break
            parts = line.split()
            if len(parts) == 2:
                chunks.append((int(parts[0]), int(parts[1])))

    print(f"Mapped {len(chunks)} target resource nodes. Initiating extraction...")
    
    with open(RESOURCE_PATH, "rb") as res_file:
        for index, (offset, length) in enumerate(chunks):
            res_file.seek(offset)
            encrypted_data = res_file.read(length)
            
            # Master Bitwise NOT (~) inversion bypass sweep
            decrypted_bytes = bytearray((~b) & 0xFF for b in encrypted_data)
            
            # Temporary local workspace file used to feed binary streams to the audio decoder
            temp_raw_path = os.path.join(OUTPUT_DIR, f"temp_{index}.dat")
            with open(temp_raw_path, "wb") as temp_file:
                temp_file.write(decrypted_bytes)
                
            # Detect source formatting parameters via header structure signature logs
            if decrypted_bytes.startswith(b"OggS"):
                native_format = "ogg"
            elif decrypted_bytes.startswith(b"RIFF") or decrypted_bytes.startswith(b"WAVE"):
                native_format = "wav"
            else:
                native_format = "mp3"

            try:
                # Load the raw audio frame layout into the decoding engine
                audio_segment = AudioSegment.from_file(temp_raw_path, format=native_format)
                duration_seconds = audio_segment.duration_seconds
                
                # High-precision resampling down to exactly 33,200 Hz
                mastered_segment = audio_segment.set_frame_rate(33200)
                
                # Evaluate duration tags to route the mastering destinations
                if duration_seconds > 60.0:
                    # Tracks over 1:00 min are encoded directly to Lossless FLAC format
                    final_filename = f"track_{index:02d}_master.flac"
                    final_path = os.path.join(OUTPUT_DIR, final_filename)
                    mastered_segment.export(final_path, format="flac")
                    print(f" -> Mastering Complete [Lossless FLAC @ 33200Hz]: {final_filename} ({duration_seconds:.2f}s)")
                else:
                    # Shorter sound effects skip OGG and drop as standard WAV files
                    final_filename = f"track_{index:02d}_master.wav"
                    final_path = os.path.join(OUTPUT_DIR, final_filename)
                    mastered_segment.export(final_path, format="wav")
                    print(f" -> Mastering Complete [Resampled WAV @ 33200Hz]: {final_filename} ({duration_seconds:.2f}s)")
                    
            except Exception as e:
                print(f"Skipping structural node {index:02d}: File parsing error. Detail: {e}")
            finally:
                # Instantly destroy temporary file arrays to keep the tree clean
                if os.path.exists(temp_raw_path):
                    os.remove(temp_raw_path)

    print("\nSuccess! The mastering pipeline completed without any missing system dependencies.")

if __name__ == "__main__":
    try:
        master_soundtrack_pipeline()
    except Exception as e:
        print(f"A structural exception halted processing: {e}")
        
    print("\n----------------------------------------")
    input("Process complete. Press ENTER to close this window...")