import { proxy, useSnapshot } from "valtio";

export const tooltipStore = proxy({ hoverInfo: null });

const setHoverInfo = (hoverInfo) => {
  if (tooltipStore.hoverInfo?.name === hoverInfo?.name) return;
  tooltipStore.hoverInfo = hoverInfo;
};

export const useTooltipStore = () => {
  return useSnapshot(tooltipStore);
};

export const useSetTooltipStore = () => {
  return setHoverInfo;
};
