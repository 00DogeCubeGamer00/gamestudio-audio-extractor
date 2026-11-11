
Audio Addons: Bass Boost, Loudness & Auto-Re-Encoder

A collection of companion utilities designed to take your extracted game tracks (or any standard audio files) and automatically re-encode them with heavier bass, boosted volume, or custom sound effects.
Instead of manually tweaking tracks one by one in an audio editor, just drop your files into the input folder (or drag them onto the script) and let the processor handle the rest.

What's Included

• Bass-Boosted Edition: Enhances low-end frequencies to give classic game loops and sound effects a heavier, deeper punch.
• Louder / Gain-Boosted Edition: Pushes overall track loudness and volume levels so quieter legacy .ogg and .wav files hit harder.
• Distorted / Loop Variants: Applies gritty overdrive and loop-ready processing for experimental remixes.
• Auto Re-Encoder (Drag & Drop): Automatically converts and re-encodes audio files dropped into it into clean, ready-to-play output tracks.

How to Use It

1. Extract Your Audio First (Optional): Run the main 3D Gamestudio extractor to pull your .ogg, .wav, or .mp3 files from the game, or gather any audio files you want to process.
2. Feed Your Files In:
	• Folder Method: Place your audio files directly into the addon's designated input folder (or update the input/output folder paths at the top of the script) and run the .py file.
	• Drag-and-Drop Method: Drag your audio files directly onto the converter script icon to trigger automatic re-encoding.
3. Grab Your New Tracks: Once processing finishes, open the output folder to find your newly re-encoded, bass-boosted, or louder audio files.

Requirements

• Python 3: Must be installed and added to your system PATH (see the main repository README.md for first-time setup steps).
• Audio Processing Dependencies (If Used): If your variant relies on ffmpeg or a Python audio library (such as pydub), make sure ffmpeg is installed on your PC so the re-encoder can read and write .ogg, .wav, and .mp3 formats smoothly.

Should be good to go afterward.
