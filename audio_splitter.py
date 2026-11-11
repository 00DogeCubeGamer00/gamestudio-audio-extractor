import os

# 1. Update this path to point exactly to your TWEotW! game folder!
GAME_DIR = r"C:\TWEotW"
METADATA_PATH = os.path.join(GAME_DIR, "Data", "audio_metadata.dat")
RESOURCE_PATH = os.path.join(GAME_DIR, "Data", "audio_resource.dat")
OUTPUT_DIR = os.path.join(GAME_DIR, "Data", "extracted_TWEotW_audio")

def unpack_dejobaan_game():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created folder: {OUTPUT_DIR}")

    print("Parsing dynamic metadata coordinates...")
    chunks = []
    with open(METADATA_PATH, "r") as meta_file:
        for line in meta_file:
            line = line.strip()
            if not line or line == "-1 -1":
                break
            parts = line.split()
            if len(parts) == 2:
                chunks.append((int(parts[0]), int(parts[1])))

    print(f"Decrypting {len(chunks)} custom audio streams via bitwise NOT...")
    with open(RESOURCE_PATH, "rb") as res_file:
        for index, (offset, length) in enumerate(chunks):
            res_file.seek(offset)
            encrypted_data = res_file.read(length)
            
            # Apply the exact same bitwise NOT (~) unmasking operation
            decrypted_bytes = bytearray((~b) & 0xFF for b in encrypted_data)
            
            # Read the header signatures to sort Ogg loops from short Wav effects
            if decrypted_bytes.startswith(b"OggS"):
                ext = "ogg"
            elif decrypted_bytes.startswith(b"RIFF") or decrypted_bytes.startswith(b"WAVE"):
                ext = "wav"
            else:
                ext = "mp3"
                
            output_filename = os.path.join(OUTPUT_DIR, f"track_{index:03d}.{ext}")
            with open(output_filename, "wb") as out_file:
                out_file.write(decrypted_bytes)
                
    print(f"\nExtraction complete! Check your crisp OGG tracks in: {OUTPUT_DIR}")

if __name__ == "__main__":
    try:
        unpack_dejobaan_game()
    except Exception as e:
        print(f"An error occurred: {e}")
        
    print("\n----------------------------------------")
    input("Press ENTER to close this window...")