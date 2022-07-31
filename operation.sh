i="$(cat servers.conf)"
echo $i
if [ $i > 3 ]
then
  j=$(($i-3))
  echo $j
elif [ $((i)) == 3 ]
then
  echo "Stable"
else
  k = $((3-$i))
  echo $k
fi