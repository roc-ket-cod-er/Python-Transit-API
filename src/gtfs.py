import ssl
import requests
import urllib3
import zipfile
from os import remove
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = {
    "GRT": {
        "ALL": "https://webapps.regionofwaterloo.ca/api/grt-routes/api/staticfeeds/0",
    },
    "GO": {
        "ALL": "https://assets.metrolinx.com/raw/upload/Documents/Metrolinx/Open%20Data/GO-GTFS.zip"
    }
}

class WeakDHAdapter(HTTPAdapter):
    """HTTPAdapter that lowers OpenSSL's security level and disables
    certificate verification entirely — most permissive TLS possible."""
    def init_poolmanager(self, *args, **kwargs):
        ctx = create_urllib3_context()
        ctx.set_ciphers("DEFAULT@SECLEVEL=1")
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        kwargs["ssl_context"] = ctx
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        ctx = create_urllib3_context()
        ctx.set_ciphers("DEFAULT@SECLEVEL=1")
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        kwargs["ssl_context"] = ctx
        return super().proxy_manager_for(*args, **kwargs)


def update(agencies):
    for agency in agencies.split("&&"):
        try:
            keys = list(URL[agency].keys())
        except KeyError as e:
            print(f"ERROR: {e}")
            continue

        session = requests.Session()
        session.mount("https://", WeakDHAdapter())

        for key in keys:
            url = URL[agency][key]
            local_path = f"GTFS\\{agency}\\{key}" if key != "ALL" else f"GTFS\\{agency}"
            Path(local_path).mkdir(parents=True, exist_ok=True)
            print(f"Fetching {url}")

            response = session.get(url, verify=False)
            if response.status_code == 200:
                print(f"wrtiting to {local_path + "\\data.zip"}")
                with open(local_path + r"\data.zip", "wb") as file:
                    file.write(response.content)
                print("Download complete!")
            else:
                print(f"Failed to download. Status code: {response.status_code}")
                continue

            with zipfile.ZipFile(local_path + "\\data.zip", 'r') as zip_ref:
                zip_ref.extractall(local_path)

            remove(local_path + "\\data.zip")


if __name__ == '__main__':
    print("\n\n\n")
    update("GO")
    print("\n\n\n")