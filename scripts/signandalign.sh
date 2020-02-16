set -x
pwd
#!/bin/bash

if [ $# -lt 1 ];
then
	echo "usage: $0 apkfile"
	exit 0
fi
apkfile=$1

echo "sign the apk ..."
jarsigner -verbose \
		-sigalg SHA1withRSA \
		-digestalg SHA1 \
		-keystore key \
		$apkfile \
		key0

echo "verify the signature just added ..."
jarsigner -verify -verbose -certs $apkfile

exit 0

echo "align the signed APK package ..."
outfn=${apkfile%.*}_signed.apk
if [ -s $outfn ];
then
	echo "remove existing version - $outfn"
	rm -f ${outfn}
fi
zipalign -v 4 $apkfile $outfn

echo "finished signing and aligning successfully."
