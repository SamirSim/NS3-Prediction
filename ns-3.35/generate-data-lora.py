from math import dist
import os
import subprocess
import sys
import csv

output_file = "lora-data-1.csv"

nED_list = [100, 500, 1000]
period_list = [300, 600, 900]
size_list = [20, 50]
distance_list = [100, 5000, 10000]
nGW_list = [1]
environment_list = ["rural", "urban", "indoor"]

SF_list = [7, 10, 12]
traffic_type_list = ["Unconfirmed", "Confirmed"]
coding_rate_list = [1, 4]
bandwidth_list = [125]
CRC_list = [1]

battery_capacity = 2300
battery_voltage = 3

for nED in nED_list:
    for period in period_list:
        for size in size_list:
            for distance in distance_list:
                for nGW in nGW_list:
                    for environment in environment_list:
                        for sf in SF_list:
                            for traffic_type in traffic_type_list:
                                for coding_rate in coding_rate_list:
                                    for bandwidth in bandwidth_list:
                                        for crc in CRC_list:
                                            simulation_time = 10 * period # 10 packets are sent                                       
                                            
                                            os.environ['SF'] = str(sf)
                                            os.environ['CODINGRATE'] = str(coding_rate)
                                            os.environ['CRC'] = str(crc)
                                            os.environ['TRAFFIC'] = str(traffic_type)
                                            os.environ['NGW'] = str(nGW)
                                            os.environ['NBDEVICES'] = str(nED)

                                            os.environ['DISTANCE'] = str(distance)
                                            os.environ['PACKETSIZE'] = str(size)
                                            os.environ['PERIOD'] = str(period)
                                            os.environ['RADIOENVIRONMENT'] = str(environment)

                                            os.environ['SIMULATION_TIME'] = str(simulation_time)
                                            os.environ['BATTERY_CAPACITY'] = str(battery_capacity)
                                            os.environ['BATTERY_VOLTAGE'] = str(battery_voltage)

                                            os.environ['LOGFILE'] = "log-"+str(sf)+"-"+str(coding_rate)+"-"+str(traffic_type)+"-"+str(environment)+"-"+str(distance)+"-"+str(size)+"-"+str(nED)+"-"+str(period)+".txt"
                                            os.environ['LOGFILEPARSED'] = "log-parsed-"+str(sf)+"-"+str(coding_rate)+"-"+str(traffic_type)+"-"+str(environment)+"-"+str(distance)+"-"+str(size)+"-"+str(nED)+"-"+str(period)+".txt"

                                            output = subprocess.check_output('./waf --run "scratch/lora-periodic.cc --radioEnvironment=$RADIOENVIRONMENT --nGateways=$NGW --trafficType=$TRAFFIC --SF=$SF --codingRate=$CODINGRATE --crc=$CRC --distance=$DISTANCE --simulationTime=$SIMULATION_TIME --nSta=$NBDEVICES --payloadSize=$PACKETSIZE --period=$PERIOD" 2> $LOGFILE', shell=True, text=True,stderr=subprocess.DEVNULL)
                                            output = output + "Energy consumption: " + subprocess.check_output("cat $LOGFILE | grep -e 'LoraRadioEnergyModel:Total energy consumption' | tail -1 | awk 'NF>1{print $NF}' | sed 's/J//g'", shell=True, text=True,stderr=subprocess.DEVNULL)
                                            latency_ = subprocess.check_output(' cat $LOGFILE | grep -e "Total time" > $LOGFILEPARSED; python3 lora-scripts/get_latencies.py $LOGFILEPARSED', shell=True, text=True,stderr=subprocess.DEVNULL)

                                            subprocess.check_output('rm $LOGFILE; rm $LOGFILEPARSED', shell=True, text=True,stderr=subprocess.DEVNULL)
                                            
                                            lines = output.splitlines()
                                            line = lines[0]
                                            i = 0
                                            while "Success" not in line:
                                                i = i + 1
                                                line = lines[i]
                                            success_rate = round(float(lines[i].split()[-1]), 2)
                                            energy = float(lines[i+2].split()[-1]) / simulation_time # Watts

                                            if traffic_type == "Unconfirmed":
                                                traffic_type = 0
                                            else:
                                                traffic_type = 1

                                            if environment == "rural":
                                                environment_id = 1
                                            elif environment == "urban":
                                                environment_id = 2
                                            elif environment == "suburban":
                                                environment_id = 3
                                            elif environment == "indoor":
                                                environment_id = 4

                                            with open(output_file, 'a', newline='') as file:
                                                writer = csv.writer(file)
                                                writer.writerow([nED, period, size, distance, nGW, environment_id, sf, traffic_type, coding_rate, bandwidth, crc, success_rate, energy])

