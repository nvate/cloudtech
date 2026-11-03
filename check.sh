#!/usr/bin/env bash
# Checks all lab 1 requirements.
# Usage: bash check.sh

HOST_A=https://site-a.local
HOST_B=https://site-b.local
CURL="curl -sk"

echo "=== 1. HTTP -> HTTPS redirect ==="
curl -sI http://site-a.local/ | grep -Ei "^(HTTP|Location)"

echo
echo "=== 2. Round-robin between two backends (6 requests) ==="
for i in {1..6}; do
  # Extract "backend": "..." using grep and sed instead of jq
  $CURL "$HOST_A/api/notes" | grep -o '"backend":"[^"]*"' | cut -d'"' -f4
done

echo
echo "=== 3. Failover: stop backend-5001, then press Enter ==="
read -r _
for i in {1..6}; do
  code=$($CURL -o /dev/null -w "%{http_code}" "$HOST_A/api/notes")
  echo "status=$code"
done

echo
echo "=== 4. /admin without credentials (expect 401) ==="
$CURL -o /dev/null -w "%{http_code}\n" "$HOST_A/admin"

echo
echo "=== 5. /admin with credentials (expect 200) ==="
$CURL -u admin:secret -o /dev/null -w "%{http_code}\n" "$HOST_A/admin"

echo
echo "=== 6. Rate limit on /api (expect 429 under flood) ==="
for i in {1..30}; do
  $CURL -o /dev/null -w "%{http_code}\n" "$HOST_A/api/notes"
done | sort | uniq -c

echo
echo "=== 7. Virtual hosts: site-b does not serve site-a ==="
echo -n "site-b root:  "
$CURL -o /dev/null -w "%{http_code}\n" "$HOST_B/"
echo -n "site-b /docs: "
$CURL -o /dev/null -w "%{http_code}\n" "$HOST_B/docs/"

echo
echo "=== 8. Custom 404 (expect 404 + custom body) ==="
status=$($CURL -o /dev/null -w "%{http_code}" "$HOST_A/nonexistent-page")
echo "status: $status"
$CURL -s "$HOST_A/nonexistent-page" | grep -q "Page not found" && echo "custom page: OK" || echo "custom page: NOT FOUND"

echo
echo "=== 9. site-b /admin is protected by nothing (expect 404) ==="
$CURL -o /dev/null -w "%{http_code}\n" "$HOST_B/admin"