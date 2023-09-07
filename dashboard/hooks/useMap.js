/**
 * A custom hook to manage map data layers, basemaps, and viewport settings.
 */

"server only"

import bbox from "@turf/bbox";
import { proxy } from "valtio";
import { derive } from "valtio/utils";
import { WebMercatorViewport } from "@deck.gl/core";
import { GeoJsonLayer } from "@deck.gl/layers";



function useMap(geographies) {

    // Configure data state
    const dataState = proxy({
        geographies: geographies ?? [],
        setGeographies: (geos) => dataState.geographies = geos,
    });

    derive(
        {
            selectedGeography: (get) => {
                let allGeos = get(dataState).geographies;
                return allGeos?.find(g => g.properties.is_target === 1) ?? null;
            }
        },
        {
            proxy: dataState
        }
    );

    // Configure viewport state
    const viewportState = proxy({
        current: {
            width: 500,
            height: 500,
            longitude: -119.272009,
            latitude: 37.421476393980676,
            zoom: 5,
            pitch: 0,
            bearing: 0,
            // padding: 30
        },
        setViewport: (view) => viewportState.current = view
    });

    // derive(
    //     {
    //         zoomToGeography: (get) => {
    //             // Abort if geography is null
    //             const geography = get(dataState.selectedGeography);
    //             if (!geography) {
    //                 return;
    //             }

    //             // Fetch viewport state
    //             let webMercatorState = get(viewportState).current;

    //             // Define coordinates of geometry bounding box
    //             const boundingBox = bbox({
    //                 type: "Feature",
    //                 geometry: geography.boundary
    //             });
    //             const boundingBoxCoords = [
    //                 [boundingBox[0], boundingBox[1]],
    //                 [boundingBox[2], boundingBox[3]],
    //             ];
        
    //             // Create viewport and fit to new bounding box
    //             const fittedViewport = new WebMercatorViewport(
    //                 ...webMercatorState
    //             );
    //             const currentLatLonZoom = fittedViewport.fitBounds(
    //                 boundingBoxCoords
    //             );
        
    //             // Update map configuration
    //             setViewport({
    //                 width: webMercatorState.width,
    //                 height: webMercatorState.height,
    //                 longitude: currentLatLonZoom.longitude,
    //                 latitude: currentLatLonZoom.latitude,
    //                 zoom: currentLatLonZoom.zoom,
    //                 pitch: webMercatorState.pitch,
    //                 bearing: webMercatorState.bearing,
    //                 padding: webMercatorState.padding
    //             });
    //         }
    //     },
    //     {
    //         proxy: viewportState,
    //     }
    // );


    // Configure base map state
    const baseMapConfig = {
        political: {
            name: "Political Basemap",
            url: "mapbox://styles/mapbox/streets-v12"
        },
        satellite: {
            name: "Satellite Basemap",
            url: "mapbox://styles/mapbox/satellite-v9"
        }
    };

    const baseMapState = proxy({
        options: baseMapConfig,
        selected: baseMapConfig.political,
        setBasemap: (mapType) => {
            if (!Object.keys(baseMapConfig).includes(mapType)) {
                return Error(`Received an invalid basemap option, "${mapType}".`);
            };
            console.log("good with basemap")
            baseMapState.selected = baseMapConfig[mapType];
        }
    });

    // Configure layer state
    const layerConfig = {
        lowIncomeTracts: {
            key: "low_income",
            name: "Low Income Census Tracts",
            fillColor: [0, 255, 255, 255],
            opacity: 0.5
        },
        justice40Communities: {
            key: "justice40",
            name: "Justice 40 Communities",
            fillColor: [255, 51, 51, 255],
            opacity: 0.5
        },
        distressedCommunities: {
            key: "dci",
            name: "Distressed Communities",
            fillColor: [153, 0, 153, 255],
            opacity: 0.5
        },
        energyCommunities: {
            key: "energy",
            name: "Energy Communities",
            fillColor: [0, 153, 0, 255],
            opacity: 0.5
        },
        municipalUtilities: {
            key: "municipal_util",
            name: "Municipal Utilities",
            fillColor: [255, 255, 100, 255],
            opacity: 0.5
        },
        ruralCoops: {
            key: "rural_coop",
            name: "Rural Co-Ops",
            fillColor: [255, 255, 100, 255],
            opacity: 0.5
        },
        counties: {
            key: "county",
            name: "Counties",
            fillColor: [0, 0, 0, 255],
            opacity: 0.2
        },
        states: {
            key: "state",
            name: "States",
            fillColor: [0, 0, 0, 255],
            opacity: 0.2
        }
    };

    const layerState = proxy({
        toggleOptions: [
            layerConfig.lowIncomeTracts.name,
            layerConfig.distressedCommunities.name,
            layerConfig.energyCommunities.name,
            layerConfig.justice40Communities.name,
            layerConfig.counties.name
        ],
        toggled: []
    })

    derive(
        {
            all: (get) => {
                // Exit if no geographies displayed
                const geographies = get(dataState).geographies;
                console.log(get(dataState).geographies);
                if (!geographies || geographies.length === 0) return []

                // Group datasets by geography type
                const geoDatasets = (get(dataState)
                    .geographies
                    .reduce((grp, geo) => {
                        let key = geo.properties.geography_type;
                        if (["energy_ffe", "energy_coal"].includes(key)) {
                            key = "energy";
                        };
                        grp[key] = grp[key] ?? [];
                        grp[key].push(geo);
                        return grp;
                    }, {}));

                
                // Map datasets to GeoJSON layers
                let layers = [];
                Object.entries(geoDatasets).forEach(([key, dataset], _) => {
                    let config = (Object
                        .entries(layerConfig)
                        .filter(([_, config]) => config.key === key));
    
                    layers.push(new GeoJsonLayer({
                        id: config.name,
                        data: dataset,
                        opacity: config.opacity,
                        stroked: false,
                        filled: true,
                        extruded: false,
                        wireframe: true,
                        getFillColor: config.fillColor,
                        getLineColor: [255, 255, 255],
                        pickable: true
                    }));
                });
            
                let l = layers;
                console.log(l);
                return l;
            },
            toggleable: (get) => {
                const ls = get(layerState);
                console.log("toggable")
                return ls.all?.filter(layer => state.toggleOptions.includes(layer));
            },
            targetGeos: (get) => {
                const ls = get(layerState);
                const validNames = [
                    layerConfig.municipalUtilities.name,
                    layerConfig.ruralCoops.name,
                    layerConfig.states.name
                ];
                console.log("target geos")
                return ls.all?.filter(layer => validNames.includes(layer));
            },
        },
        {
            proxy: layerState
        }
    )


    // Compose final state object
    const combinedState = proxy({
        basemap: baseMapState,
        viewport: viewportState,
        layers: layerState,
        data: dataState
    });

    console.log(combinedState);

    return [combinedState];
};

export { useMap };

// // Create hook for updating map focus
// useEffect(() => {
//     const handleResize = () => {
//         if (mapContainerRef.current) {
//             const width = mapContainerRef.current.getBoundingClientRect().width;
//             const height = mapContainerRef.current.getBoundingClientRect().height;
//             setMapConfig({
//                 ...mapConfig,
//                 containerWidth: width,
//                 containerHeight: height
//             })
//         }
//     };
//     setTimeout(handleResize, 200);  // TODO: this timeout is weird and I probably shouldn't have to actually do this
//     window.addEventListener("resize", handleResize);
//     return () => window.removeEventListener("resize", handleResize);
// }, []);