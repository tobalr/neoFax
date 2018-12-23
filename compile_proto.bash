#!/bin/bash
PROTO_SRC=./messages.proto
PROTO_DST=./src/gen/
mkdir -p $PROTO_DST
protoc --proto_path=./ --python_out=$PROTO_DST $PROTO_SRC
