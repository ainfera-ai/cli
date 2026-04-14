#!/bin/bash
# Ainfera CLI — Investor Pitch Demo
#
# Usage:
#   bash scripts/demo.sh
#
# Walks through the full CLI experience live during a pitch:
# platform status, listing agents, creating an agent, scaffolding
# a local ainfera.yaml, deploying, and checking a trust score.
#
# Requires:
#   - `ainfera` installed (pip install ainfera)
#   - `ainfera auth login` already run so a valid API key is in ~/.ainfera/config.yaml

set -e

AGENT_NAME="${AINFERA_DEMO_AGENT_NAME:-demo-pitch-agent}"
PAUSE="${AINFERA_DEMO_PAUSE:-2}"

echo "═══════════════════════════════════════"
echo "  Ainfera CLI — Live Demo"
echo "═══════════════════════════════════════"
echo ""

echo "1. Check platform status..."
ainfera status
echo ""
sleep "$PAUSE"

echo "2. List agents on the platform..."
ainfera agents list
echo ""
sleep "$PAUSE"

echo "3. Create a new agent..."
ainfera agents create \
  --name "$AGENT_NAME" \
  --framework langchain \
  --description "Live demo agent created during investor pitch"
echo ""
sleep "$PAUSE"

echo "4. Initialize agent config..."
DEMO_DIR="$(mktemp -d -t ainfera-demo-XXXXXX)"
cd "$DEMO_DIR"
ainfera init \
  --name "$AGENT_NAME" \
  --framework langchain \
  --tier standard \
  --non-interactive \
  --force
echo ""
echo "--- ainfera.yaml ---"
cat ainfera.yaml
echo ""
sleep "$PAUSE"

echo "5. Deploy agent..."
ainfera deploy
echo ""
sleep "$PAUSE"

echo "6. Check trust score..."
ainfera trust score "$AGENT_NAME" || echo "  (trust score pending — new agent)"
echo ""
sleep "$PAUSE"

echo "7. View agents list with new agent..."
ainfera agents list
echo ""

echo "═══════════════════════════════════════"
echo "  Demo complete. Infrastructure ready."
echo "═══════════════════════════════════════"
