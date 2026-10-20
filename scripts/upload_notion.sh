#!/bin/bash
# Upload images to Notion file-upload slots created with the MCP tool notion-create-file-upload.
#
# Usage: upload_notion.sh CROPS_DIR < lines
#   each stdin line: <name> <file_upload_id> <authorization-token-without-"Bearer ">
#   uploads CROPS_DIR/<name>.jpg and prints "<name> <http-code>" (expect 200).
#
# After a 200, attach it with notion-update-page update_properties:
#   {"Image":[{"type":"file_upload","file_upload":{"id":"<file_upload_id>"}}]}
# Slots expire ~10 minutes after creation (see expires_at): upload and attach right away.
set -u
dir=${1:?usage: upload_notion.sh CROPS_DIR < lines}
while read -r name id tok; do
  [ -z "$name" ] && continue
  code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "https://api.notion.com/v1/mcp/file_uploads/$id/send" \
    -H "authorization: Bearer $tok" -F "file=@$dir/$name.jpg;type=image/jpeg" </dev/null)
  echo "$name $code"
done
