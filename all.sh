#/usr/bin/env bash

for i in `ls input/`
do
  ./test.py input/$i
done