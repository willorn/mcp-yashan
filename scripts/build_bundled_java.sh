#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
JAVA_HOME_DIR="${JAVA_HOME:-/Users/tianyi/Library/Java/JavaVirtualMachines/graalvm-jdk-21.0.7/Contents/Home}"
BUILD_DIR="$ROOT_DIR/build/java-helper"
CLASSES_DIR="$BUILD_DIR/classes"
RUNTIME_DIR="$ROOT_DIR/runtime"
HELPER_JAR="$RUNTIME_DIR/java/yashan-mcp-helper.jar"
JDBC_JAR="$ROOT_DIR/yashandb-jdbc-1.9.3.jar"

mkdir -p "$CLASSES_DIR" "$RUNTIME_DIR/java"
rm -rf "$CLASSES_DIR"/*

"$JAVA_HOME_DIR/bin/javac" \
  -encoding UTF-8 \
  -d "$CLASSES_DIR" \
  "$ROOT_DIR/java-src/io/yashan/mcp/SqlExecutorMain.java"

"$JAVA_HOME_DIR/bin/jar" \
  --create \
  --file "$HELPER_JAR" \
  -C "$CLASSES_DIR" .

rm -rf "$RUNTIME_DIR/jre"
"$JAVA_HOME_DIR/bin/jlink" \
  --add-modules java.base,java.management,java.naming,java.sql \
  --output "$RUNTIME_DIR/jre" \
  --strip-debug \
  --no-man-pages \
  --no-header-files \
  --compress=zip-6

echo "Built helper jar: $HELPER_JAR"
echo "Built bundled runtime: $RUNTIME_DIR/jre"
echo "JDBC jar kept at: $JDBC_JAR"
