#!/bin/bash
<<CLOSURE
Scripts to run Closure compiler over JS files during build.

This function is separated from build.sh so it can be run standalone
without building if needed.

Requires Java installed.
CLOSURE

echo "*** CLOSURE: running closure compiler ***"

CLOSURE="../thirdparty/closure/compiler.jar"

echo "*** CLOSURE: minifying javascript files ***"
let SOURCE_FILE_SIZES=0
let DEST_FILE_SIZES=0

closure () {
  SOURCE_DIR=$1
  for dir in $(find $SOURCE_DIR -type d); do
    for i in $(find $dir/*.js -type f); do
      echo "CLOSURE: Processing $i"
      CURRENT_SOURCE_FILE_SIZE=$(ls -l "$i" | awk '{print $5}')
      let SOURCE_FILE_SIZES=$SOURCE_FILE_SIZES+$CURRENT_SOURCE_FILE_SIZE
      mv $i $i.old.js
      java -jar $CLOSURE --js=$i.old.js > $i
      if [ "$?" == "1" ]; then
        echo "*** ATTENTION ***: $i minimization failed, copying plain file"
        cp $i.old.js $i
      fi
      rm $i.old.js
      CURRENT_DEST_FILE_SIZE=$(ls -l "$i" | awk '{print $5}')
      let DEST_FILE_SIZES=$DEST_FILE_SIZES+$CURRENT_DEST_FILE_SIZE
    done
  done
}

for DEST_DIR in "$@"; do
  closure $DEST_DIR
done

let COMPRESSION_RATE=$DEST_FILE_SIZES*100/$SOURCE_FILE_SIZES
echo "*** CLOSURE: Source file sizes: $SOURCE_FILE_SIZES, Dest file sizes: $DEST_FILE_SIZES"
echo "*** CLOSURE: Congratulations! You achieved $COMPRESSION_RATE% compression rate!"
