#!/usr/bin/env python3
"""Read-only EBRULI funnel smoke test. Never submits forms or payments.
Run: python3 -B tools/ebruli_funnel_smoke_20261025.py
"""
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

PUBLIC_PAGE = "https://charlysmoky2010-hub.github.io/ebruli-personal-botanica.html"
FUNCTION = "https://vlgibwclecuhnnrgycnx.supabase.co/functions/v1/ebruli-store?go=commission&locale=de&utm_source=qa_manual"
FORM = "https://form.jotform.com/262621716795061"
ALLOWED_HOSTS = frozenset(("form.jotform.com", "www.jotform.com"))

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None

def read(url):
    request = urllib.request.Request(url, method="GET", headers={"User-Agent":"EBRULI-ReadOnly-FunnelCheck/1.0"})
    opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    try:
        with opener.open(request, timeout=18) as response:
            return response.status, response.headers, response.read(500000).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as err:
        return err.code, err.headers, ""

def safe_form_url(value):
    if not value: return False
    p = urllib.parse.urlparse(value)
    return p.scheme == "https" and p.hostname in ALLOWED_HOSTS and p.path.rstrip("/") == "/262621716795061"

def run():
    failure = False
    print("EBRULI | SALT_OKUNUR_KONTROL | FORM_GONDERIMI=0 | ODEME=0")
    try:
        code, headers, body = read(PUBLIC_PAGE)
        ok = code == 200 and "Personal Botanica" in body and "79" in body
        print("SAYFA:", "OK" if ok else "HATA", "HTTP", code)
        failure |= not ok
        imprint = bool(re.search(r'href\s*=\s*["\'](?:[^"\']*/)?(?:impressum|legal-notice)',body,flags=re.I))
        privacy = bool(re.search(r'href\s*=\s*["\'](?:[^"\']*/)?(?:datenschutz|privacy)',body,flags=re.I))
        print("YASAL_LINKLER:", "IMPRINT_VE_PRIVACY_VAR" if imprint and privacy else "EKSIK")
        if not (imprint and privacy): failure = True
        print("YASAL_METIN_AYRINTILI_INCELEME:", "GEREKLI")
    except Exception as exc:
        print("SAYFA: BAGLANTI_HATASI", type(exc).__name__)
        failure = True
    try:
        code, headers, body = read(FUNCTION)
        ok = code in (301,302,303,307,308) and safe_form_url(headers.get("Location"))
        print("YONLENDIRME:", "OK" if ok else "HATA", "HTTP", code)
        failure |= not ok
    except Exception as exc:
        print("YONLENDIRME: BAGLANTI_HATASI", type(exc).__name__)
        failure = True
    try:
        code, headers, body = read(FORM)
        ok = code == 200 and ("jotform" in body.lower() or "form" in body.lower())
        print("JOTFORM:", "OK" if ok else "HATA", "HTTP", code)
        failure |= not ok
    except Exception as exc:
        print("JOTFORM: BAGLANTI_HATASI", type(exc).__name__)
        failure = True
    print("SONUC:", "TEKNIK_BAGLANTI_ADIMLARI_GECTI" if not failure else "ENGEL_VAR")
    print("UYARI: Link erisimi gercek form gonderimini, hukuki uyumu veya tahsilati kanitlamaz.")
    return 2 if failure else 0

if __name__ == "__main__": sys.exit(run())
