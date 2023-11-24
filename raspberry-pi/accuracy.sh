cd /home/pi/Downloads/AOA-Localization/raspberry-pi/measurements
folders=($(ls))

for folder in "${folders[@]}"; do
    full_path=$(readlink -f $folder)
    python ../accuracy_analysis.py $full_path
done