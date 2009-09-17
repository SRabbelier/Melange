#!/bin/bash
#Requires java installed

echo "*** SHRINKSAFE: running shrinksafe ***"

SHRINKSAFE="../thirdparty/shrinksafe/shrinksafe.jar"

echo "*** SHRINKSAFE: minifying javascript files ***"
let SOURCE_FILE_SIZES=0
let DEST_FILE_SIZES=0

shrinksafe () {
  SOURCE_DIR=$1
  for dir in $(find $SOURCE_DIR -type d); do
    for i in $(find $dir/*.js -type f); do
      echo "SHRINKSAFE: Processing $i"
      CURRENT_SOURCE_FILE_SIZE=$(ls -l "$i" | awk '{print $5}')
      let SOURCE_FILE_SIZES=$SOURCE_FILE_SIZES+$CURRENT_SOURCE_FILE_SIZE
      mv $i $i.old.js
      java -jar $SHRINKSAFE $i.old.js > $i
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
  shrinksafe $DEST_DIR
done

let COMPRESSION_RATE=$DEST_FILE_SIZES*100/$SOURCE_FILE_SIZES
echo "*** SHRINKSAFE: Source file sizes: $SOURCE_FILE_SIZES, Dest file sizes: $DEST_FILE_SIZES"
echo "*** SHRINKSAFE: Congratulations! You achieved $COMPRESSION_RATE% compression rate!"
