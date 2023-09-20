/**
 * A store for basemap
 */
import { proxy } from "valtio";

const baseMapConfig = {
  political: {
    name: "Political Basemap",
    url: "mapbox://styles/mapbox/streets-v12",
  },
  satellite: {
    name: "Satellite Basemap",
    url: "mapbox://styles/mapbox/satellite-streets-v12",
  },
};

const baseMapStore = proxy({
  options: baseMapConfig,
  selected: baseMapConfig.political,
  setMap: (mapType) => {
    if (!Object.keys(baseMapConfig).includes(mapType)) {
      return Error(`Received an invalid basemap option, "${mapType}".`);
    }
    baseMapStore.selected = baseMapConfig[mapType];
  },
});
const useBaseMapStore = () => baseMapStore;
export { baseMapStore, useBaseMapStore };
