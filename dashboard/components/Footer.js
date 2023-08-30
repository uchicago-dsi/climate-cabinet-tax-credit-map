"use client";
import Image from "next/image";

export default function Footer() {
  return (
    <div className="text-center">
      <div className="mx-auto w-[250px]">
        <Image
          src="/images/climate-cabinet-logo-black.png"
          alt="Description"
          width={424} // width of the original image
          height={276} // height of the original image
        />
      </div>
      <p className=" w-2/3 mx-auto py-5">
        Paid Pol. Adv. paid for with regulated funds by Climate Cabinet PAC,
        independently of and not authorized or approved by any federal, state,
        or local candidate, candidate’s agent, or committee.
      </p>
    </div>
  );
}
