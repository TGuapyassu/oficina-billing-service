#!/usr/bin/env bash
set -euo pipefail
APP_DIR="$(cd "$(dirname "$0")/../infra-k8s/manifests/app" && pwd)"
NAMESPACE="${NAMESPACE:-oficina}"
: "${IMAGE:?IMAGE is required}"
kubectl apply -f "${APP_DIR}/namespace.yaml"
kubectl apply -f "${APP_DIR}/configmap.yaml"
sed "s|oficina-billing-service:latest|${IMAGE}|g" "${APP_DIR}/deployment.yaml" | kubectl apply -f -
kubectl apply -f "${APP_DIR}/service.yaml"
kubectl rollout status deployment/oficina-billing-service -n "${NAMESPACE}" --timeout=180s
