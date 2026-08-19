import urequests
import json
import machine
import os

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/CivyHomestead/civy-mesh/main/firmware/pico/"

class OTAUpdater:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        with open(config_path, "r") as f:
            self.config = json.load(f)
            
        self.current_ver = self.config.get("firmware_version", 100)

    def check_and_update(self):
        """Checks GitHub for version bump and pulls updated files."""
        print(f"[OTA] Current Firmware Version: v{self.current_ver}")
        try:
            url = GITHUB_RAW_BASE + "version.json"
            print(f"[OTA] Fetching manifest: {url}")
            res = urequests.get(url)
            
            if res.status_code != 200:
                print(f"[OTA] No version manifest found on repo (HTTP {res.status_code}).")
                res.close()
                return False

            manifest = res.json()
            res.close()
            
            remote_ver = manifest.get("version", self.current_ver)
            files_to_update = manifest.get("files", [])

            if remote_ver > self.current_ver:
                print(f"[OTA] New firmware release found: v{remote_ver}")
                
                # Fetch each updated file listed in the manifest
                for file_name in files_to_update:
                    if not self._download_file(file_name):
                        print(f"[OTA CRITICAL] Failed updating {file_name}. Aborting update.")
                        return False

                # Update local config version
                self.config["firmware_version"] = remote_ver
                with open(self.config_path, "w") as f:
                    json.dump(self.config, f)
                    
                print(f"[OTA] Firmware updated to v{remote_ver}. Triggering system reset...")
                machine.reset()
            else:
                print("[OTA] Device is running latest release.")
                return True

        except Exception as e:
            print(f"[OTA ERROR] Check failed: {e}")
            return False

    def _download_file(self, filename):
        """Downloads updated code to a .tmp file before atomic replacement."""
        try:
            url = GITHUB_RAW_BASE + filename
            print(f"[OTA] Downloading {filename}...")
            res = urequests.get(url)
            
            if res.status_code == 200:
                # Atomic write to temporary file
                tmp_name = filename + ".tmp"
                with open(tmp_name, "w") as f:
                    f.write(res.text)
                res.close()
                
                # Overwrite live module
                try:
                    os.remove(filename)
                except OSError:
                    pass
                os.rename(tmp_name, filename)
                print(f"[OTA] Verified and updated {filename}")
                return True
            res.close()
            return False
        except Exception as err:
            print(f"[OTA ERROR] File write error ({filename}): {err}")
            return False