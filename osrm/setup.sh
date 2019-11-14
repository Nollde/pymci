#!/usr/bin/env bash

# requests at: http://localhost:5000/route/v1/driving/13.388860,52.517037;13.385983,52.496891?steps=true
# docker run -t -i -p 5000:6000 -v "/Users/dennis/work/projects/geo_bonn/osrm:/data/bicycle" osrm/osrm-backend osrm-routed --algorithm mld /data/bicycle/koeln-regbez-latest.osrm

build_osrm() {
    if [ ! -z "$ZSH_VERSION" ]; then
        local this_file="${(%):-%x}"
    else
        local this_file="${BASH_SOURCE[0]}"
    fi
    local base="$( cd "$( dirname "$this_file" )" && pwd )"

    docker run -v "${base}:/data/$1" osrm/osrm-backend osrm-extract -p /opt/$1.lua /data/$1/koeln-regbez-latest.osm.pbf
    docker run -v "${base}:/data/$1" osrm/osrm-backend osrm-partition /data/$1/koeln-regbez-latest.osrm
    docker run -v "${base}:/data/$1" osrm/osrm-backend osrm-customize /data/$1/koeln-regbez-latest.osrm

    docker run -p $2:5000 -v "${base}:/data/$1" osrm/osrm-backend osrm-routed --algorithm mld /data/$1/koeln-regbez-latest.osrm
}

run_osrm() {
    docker run -p $2:5000 -v "${base}:/data/$1" osrm/osrm-backend osrm-routed --algorithm mld /data/$1/koeln-regbez-latest.osrm
}

# build_osrm car 5000
# build_osrm bicycle 5001
# build_osrm foot 5002

# (run_osrm car 5000 &)
# (run_osrm bicycle 5001 &)
# (run_osrm foot 5002 &)
