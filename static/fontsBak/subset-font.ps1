param($completeFile, $outputFile)
$ocFeatures = "dlig,pcap,c2pc,case,swsh,onum,pnum,smcp"
$latin = "U+0-FF,U+131,U+152,U+153,U+2BB,U+2BC,U+2C6,U+2DA,U+2DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"
$fleuron = "U+2767"
$subset = "$latin,$fleuron"

pyftsubset $completeFile --unicodes=$subset --flavor="woff2" --with-zopfli --output-file="$outputFile.woff2" --layout-features+=$ocFeatures
pyftsubset $completeFile --unicodes=$subset --flavor="woff" --with-zopfli --output-file="$outputFile.woff" --layout-features+=$ocFeatures