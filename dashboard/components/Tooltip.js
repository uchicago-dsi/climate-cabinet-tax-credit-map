/**
 * A tooltip to use for deck.gl map layers.
 */

"use client";

import { tooltipStore } from "@/hooks/useTooltipStore";
import React from "react";
import { useSnapshot } from "valtio";

const Tooltip = () => {
  const ts = useSnapshot(tooltipStore);
  if (!ts.hoverInfo) return null;
  return (
    <div className="tooltip" style={{ left: ts.hoverInfo.x, top: ts.hoverInfo.y }}>
      <p>{ts.hoverInfo.name}</p>
    </div>
  );
}

export default Tooltip;
