import os
import uuid

# Create a temporary folder to store in-memory files in, which is removed after use.
# Takes a dictionary of the form {filename: bytes} so it also works for non-streamlit applications.
# Note that this removes all file metadata.
class TempDir:
    def __init__(self, files):
        # This assumes Unix-like filesystem.
        # Consider using the tempfile module to make it cross-platform
        self.tmpdir = os.path.join("/tmp/upload/", str(uuid.uuid4()))
        self.files = files

    def __enter__(self):
        os.makedirs(self.tmpdir)
        for filename, file_bytes in self.files.items():
            file_path = os.path.join(self.tmpdir, filename)
            with open(file_path, 'wb') as f:
                f.write(file_bytes)
        return self.tmpdir

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # for filename in self.files.keys():
        #     file_path = os.path.join(self.tmpdir, filename)
        #     os.remove(file_path)
        # os.rmdir(self.tmpdir)
        return False