declare -a simulationTime=3600 # Seconds
declare -a payloadSize=23 # Bytes
declare -a period=1000 # Seconds
declare -a nSta=2 # Number of end-devices
declare -a distance=100 # Meters from ED to GW
declare -a nGW=2 # Number of gateways
declare -a environment="Urban" # Radio environment

declare -a SF=7 # Spreading Factor
declare -a type="Unconfirmed" # Type of traffic
declare -a codingRate=1 # Coding rate
declare -a bandwidth=125 # Bandwidth in KHz

declare -a step=2000

path="telemetry-final"
mkdir -p "$path"

for SF in 7
do
    for type in "Unconfirmed"
    do
        for codingRate in 1
        do
            for bandwidth in 125
            do
                for distance in 100 1000 2000 3000
                do
                    for payloadSize in 20 40
                    do
                        for period in 300 400 500 600 700 800 900 1000
                        do
                            for environment in "Rural"
                            do
                                for nSta in 100 120 140 160 180 200
                                do 
                                    for nGW in 1
                                    do
                                        ./waf --run "scratch/lora-periodic.cc --simulationTime=$simulationTime --payloadSize=$payloadSize --period=$period --nSta=$nSta --distance=$distance --energyRatio=$energyRatio --successRate=$successRate --batteryLife=$batteryLife" 2> "${path}/$nSta-$period-$distance-$payloadSize-log.txt" > "${path}/$nSta-$period-$distance-$payloadSize-out.txt"
                                        
                                        if [[ $successRate -eq 1 ]]
                                        then
                                            mkdir -p "$path/success-rate"
                                            python3 get_loss.py "${path}/$nSta-$period-$distance-$payloadSize-out.txt" "${path}/success-rate/$period-$distance-$payloadSize.csv" $nSta
                                        fi 

                                        if [[ $energyRatio -eq 1 ]]
                                        then
                                            mkdir -p "$path/energy"
                                            energyJoules=$(cat "${path}/$nSta-$period-$distance-$payloadSize-log.txt" | grep -e "LoraRadioEnergyModel:Total energy consumption" | tail -1 | awk 'NF>1{print $NF}' | sed 's/J//g')
                                            nbPackets=$(cat "${path}/$nSta-$period-$distance-$payloadSize-out.txt" | tail -1 | awk '{print $2;}')
                                            nbBytes=$(bc <<< "($nbPackets/$nSta)*($payloadSize+9)")
                                            energyJoulesPerByte=$(bc <<< "scale=10;$energyJoules/$nbBytes" | awk '{printf "%f", $0}') # Joules/Byte
                                            #echo $nSta $energyJoulesPerByte >> "${path}/energy/$period-$distance-$payloadSize-ratio.csv" 
                                            echo $nSta $energyJoules $nbBytes $energyJoulesPerByte
                                        fi     
                                        #cat "${path}/$nSta-$period-$distance-$payloadSize-out.txt"
                                        rm "${path}/$nSta-$period-$distance-$payloadSize-out.txt" "${path}/$nSta-$period-$distance-$payloadSize-log.txt"
                                    done
                                done
                            done
                        done
                    done
                done
            done
        done
    done
done