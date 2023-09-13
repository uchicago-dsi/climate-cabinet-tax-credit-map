/**
 * A custom hook for managing DeckGL base maps.
 */

import { bind } from "@/lib/utils";
import { proxy } from "valtio";


const baseMapConfig = {
    political: {
        name: "Political Basemap",
        url: "mapbox://styles/mapbox/streets-v12"
    },
    satellite: {
        name: "Satellite Basemap",
        url: "mapbox://styles/mapbox/satellite-streets-v12"
    }
};


class BaseMapStore {
    constructor() {
        this.options = baseMapConfig;
        this.selected = baseMapConfig.political;
    }

    setMap(mapType) {
        if (!Object.keys(baseMapConfig).includes(mapType)) {
            return Error(`Received an invalid basemap option, "${mapType}".`);
        };
        this.selected = baseMapConfig[mapType];
    }
}

const useBaseMapStore = () => {
    return bind(proxy(new BaseMapStore()));
};


export { useBaseMapStore }
