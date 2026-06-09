#!/usr/bin/env bash
# ============================================================================
#  generate-colleague.sh  —  Dinghui AR business-card generator
#  Creates a self-contained AR card folder for one colleague, reachable at
#  https://nas.ivannas.vip:8443/<slug>/
#
#  Usage:
#    ./generate-colleague.sh --slug zhangsan --name 张三 --phone 13800000000 \
#         --wechat wxid_abc --qq 123456 --email a@b.com --address "广东省..."
#
#  Required: --slug --name --phone
#  Optional: --wechat --qq --email --address --org1 --org2 --force
# ============================================================================
set -euo pipefail

ROOT="/vol1/1000/web/card/card"
BASEURL="https://nas.ivannas.vip:8443"
SELFDIR="$(cd "$(dirname "$0")" && pwd)"
PY="$SELFDIR/card_gen.py"
TEMPLATE="$ROOT/ar-live.html"

ORG1="广东省鼎汇项目管理咨询有限公司"
ORG2="深圳鼎汇网络信息有限公司"
SLUG="" NAME="" PHONE="" WECHAT="" QQ="" EMAIL="" ADDRESS="" FORCE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --slug) SLUG="$2"; shift 2;;
    --name) NAME="$2"; shift 2;;
    --phone) PHONE="$2"; shift 2;;
    --wechat) WECHAT="$2"; shift 2;;
    --qq) QQ="$2"; shift 2;;
    --email) EMAIL="$2"; shift 2;;
    --address) ADDRESS="$2"; shift 2;;
    --org1) ORG1="$2"; shift 2;;
    --org2) ORG2="$2"; shift 2;;
    --force) FORCE=1; shift;;
    -h|--help) grep '^#' "$0" | sed 's/^#//'; exit 0;;
    *) echo "Unknown arg: $1" >&2; exit 1;;
  esac
done

# ---- validate -------------------------------------------------------------
[[ -z "$SLUG"  ]] && { echo "Missing --slug"  >&2; exit 1; }
[[ -z "$NAME"  ]] && { echo "Missing --name"  >&2; exit 1; }
[[ -z "$PHONE" ]] && { echo "Missing --phone" >&2; exit 1; }
[[ "$SLUG" =~ ^[a-zA-Z0-9._-]+$ ]] || { echo "slug must be [a-zA-Z0-9._-]" >&2; exit 1; }

DIR="$ROOT/$SLUG"
if [[ -e "$DIR" && $FORCE -ne 1 ]]; then
  echo "Folder already exists: $DIR  (use --force to overwrite)" >&2; exit 1
fi
mkdir -p "$DIR"
echo ">> $DIR"

# ---- 1) symlink shared resources (icons, buttons, video, panels, JS) ------
ln -sfn ../ar-assets "$DIR/ar-assets"
ln -sfn ../vendor    "$DIR/vendor"

# ---- 2) per-person human assets (placeholders until designer/MindAR) ------
python3 "$PY" placeholder --out "$DIR/identity-float.png" --name "$NAME"
ln -sfn ../dinghui-card-front-black-gold.png            "$DIR/card-front.png"
ln -sfn ../tan-junjia-ar-back-new.jpg                   "$DIR/card-back.jpg"
ln -sfn ../targets/dinghui-card-front-back-print-v18.mind "$DIR/target.mind"

# ---- 3) copy template + swap personal fields ------------------------------
ADDR_ENC="$(python3 "$PY" urlencode --text "$ADDRESS")"
cp "$TEMPLATE" "$DIR/ar-live.html"
python3 "$PY" patch-html --file "$DIR/ar-live.html" \
  --name "$NAME" --phone "$PHONE" --wechat "$WECHAT" --qq "$QQ" \
  --email "$EMAIL" --addr-enc "$ADDR_ENC"

# ---- 4) contact.vcf + QR code ---------------------------------------------
python3 "$PY" vcf --out "$DIR/contact.vcf" --name "$NAME" --phone "$PHONE" \
  --wechat "$WECHAT" --qq "$QQ" --email "$EMAIL" --address "$ADDRESS" \
  --org1 "$ORG1" --org2 "$ORG2"
python3 "$PY" qr  --out "$DIR/qr.png" --url "$BASEURL/$SLUG/"

# ---- 5) publish as index.html ---------------------------------------------
cp "$DIR/ar-live.html" "$DIR/index.html"

# ---- TODO note for the human-made assets ----------------------------------
cat > "$DIR/_REPLACE_THESE.txt" <<EOF
Human-made assets to drop into this folder for $NAME ($SLUG):
  identity-float.png  -> transparent PNG of the name "$NAME" (currently auto-placeholder)
  card-front.png      -> front card design  (currently symlinked to Ivan's)
  card-back.jpg       -> back card design   (currently symlinked to Ivan's)
  target.mind         -> MindAR target file (currently symlinked to Ivan's)
Page URL: $BASEURL/$SLUG/
EOF

echo "------------------------------------------------------------"
echo "DONE  ->  $BASEURL/$SLUG/"
echo "QR    ->  $DIR/qr.png"
echo "Still needs human assets: see $DIR/_REPLACE_THESE.txt"
echo "------------------------------------------------------------"
