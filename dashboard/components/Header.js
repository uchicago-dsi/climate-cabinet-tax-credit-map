"use client";
import Image from "next/image";

export default function Header() {
  return (
    <div className="flex flex-row">
      <div className="w-[200px]">
        <Image
          src="/images/climate-cabinet-logo.png"
          alt="Description"
          width={424} // width of the original image
          height={276} // height of the original image
        />
      </div>
      <div className="flex flex-1 items-center justify-end">
        <nav>
          <ul className="flex space-x-10">
            <li>Home</li>
            <li>About</li>
            <li>Case Studies</li>
            <li>Map</li>
          </ul>
        </nav>
      </div>
    </div>
  );
}
