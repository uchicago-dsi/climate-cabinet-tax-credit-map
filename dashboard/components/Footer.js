"use client";
import Image from "next/image";

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="text-center">
      <div className="mx-auto w-[250px]">
        <Image
          src="/images/climate-cabinet-education-black.png"
          alt="Description"
          width={424} // width of the original image
          height={276} // height of the original image
        />
      </div>
      <div className="w-full">
        <div className="w-2/3 mx-auto py-5">
          <p>We identify and support local climate leaders</p>
        </div>
      </div>
      <div className="w-full border-b border-ccgray-light"></div>
      <div className="py-5">
        <p>Copyright © {currentYear} Climate Cabinet. All Rights Reserved.</p>
      </div>
    </footer>
  );
}
