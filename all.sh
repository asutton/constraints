#/usr/bin/env bash

for i in `ls input/`
do
  >&2 echo "testing $i"
  ./test.py input/$i
done