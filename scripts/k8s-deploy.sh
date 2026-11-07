#!/usr/bin/env bash
set -euo pipefail
K8S_DIR="$(cd "$(dirname "$0")/../k8s" && pwd)"
NAMESPACE="${NAMESPACE:-oficina}"
: "${IMAGE:?IMAGE is required}"
kubectl apply -f "${K8S_DIR}/namespace.yaml"
kubectl apply -f "${K8S_DIR}/configmap.yaml"
sed "s|oficina-billing-service:latest|${IMAGE}|g" "${K8S_DIR}/deployment.yaml" | kubectl apply -f -
kubectl apply -f "${K8S_DIR}/service.yaml"
kubectl rollout status deployment/oficina-billing-service -n "${NAMESPACE}" --timeout=180s
