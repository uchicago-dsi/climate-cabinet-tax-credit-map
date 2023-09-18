/**
 * A tooltip to use for deck.gl map layers.
 */

"use client";

import React from "react";

const Tooltip = React.memo(({ hoverInfo }) => {
  return (
    <div className="tooltip" style={{ left: hoverInfo.x, top: hoverInfo.y }}>
      <p>{hoverInfo.name}</p>
    </div>
  );
});

export default Tooltip;
