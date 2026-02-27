#!/usr/bin/env bash
# 用法: NEON_API_KEY="key" NEON_ORG_ID="org-xxx" ./scripts/setup_neon_and_vercel.sh
# 或: ./scripts/setup_neon_and_vercel.sh "你的key" "org-xxx"
set -e
API_KEY="${1:-$NEON_API_KEY}"
ORG_ID="${2:-$NEON_ORG_ID}"
if [ -z "$API_KEY" ]; then
  echo "请设置 NEON_API_KEY 或作为第一个参数传入"
  exit 1
fi
if [ -z "$ORG_ID" ]; then
  echo "请设置 NEON_ORG_ID 或作为第二个参数传入（在 Neon 设置页 Organization 里复制）"
  exit 1
fi

echo "正在用 Neon API 创建项目..."
URL="https://console.neon.tech/api/v2/projects?org_id=$ORG_ID"
RESP=$(curl -s -X POST "$URL" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"project":{"name":"metro-trade","region_id":"aws-us-east-2"}}')

if echo "$RESP" | grep -q "connection_uri"; then
  CONN=$(echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('connection_uri') or d.get('project',{}).get('connection_uri') or '')")
fi
if [ -z "$CONN" ] && echo "$RESP" | grep -q "id"; then
  PROJ_ID=$(echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('project',{}).get('id') or d.get('id',''))")
  if [ -n "$PROJ_ID" ]; then
    echo "项目已创建，正在获取连接串..."
    ENDPOINT=$(curl -s "https://console.neon.tech/api/v2/projects/$PROJ_ID/connection_uri" \
      -H "Accept: application/json" \
      -H "Authorization: Bearer $API_KEY")
    CONN=$(echo "$ENDPOINT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('connection_uri',''))" 2>/dev/null || echo "")
  fi
fi
if [ -z "$CONN" ]; then
  echo "从 create 响应解析连接串..."
  CONN=$(echo "$RESP" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    p = d.get('project') or d
    for k in ['connection_uri','connection_string','database_uri']:
        if p.get(k): print(p[k]); break
    else:
        ep = (p.get('endpoints') or [{}])[0]
        h = ep.get('host')
        if h:
            role = (p.get('roles') or [{}])[0]
            db = (p.get('databases') or [{}])[0]
            print(f\"postgresql://{role.get('name','neondb_owner')}:{role.get('password','')}@{h}/{db.get('name','neondb')}?sslmode=require\")
except Exception as e:
    print('', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null)
fi

if [ -z "$CONN" ]; then
  echo "API 响应: $RESP" | head -c 500
  echo ""
  echo "无法解析连接串，请到 https://console.neon.tech 手动创建项目并复制 Connection string 到 Vercel"
  exit 1
fi

echo "连接串已获取，正在写入 Vercel..."
cd "$(dirname "$0")/.."
npx vercel env rm DATABASE_URL production -y 2>/dev/null || true
echo "$CONN" | npx vercel env add DATABASE_URL production
echo "正在重新部署..."
npx vercel --prod --yes
echo "完成。DATABASE_URL 已配置并已部署。"
