import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

def extract_thumbnail(mp3_path: str, output_folder: str) -> str | None:
    """
    Extract embedded album art from an MP3 file.

    Returns:
        Path to the saved thumbnail, or None if not found or failed.
    """

    os.makedirs(output_folder, exist_ok=True)

    try:
        audio = MP3(mp3_path, ID3=ID3)

        if audio.tags is None:
            return None

        for tag in audio.tags.values():
            if isinstance(tag, APIC):
                extension = tag.mime.split("/")[-1]
                filename = os.path.splitext(os.path.basename(mp3_path))[0]
                thumbnail_path = os.path.join(
                    output_folder,
                    f"{filename}.{extension}"
                )

                with open(thumbnail_path, "wb") as image:
                    image.write(tag.data)

                return thumbnail_path

    except Exception:
        # Any failure here should not crash the application
        return None

    return None
        