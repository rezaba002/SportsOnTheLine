cd D:/Youtube/video02/work
for c in C1 C6 S5 S1 S3 A4 A2 A3 B1 B4 B5 K1 K8 K2; do
  PYTHONIOENCODING=utf-8 python highlight2.py highlights/$c.json > highlights/$c.log 2>&1 && echo "$c ok" || echo "$c FAILED"
done
echo ALLDONE
