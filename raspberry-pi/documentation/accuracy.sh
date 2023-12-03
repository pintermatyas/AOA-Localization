cd /home/pi/Downloads/AOA-Localization/raspberry-pi/measurements
rm accuracy.csv
touch accuracy.csv
echo "accuracy,biggest_difference" 2>&1 | tee accuracy.csv
rm accuracy_total.csv
touch accuracy_total.csv
echo "measurement_name,total_positioning,under_5m,under_2m,under_1m" 2>&1 | tee accuracy_total.csv
folders=($(ls))

for folder in "${folders[@]}"; do
    full_path=$(readlink -f $folder)
    python ../accuracy_analysis.py $full_path
done