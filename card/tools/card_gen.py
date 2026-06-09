#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helper for the Dinghui AR business-card generator."""
import argparse, re, sys, urllib.parse

FONT_CJK = "/vol1/@appcenter/Jellyfin/share/fonts/truetype/wqy/wqy-zenhei.ttc"

# Values baked into the master template (ar-live.html) = Ivan's card.
OLD_NAME   = "谭俊佳"
OLD_PHONE  = "13692233879"
OLD_WECHAT = "cyclone_2006"
OLD_QQ     = "304514421"
OLD_EMAIL  = "ivan.tan0528@gmail.com"


def cmd_urlencode(a):
    sys.stdout.write(urllib.parse.quote(a.text or ""))


def cmd_patch_html(a):
    with open(a.file, encoding="utf-8") as f:
        h = f.read()
    h = h.replace(OLD_NAME, a.name)
    h = h.replace(OLD_PHONE, a.phone)
    if a.wechat:
        h = h.replace(OLD_WECHAT, a.wechat)
    if a.qq:
        h = h.replace(OLD_QQ, a.qq)
    if a.email:
        h = h.replace(OLD_EMAIL, a.email)
    # Repoint per-person assets to local files inside the colleague folder.
    h = h.replace("ar-assets/identity-float.png", "identity-float.png")
    h = re.sub(r"dinghui-card-front-black-gold\.png(\?v=\d+)?", "card-front.png", h)
    h = h.replace("tan-junjia-ar-back-new.jpg", "card-back.jpg")
    h = re.sub(r"targets/dinghui-card-front-back-print-v18\.mind(\?v=\d+)?",
               "target.mind", h)
    if a.addr_enc:
        h = re.sub(r"(maps\.apple\.com/\?q=)[^\"']*", r"\1" + a.addr_enc, h)
    with open(a.file, "w", encoding="utf-8") as f:
        f.write(h)
    print("patched", a.file)


def cmd_vcf(a):
    name = a.name
    surname = name[0] if name else ""
    given = name[1:] if len(name) > 1 else ""
    notes = []
    if a.wechat: notes.append("微信号: " + a.wechat)
    if a.qq:     notes.append("QQ号: " + a.qq)
    if a.org2:   notes.append("第二公司: " + a.org2)
    lines = ["BEGIN:VCARD", "VERSION:3.0",
             "PRODID:-//Dinghui Electronic Business Card//CN",
             "N;CHARSET=UTF-8:%s;%s;;;" % (surname, given),
             "FN;CHARSET=UTF-8:" + name,
             "ORG;CHARSET=UTF-8:%s;%s" % (a.org1, a.org2),
             "TEL;TYPE=CELL:" + a.phone]
    if a.email:   lines.append("EMAIL;TYPE=INTERNET:" + a.email)
    if a.address: lines.append("ADR;TYPE=WORK;CHARSET=UTF-8:;;%s;;;;" % a.address)
    if notes:     lines.append("NOTE;CHARSET=UTF-8:" + " | ".join(notes))
    if a.wechat:  lines.append("X-WECHAT:" + a.wechat)
    if a.qq:      lines.append("X-QQ:" + a.qq)
    lines.append("END:VCARD")
    with open(a.out, "w", encoding="utf-8") as f:
        f.write("\r\n".join(lines) + "\r\n")
    print("wrote", a.out)


def cmd_qr(a):
    import qrcode
    qrcode.make(a.url).save(a.out)
    print("wrote", a.out)


def cmd_placeholder(a):
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1000, 360
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_CJK, 180)
        small = ImageFont.truetype(FONT_CJK, 26)
    except Exception:
        font = small = ImageFont.load_default()
    bbox = d.textbbox((0, 0), a.name, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((W - tw) / 2 - bbox[0], (H - th) / 2 - bbox[1]),
           a.name, font=font, fill=(212, 175, 110, 255))
    d.text((20, H - 38), "PLACEHOLDER - replace with designer PNG",
           font=small, fill=(170, 170, 170, 200))
    img.save(a.out)
    print("wrote", a.out)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("urlencode"); s.add_argument("--text", default="")
    s.set_defaults(fn=cmd_urlencode)

    s = sub.add_parser("patch-html")
    s.add_argument("--file", required=True); s.add_argument("--name", required=True)
    s.add_argument("--phone", required=True); s.add_argument("--wechat", default="")
    s.add_argument("--qq", default=""); s.add_argument("--email", default="")
    s.add_argument("--addr-enc", dest="addr_enc", default="")
    s.set_defaults(fn=cmd_patch_html)

    s = sub.add_parser("vcf")
    s.add_argument("--out", required=True); s.add_argument("--name", required=True)
    s.add_argument("--phone", required=True); s.add_argument("--wechat", default="")
    s.add_argument("--qq", default=""); s.add_argument("--email", default="")
    s.add_argument("--address", default=""); s.add_argument("--org1", default="")
    s.add_argument("--org2", default=""); s.set_defaults(fn=cmd_vcf)

    s = sub.add_parser("qr"); s.add_argument("--out", required=True)
    s.add_argument("--url", required=True); s.set_defaults(fn=cmd_qr)

    s = sub.add_parser("placeholder"); s.add_argument("--out", required=True)
    s.add_argument("--name", required=True); s.set_defaults(fn=cmd_placeholder)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
