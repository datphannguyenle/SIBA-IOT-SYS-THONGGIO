#!/usr/bin/env python3
"""Encode the original generated PNG as WebP for the TB descriptor size limit.

Transport optimization only: same canvas dimensions/composition; preserve original PNG.
Run locally; no external image service or ThingsBoard calls.
"""
import base64
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tests"))
from webdriver_support import ROOT, Browser, StaticServer


def main():
    with StaticServer() as server:
        browser = Browser()
        try:
            browser.open(server.base_url + "/dashboard/index.html#default")
            browser.run("document.querySelector('.barn-illustration img').src = 'assets/ventilation-barn-v1.png'")
            browser.wait_for("var img=document.querySelector('.barn-illustration img'); return img && img.complete && img.naturalWidth > 0")
            encoded = browser.run("""
              var img=document.querySelector('.barn-illustration img');
              var canvas=document.createElement('canvas');
              canvas.width=img.naturalWidth; canvas.height=img.naturalHeight;
              canvas.getContext('2d').drawImage(img,0,0);
              return canvas.toDataURL('image/webp',0.88);
            """)
            if not encoded.startswith("data:image/webp;base64,"):
                raise RuntimeError("WebP encoding unsupported")
            data = base64.b64decode(encoded.split(",", 1)[1])
            target = ROOT / "dashboard/assets/ventilation-barn-v1.webp"
            target.write_bytes(data)
            print("WebP bytes:", len(data))
        finally:
            browser.close()


if __name__ == "__main__":
    main()
