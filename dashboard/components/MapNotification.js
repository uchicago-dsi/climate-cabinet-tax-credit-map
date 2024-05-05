"use client";

/**
 * A notification popup for a map.
 */

import Spinner from "@/components/Spinner";

function MapNotification({ notificationText }) {
  return (
    <div className="z-10 relative isolate flex flex-row-reverse overflow-hidden bg-gray-50 px-6 py-2.5 sm:px-3.5 sm:before:flex-1">
      <div className="flex flex-wrap place-items-start gap-x-4 gap-y-2">
        <Spinner />
        <p className="text-sm leading-6 text-gray-900">
          <strong className="font-semibold">{notificationText}</strong>
        </p>
      </div>
      <div
        className="absolute left-[max(-7rem,calc(50%-52rem))] top-1/2 -z-10 -translate-y-1/2 transform-gpu blur-2xl"
        aria-hidden="true"
      >
        <div className="aspect-[577/310] w-[36.0625rem] bg-gradient-to-r from-[#ff80b5] to-[#9089fc] opacity-30"></div>
      </div>
      <div
        className="absolute left-[max(45rem,calc(50%+8rem))] top-1/2 -z-10 -translate-y-1/2 transform-gpu blur-2xl"
        aria-hidden="true"
      >
        <div className="aspect-[577/310] w-[36.0625rem] bg-gradient-to-r from-[#ff80b5] to-[#9089fc] opacity-30"></div>
      </div>
    </div>
  );
}

export default MapNotification;
