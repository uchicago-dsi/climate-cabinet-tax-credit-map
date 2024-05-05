"use client";

/**
 * A tooltip to use for deck.gl map layers.
 */

import { tooltipStore } from "@/hooks/useTooltipStore";
import { useSnapshot } from "valtio";

const Tooltip = () => {
  const ts = useSnapshot(tooltipStore);
  if (!ts.hoverInfo) return null;
  return (
    <div
      className="tooltip"
      style={{ left: ts.hoverInfo.x, top: ts.hoverInfo.y }}
    >
      <p>{ts.hoverInfo.name}</p>
    </div>
  );
};

export default Tooltip;
